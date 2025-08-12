# -*- coding: utf-8 -*-
"""
MLStrategy - Machine Learning Based Trading Strategy
Usa scikit-learn para predições baseadas em features técnicas
"""
import logging
import os
import pickle
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import talib.abstract as ta

from freqtrade.strategy import (CategoricalParameter, DecimalParameter,
                                IntParameter, IStrategy)

# ML imports
try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.metrics import accuracy_score
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    logging.warning("⚠️ scikit-learn não disponível. Usando fallback para indicadores técnicos.")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLStrategy(IStrategy):
    """
    Estratégia baseada em Machine Learning

    Features utilizadas:
    - RSI, MACD, Bollinger Bands
    - Volume patterns
    - Price momentum
    - Volatility measures
    """

    INTERFACE_VERSION = 3

    # Configurações básicas
    timeframe = '5m'
    stoploss = -0.08
    minimal_roi = {
        "0": 0.05,
        "10": 0.03,
        "20": 0.02,
        "30": 0.01,
        "60": 0.005
    }

    # Trailing stop
    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.03
    trailing_only_offset_is_reached = True

    # Parâmetros otimizáveis
    ml_lookback = IntParameter(50, 200, default=100, space='buy')
    ml_threshold = DecimalParameter(0.6, 0.9, default=0.75, space='buy')
    retrain_interval = IntParameter(100, 500, default=200, space='buy')

    # Proteções
    cooldown_lookback = IntParameter(2, 48, default=10, space="protection")
    stop_duration = IntParameter(12, 200, default=20, space="protection")
    use_stop_protection = CategoricalParameter([True, False], default=True, space="protection")

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = Path("user_data/ml_models")
        self.model_path.mkdir(exist_ok=True)
        self.last_train_candle = 0
        self.feature_columns = []

        if not ML_AVAILABLE:
            logger.warning("🚨 ML não disponível - usando estratégia técnica como fallback")

    def get_int_value(self, param):
        """Helper para converter parâmetros para int"""
        return int(param.value)

    @property
    def protections(self):
        if not self.use_stop_protection.value:
            return []
        return [
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": self.get_int_value(self.stop_duration)
            },
            {
                "method": "StoplossGuard",
                "lookback_period_candles": self.get_int_value(self.cooldown_lookback),
                "trade_limit": 3,
                "stop_duration_candles": self.get_int_value(self.stop_duration),
                "only_per_pair": False
            }
        ]

    def create_features(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Criar features para o modelo ML
        """
        # Indicadores técnicos básicos
        dataframe['rsi'] = ta.RSI(dataframe['close'], timeperiod=14)
        dataframe['rsi_fast'] = ta.RSI(dataframe['close'], timeperiod=7)
        dataframe['rsi_slow'] = ta.RSI(dataframe['close'], timeperiod=21)

        # MACD
        macd = ta.MACD(dataframe['close'])
        dataframe['macd'] = macd['macd']
        dataframe['macd_signal'] = macd['macdsignal']
        dataframe['macd_hist'] = macd['macdhist']

        # Bollinger Bands
        bb = ta.BBANDS(dataframe['close'])
        dataframe['bb_upper'] = bb['upperband']
        dataframe['bb_middle'] = bb['middleband']
        dataframe['bb_lower'] = bb['lowerband']
        dataframe['bb_percent'] = (dataframe['close'] - dataframe['bb_lower']) / (dataframe['bb_upper'] - dataframe['bb_lower'])
        dataframe['bb_width'] = (dataframe['bb_upper'] - dataframe['bb_lower']) / dataframe['bb_middle']

        # EMAs
        dataframe['ema_8'] = ta.EMA(dataframe['close'], timeperiod=8)
        dataframe['ema_21'] = ta.EMA(dataframe['close'], timeperiod=21)
        dataframe['ema_50'] = ta.EMA(dataframe['close'], timeperiod=50)

        # Price momentum
        dataframe['price_change_1'] = dataframe['close'].pct_change(1)
        dataframe['price_change_5'] = dataframe['close'].pct_change(5)
        dataframe['price_change_10'] = dataframe['close'].pct_change(10)

        # Volume features
        dataframe['volume_sma'] = dataframe['volume'].rolling(20).mean()
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_sma']
        dataframe['volume_change'] = dataframe['volume'].pct_change(1)

        # Volatility
        dataframe['atr'] = ta.ATR(dataframe['high'], dataframe['low'], dataframe['close'], timeperiod=14)
        dataframe['volatility'] = dataframe['close'].rolling(20).std()

        # Trend strength
        dataframe['adx'] = ta.ADX(dataframe['high'], dataframe['low'], dataframe['close'], timeperiod=14)

        # Support/Resistance levels
        dataframe['high_20'] = dataframe['high'].rolling(20).max()
        dataframe['low_20'] = dataframe['low'].rolling(20).min()
        dataframe['close_to_high'] = (dataframe['close'] - dataframe['low_20']) / (dataframe['high_20'] - dataframe['low_20'])

        return dataframe

    def create_target(self, dataframe: pd.DataFrame, lookahead: int = 5) -> pd.Series:
        """
        Criar target para treinamento (1 = buy signal, 0 = no signal)
        """
        # Target: preço sobe mais de 1% nos próximos 5 candles
        future_max = dataframe['high'].rolling(window=lookahead, min_periods=1).max().shift(-lookahead)
        target = (future_max / dataframe['close'] - 1) > 0.01
        return target.astype(int)

    def prepare_ml_data(self, dataframe: pd.DataFrame):
        """
        Preparar dados para ML
        """
        # Features para ML
        feature_cols = [
            'rsi', 'rsi_fast', 'rsi_slow',
            'macd', 'macd_signal', 'macd_hist',
            'bb_percent', 'bb_width',
            'price_change_1', 'price_change_5', 'price_change_10',
            'volume_ratio', 'volume_change',
            'atr', 'volatility', 'adx',
            'close_to_high'
        ]

        # Filtrar apenas colunas que existem
        available_cols = [col for col in feature_cols if col in dataframe.columns]
        self.feature_columns = available_cols

        # Preparar features
        X = dataframe[available_cols].copy()

        # Remover NaN
        X = X.fillna(method='ffill').fillna(0)

        return X

    def train_model(self, dataframe: pd.DataFrame):
        """
        Treinar modelo ML
        """
        if not ML_AVAILABLE:
            return False

        try:
            logger.info("🤖 Treinando modelo ML...")

            # Preparar dados
            X = self.prepare_ml_data(dataframe)
            y = self.create_target(dataframe)

            # Remover últimas linhas (sem target)
            valid_idx = ~y.isna()
            X = X[valid_idx]
            y = y[valid_idx]

            if len(X) < 100:
                logger.warning("⚠️ Dados insuficientes para treinamento ML")
                return False

            # Split train/test
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )

            # Normalizar features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)

            # Treinar modelo
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )

            self.model.fit(X_train_scaled, y_train)

            # Avaliar modelo
            y_pred = self.model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)

            logger.info(f"✅ Modelo treinado - Acurácia: {accuracy:.3f}")

            # Salvar modelo
            model_file = self.model_path / "ml_model.pkl"
            with open(model_file, 'wb') as f:
                pickle.dump({
                    'model': self.model,
                    'scaler': self.scaler,
                    'features': self.feature_columns,
                    'accuracy': accuracy
                }, f)

            return True

        except Exception as e:
            logger.error(f"❌ Erro no treinamento ML: {e}")
            return False

    def load_model(self):
        """
        Carregar modelo salvo
        """
        model_file = self.model_path / "ml_model.pkl"
        if model_file.exists():
            try:
                with open(model_file, 'rb') as f:
                    data = pickle.load(f)
                    self.model = data['model']
                    self.scaler = data['scaler']
                    self.feature_columns = data['features']
                logger.info("✅ Modelo ML carregado")
                return True
            except Exception as e:
                logger.error(f"❌ Erro ao carregar modelo: {e}")
        return False

    def get_ml_prediction(self, dataframe: pd.DataFrame) -> pd.Series:
        """
        Obter predições do modelo ML
        """
        if not ML_AVAILABLE or self.model is None:
            return pd.Series(0, index=dataframe.index)

        try:
            X = self.prepare_ml_data(dataframe)
            X_scaled = self.scaler.transform(X)

            # Predições de probabilidade
            probabilities = self.model.predict_proba(X_scaled)[:, 1]  # Probabilidade da classe 1

            return pd.Series(probabilities, index=dataframe.index)

        except Exception as e:
            logger.error(f"❌ Erro na predição ML: {e}")
            return pd.Series(0, index=dataframe.index)

    def populate_indicators(self, dataframe, metadata):
        """
        Calcular indicadores e treinar modelo se necessário
        """
        # Criar features
        dataframe = self.create_features(dataframe)

        # Verificar se precisa treinar/retreinar modelo
        current_candle = len(dataframe)
        retrain_interval = self.get_int_value(self.retrain_interval)

        if (self.model is None and not self.load_model()) or \
           (current_candle - self.last_train_candle > retrain_interval):

            if self.train_model(dataframe):
                self.last_train_candle = current_candle

        # Obter predições ML
        if ML_AVAILABLE and self.model is not None:
            dataframe['ml_prediction'] = self.get_ml_prediction(dataframe)
        else:
            # Fallback: usar RSI como "predição"
            dataframe['ml_prediction'] = (100 - dataframe['rsi']) / 100

        return dataframe

    def populate_entry_trend(self, dataframe, metadata):
        """
        Sinais de entrada baseados em ML + confirmação técnica
        """
        ml_threshold = self.ml_threshold.value

        if ML_AVAILABLE and self.model is not None:
            # Condições ML
            ml_signal = dataframe['ml_prediction'] > ml_threshold

            # Confirmação técnica
            technical_confirm = (
                (dataframe['rsi'] < 70) &
                (dataframe['bb_percent'] < 0.8) &
                (dataframe['volume_ratio'] > 0.8) &
                (dataframe['adx'] > 20)
            )

            entry_signal = ml_signal & technical_confirm

        else:
            # Fallback: estratégia técnica tradicional
            entry_signal = (
                (dataframe['rsi'] < 30) &
                (dataframe['bb_percent'] < 0.2) &
                (dataframe['macd'] > dataframe['macd_signal']) &
                (dataframe['volume_ratio'] > 1.2)
            )

        dataframe.loc[entry_signal, 'enter_long'] = 1
        dataframe.loc[entry_signal, 'enter_tag'] = 'ML_signal' if ML_AVAILABLE else 'technical_fallback'

        return dataframe

    def populate_exit_trend(self, dataframe, metadata):
        """
        Sinais de saída
        """
        if ML_AVAILABLE and self.model is not None:
            # Saída quando ML prediction fica baixa
            exit_signal = (
                (dataframe['ml_prediction'] < 0.3) |
                (dataframe['rsi'] > 80) |
                (dataframe['bb_percent'] > 0.95)
            )
        else:
            # Fallback técnico
            exit_signal = (
                (dataframe['rsi'] > 70) |
                (dataframe['bb_percent'] > 0.8) |
                (dataframe['macd'] < dataframe['macd_signal'])
            )

        dataframe.loc[exit_signal, 'exit_long'] = 1

        return dataframe
