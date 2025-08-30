import numpy as np
import pandas as pd
from pandas import DataFrame
import talib.abstract as ta
from freqtrade.strategy import IStrategy, DecimalParameter, IntParameter
from datetime import datetime
from typing import Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SampleStrategyB(IStrategy):
    """
    Estratégia B - Baseada em RSI, MACD e Bollinger Bands
    Estratégia conservadora focada em reversões de tendência
    """
    INTERFACE_VERSION = 3

    # Configurações básicas
    timeframe = '15m'  # Timeframe diferente da Strategy A
    stoploss = -0.08   # Stop loss mais conservador
    minimal_roi = {
        "0": 0.06,     # ROI inicial maior (mais conservador)
        "10": 0.04,
        "20": 0.02,
        "40": 0.01,
        "60": 0.005
    }

    # Sem trailing stop (diferente da A)
    trailing_stop = False

    # Parâmetros otimizáveis
    rsi_period = IntParameter(10, 20, default=14, space='buy')
    rsi_oversold = IntParameter(25, 35, default=30, space='buy')
    rsi_overbought = IntParameter(65, 80, default=70, space='sell')
    
    bb_period = IntParameter(15, 25, default=20, space='buy')
    bb_std = DecimalParameter(1.8, 2.2, default=2.0, space='buy')

    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.logger = logging.getLogger(__name__)

    @property
    def protections(self):
        """Proteções básicas para Strategy B"""
        return [
            {
                "method": "CooldownPeriod",
                "stop_duration_candles": 3
            },
            {
                "method": "StoplossGuard",
                "lookback_period_candles": 24,
                "trade_limit": 2,
                "stop_duration_candles": 12,
                "only_per_pair": False
            }
        ]

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Indicadores para Strategy B - RSI, MACD, Bollinger Bands
        Foco em reversões e momentum
        """
        
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe['close'], timeperiod=self.rsi_period.value)
        
        # MACD
        macd_line, macd_signal, macd_hist = ta.MACD(dataframe['close'])
        dataframe['macd'] = macd_line
        dataframe['macdsignal'] = macd_signal
        dataframe['macdhist'] = macd_hist
        
        # Bollinger Bands
        bollinger = ta.BBANDS(dataframe['close'], 
                             timeperiod=self.bb_period.value, 
                             nbdevup=self.bb_std.value, 
                             nbdevdn=self.bb_std.value)
        dataframe['bb_lower'] = bollinger['lowerband']
        dataframe['bb_middle'] = bollinger['middleband']
        dataframe['bb_upper'] = bollinger['upperband']
        dataframe['bb_percent'] = (dataframe['close'] - dataframe['bb_lower']) / (dataframe['bb_upper'] - dataframe['bb_lower'])
        
        # Médias móveis simples
        dataframe['sma_20'] = ta.SMA(dataframe['close'], timeperiod=20)
        dataframe['sma_50'] = ta.SMA(dataframe['close'], timeperiod=50)
        
        # Volume
        dataframe['volume_sma'] = ta.SMA(dataframe['volume'], timeperiod=20)
        
        # ATR para volatilidade
        dataframe['atr'] = ta.ATR(dataframe['high'], dataframe['low'], dataframe['close'], timeperiod=14)
        
        # Stochastic
        stoch = ta.STOCH(dataframe['high'], dataframe['low'], dataframe['close'])
        dataframe['stoch_k'] = stoch['slowk']
        dataframe['stoch_d'] = stoch['slowd']
        
        return dataframe

    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Sinais de entrada para Strategy B
        Baseado em RSI oversold + MACD bullish + preço próximo à BB inferior
        """
        
        # Condições de entrada (mais conservadoras)
        rsi_condition = (
            dataframe['rsi'] < self.rsi_oversold.value
        )
        
        macd_condition = (
            (dataframe['macd'] > dataframe['macdsignal']) &
            (dataframe['macdhist'] > 0)
        )
        
        bb_condition = (
            (dataframe['close'] <= dataframe['bb_lower'] * 1.02) |  # Próximo à banda inferior
            (dataframe['bb_percent'] < 0.2)  # Na parte inferior das bandas
        )
        
        volume_condition = (
            dataframe['volume'] > dataframe['volume_sma'] * 0.8
        )
        
        trend_condition = (
            dataframe['close'] > dataframe['sma_50']  # Tendência de alta geral
        )
        
        stoch_condition = (
            (dataframe['stoch_k'] < 30) &  # Stochastic oversold
            (dataframe['stoch_k'] > dataframe['stoch_d'])  # K cruzando D para cima
        )
        
        # Combinar condições
        dataframe.loc[
            (
                rsi_condition &
                (macd_condition | bb_condition) &  # MACD OU BB (mais flexível)
                volume_condition &
                (trend_condition | stoch_condition)  # Tendência OU Stochastic
            ),
            'enter_long'
        ] = 1
        
        # Tag para identificação
        dataframe.loc[dataframe['enter_long'] == 1, 'enter_tag'] = (
            f"RSI:{dataframe['rsi']:.1f} | "
            f"MACD:{dataframe['macd']:.4f} | "
            f"BB%:{dataframe['bb_percent']:.2f} | "
            f"Stoch:{dataframe['stoch_k']:.1f}"
        )
        
        return dataframe

    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Sinais de saída para Strategy B
        Baseado em RSI overbought + MACD bearish + preço próximo à BB superior
        """
        
        # Condições de saída
        rsi_condition = (
            dataframe['rsi'] > self.rsi_overbought.value
        )
        
        macd_condition = (
            (dataframe['macd'] < dataframe['macdsignal']) &
            (dataframe['macdhist'] < 0)
        )
        
        bb_condition = (
            (dataframe['close'] >= dataframe['bb_upper'] * 0.98) |  # Próximo à banda superior
            (dataframe['bb_percent'] > 0.8)  # Na parte superior das bandas
        )
        
        volume_condition = (
            dataframe['volume'] > dataframe['volume_sma'] * 1.2  # Volume alto para confirmação
        )
        
        stoch_condition = (
            (dataframe['stoch_k'] > 70) &  # Stochastic overbought
            (dataframe['stoch_k'] < dataframe['stoch_d'])  # K cruzando D para baixo
        )
        
        # Combinar condições de saída
        dataframe.loc[
            (
                rsi_condition &
                (macd_condition | bb_condition) &  # MACD OU BB
                (volume_condition | stoch_condition)  # Volume OU Stochastic
            ),
            'exit_long'
        ] = 1
        
        # Tag para identificação
        dataframe.loc[dataframe['exit_long'] == 1, 'exit_tag'] = (
            f"RSI:{dataframe['rsi']:.1f} | "
            f"MACD:{dataframe['macd']:.4f} | "
            f"BB%:{dataframe['bb_percent']:.2f} | "
            f"Stoch:{dataframe['stoch_k']:.1f}"
        )
        
        return dataframe

    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: datetime,
                        current_rate: float, current_profit: float, **kwargs) -> float:
        """
        Stop loss dinâmico para Strategy B
        Mais conservador que a Strategy A
        """
        
        # Trailing stop baseado no lucro
        if current_profit > 0.08:  # 8% de lucro
            return 0.04  # Proteger 4%
        elif current_profit > 0.06:  # 6% de lucro
            return 0.03  # Proteger 3%
        elif current_profit > 0.04:  # 4% de lucro
            return 0.02  # Proteger 2%
        elif current_profit > 0.02:  # 2% de lucro
            return 0.01  # Proteger 1%
        
        # Stop loss baseado no tempo (mais conservador)
        trade_duration = (current_time - trade.open_date_utc).total_seconds()
        
        if trade_duration < 1800:  # Primeiros 30 minutos
            return self.stoploss  # Stop loss original
        elif trade_duration < 3600:  # Primeira hora
            return self.stoploss * 0.8  # Reduzir stop loss
        else:  # Após 1 hora
            return self.stoploss * 0.9  # Stop loss mais solto
        
        return self.stoploss