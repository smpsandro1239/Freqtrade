# -*- coding: utf-8 -*-
"""
MultiTimeframeStrategy - Análise Multi-Timeframe
Analisa 1m, 5m, 15m, 1h simultaneamente para confirmação de sinais
"""
import logging
from datetime import datetime

import numpy as np
import pandas as pd

from freqtrade.strategy import (CategoricalParameter, DecimalParameter,
                                IntParameter, IStrategy, informative)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiTimeframeStrategy(IStrategy):
    """
    Estratégia Multi-Timeframe

    Timeframes analisados:
    - 1m: Entrada precisa
    - 5m: Confirmação de momentum
    - 15m: Tendência de médio prazo
    - 1h: Tendência de longo prazo

    Lógica:
    - Tendência 1h deve ser bullish
    - Confirmação 15m deve estar alinhada
    - Momentum 5m deve ser favorável
    - Entrada precisa no 1m
    """

    INTERFACE_VERSION = 3

    # Configurações básicas
    timeframe = '1m'  # Timeframe principal para entrada
    stoploss = -0.06
    minimal_roi = {
        "0": 0.06,
        "5": 0.04,
        "10": 0.03,
        "15": 0.02,
        "30": 0.01,
        "60": 0.005
    }

    # Trailing stop
    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.025
    trailing_only_offset_is_reached = True

    # Parâmetros otimizáveis
    rsi_oversold = IntParameter(20, 35, default=30, space='buy')
    rsi_overbought = IntParameter(65, 80, default=70, space='sell')

    # Parâmetros de confirmação multi-timeframe
    trend_strength_threshold = DecimalParameter(0.5, 0.9, default=0.7, space='buy')
    volume_threshold = DecimalParameter(1.0, 2.0, default=1.5, space='buy')

    # Proteções
    cooldown_lookback = IntParameter(2, 48, default=15, space="protection")
    stop_duration = IntParameter(12, 200, default=30, space="protection")
    use_stop_protection = CategoricalParameter([True, False], default=True, space="protection")

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
                "trade_limit": 2,
                "stop_duration_candles": self.get_int_value(self.stop_duration),
                "only_per_pair": False
            }
        ]

    def rsi(self, series: pd.Series, period: int = 14) -> pd.Series:
        """Implementação nativa do RSI"""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def ema(self, series: pd.Series, period: int) -> pd.Series:
        """Implementação nativa da EMA"""
        return series.ewm(span=period).mean()

    def sma(self, series: pd.Series, period: int) -> pd.Series:
        """Implementação nativa da SMA"""
        return series.rolling(window=period).mean()

    def atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14):
        """Implementação nativa do ATR"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()

    def calculate_trend_strength(self, dataframe: pd.DataFrame) -> pd.Series:
        """
        Calcular força da tendência baseada em múltiplos indicadores
        Retorna valor entre 0 (bearish) e 1 (bullish)
        """
        # EMA alignment
        ema_8 = self.ema(dataframe['close'], 8)
        ema_21 = self.ema(dataframe['close'], 21)
        ema_50 = self.ema(dataframe['close'], 50)

        ema_alignment = (
            (ema_8 > ema_21).astype(int) * 0.4 +
            (ema_21 > ema_50).astype(int) * 0.3 +
            (dataframe['close'] > ema_8).astype(int) * 0.3
        )

        # RSI momentum
        rsi = self.rsi(dataframe['close'])
        rsi_momentum = ((rsi - 50) / 50).clip(-1, 1) * 0.5 + 0.5

        # Price momentum
        price_change_5 = dataframe['close'].pct_change(5)
        price_momentum = (price_change_5 > 0).astype(int)

        # Combine all factors
        trend_strength = (
            ema_alignment * 0.5 +
            rsi_momentum * 0.3 +
            price_momentum * 0.2
        )

        return trend_strength.clip(0, 1)

    @informative('5m')
    def populate_indicators_5m(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """Indicadores para timeframe 5m"""
        dataframe['rsi'] = self.rsi(dataframe['close'])
        dataframe['ema_8'] = self.ema(dataframe['close'], 8)
        dataframe['ema_21'] = self.ema(dataframe['close'], 21)
        dataframe['ema_50'] = self.ema(dataframe['close'], 50)
        dataframe['volume_sma'] = self.sma(dataframe['volume'], 20)
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_sma']
        dataframe['trend_strength'] = self.calculate_trend_strength(dataframe)

        return dataframe

    @informative('15m')
    def populate_indicators_15m(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """Indicadores para timeframe 15m"""
        dataframe['rsi'] = self.rsi(dataframe['close'])
        dataframe['ema_8'] = self.ema(dataframe['close'], 8)
        dataframe['ema_21'] = self.ema(dataframe['close'], 21)
        dataframe['ema_50'] = self.ema(dataframe['close'], 50)
        dataframe['sma_100'] = self.sma(dataframe['close'], 100)
        dataframe['trend_strength'] = self.calculate_trend_strength(dataframe)

        # Volatilidade
        dataframe['atr'] = self.atr(dataframe['high'], dataframe['low'], dataframe['close'])
        dataframe['volatility'] = dataframe['close'].rolling(20).std()

        return dataframe

    @informative('1h')
    def populate_indicators_1h(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        """Indicadores para timeframe 1h - Tendência de longo prazo"""
        dataframe['rsi'] = self.rsi(dataframe['close'])
        dataframe['ema_8'] = self.ema(dataframe['close'], 8)
        dataframe['ema_21'] = self.ema(dataframe['close'], 21)
        dataframe['ema_50'] = self.ema(dataframe['close'], 50)
        dataframe['sma_200'] = self.sma(dataframe['close'], 200)
        dataframe['trend_strength'] = self.calculate_trend_strength(dataframe)

        # Tendência de longo prazo
        dataframe['long_trend'] = (
            (dataframe['ema_8'] > dataframe['ema_21']) &
            (dataframe['ema_21'] > dataframe['ema_50']) &
            (dataframe['close'] > dataframe['sma_200'])
        ).astype(int)

        return dataframe

    def populate_indicators(self, dataframe, metadata):
        """
        Indicadores para timeframe principal (1m)
        """
        # Indicadores básicos 1m
        dataframe['rsi'] = self.rsi(dataframe['close'])
        dataframe['ema_8'] = self.ema(dataframe['close'], 8)
        dataframe['ema_21'] = self.ema(dataframe['close'], 21)
        dataframe['volume_sma'] = self.sma(dataframe['volume'], 20)
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_sma']

        # ATR para stop loss dinâmico
        dataframe['atr'] = self.atr(dataframe['high'], dataframe['low'], dataframe['close'])

        # Momentum de curto prazo
        dataframe['price_change_3'] = dataframe['close'].pct_change(3)
        dataframe['price_change_5'] = dataframe['close'].pct_change(5)

        # Trend strength no timeframe principal
        dataframe['trend_strength'] = self.calculate_trend_strength(dataframe)

        return dataframe

    def populate_entry_trend(self, dataframe, metadata):
        """
        Sinais de entrada baseados em confirmação multi-timeframe
        """
        # Condições do timeframe 1h (tendência de longo prazo)
        long_trend_bullish = (
            (dataframe['long_trend_1h'] == 1) &
            (dataframe['trend_strength_1h'] > 0.6)
        )

        # Condições do timeframe 15m (tendência de médio prazo)
        medium_trend_bullish = (
            (dataframe['trend_strength_15m'] > self.trend_strength_threshold.value) &
            (dataframe['rsi_15m'] < 65) &
            (dataframe['ema_8_15m'] > dataframe['ema_21_15m'])
        )

        # Condições do timeframe 5m (momentum)
        momentum_favorable = (
            (dataframe['trend_strength_5m'] > 0.6) &
            (dataframe['volume_ratio_5m'] > 1.2) &
            (dataframe['rsi_5m'] < 60)
        )

        # Condições do timeframe 1m (entrada precisa)
        entry_precise = (
            (dataframe['rsi'] < self.rsi_oversold.value) &
            (dataframe['ema_8'] > dataframe['ema_21']) &
            (dataframe['volume_ratio'] > self.volume_threshold.value) &
            (dataframe['price_change_3'] > -0.005)  # Não em queda livre
        )

        # Confirmação adicional: preço não muito longe da EMA
        price_not_extended = (
            abs(dataframe['close'] - dataframe['ema_21']) / dataframe['ema_21'] < 0.02
        )

        # Sinal final: todas as condições devem ser verdadeiras
        entry_signal = (
            long_trend_bullish &
            medium_trend_bullish &
            momentum_favorable &
            entry_precise &
            price_not_extended
        )

        dataframe.loc[entry_signal, 'enter_long'] = 1
        dataframe.loc[entry_signal, 'enter_tag'] = 'multi_tf_confirmed'

        return dataframe

    def populate_exit_trend(self, dataframe, metadata):
        """
        Sinais de saída baseados em deterioração multi-timeframe
        """
        # Saída por RSI overbought no 1m
        rsi_exit = dataframe['rsi'] > self.rsi_overbought.value

        # Saída por deterioração da tendência 5m
        momentum_deterioration = (
            (dataframe['trend_strength_5m'] < 0.4) |
            (dataframe['rsi_5m'] > 75)
        )

        # Saída por deterioração da tendência 15m
        medium_trend_deterioration = (
            (dataframe['trend_strength_15m'] < 0.3) |
            (dataframe['ema_8_15m'] < dataframe['ema_21_15m'])
        )

        # Saída por reversão da tendência 1h
        long_trend_reversal = (
            (dataframe['long_trend_1h'] == 0) &
            (dataframe['trend_strength_1h'] < 0.4)
        )

        # Volume anômalo (possível dump)
        volume_spike = dataframe['volume_ratio'] > 3.0

        # Sinal de saída: qualquer condição crítica
        exit_signal = (
            rsi_exit |
            momentum_deterioration |
            medium_trend_deterioration |
            long_trend_reversal |
            volume_spike
        )

        dataframe.loc[exit_signal, 'exit_long'] = 1

        return dataframe

    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: datetime,
                       current_rate: float, current_profit: float, **kwargs) -> float:
        """
        Stop loss dinâmico baseado no ATR
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()

        if 'atr' in last_candle:
            # Stop loss baseado em 2x ATR
            atr_stop = 2.0 * last_candle['atr'] / current_rate

            # Mínimo de 3%, máximo de 8%
            dynamic_stop = max(0.03, min(0.08, atr_stop))

            return -dynamic_stop

        # Fallback para stop loss fixo
        return self.stoploss
