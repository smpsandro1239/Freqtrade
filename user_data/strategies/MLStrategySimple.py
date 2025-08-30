# -*- coding: utf-8 -*-
"""
MLStrategySimple - Simplified Machine Learning Strategy
Basic ML approach with essential indicators
"""
import logging
from typing import Optional
import numpy as np
import pandas as pd
from pandas import DataFrame
from freqtrade.strategy import IStrategy, DecimalParameter, IntParameter
import talib.abstract as ta

logger = logging.getLogger(__name__)

class MLStrategySimple(IStrategy):
    """
    Simplified Machine Learning Strategy
    """
    
    INTERFACE_VERSION = 3
    
    # Strategy parameters
    minimal_roi = {
        "0": 0.04,
        "15": 0.02,
        "30": 0.01,
        "60": 0
    }
    
    stoploss = -0.04
    timeframe = '5m'
    
    # Hyperopt parameters
    rsi_buy = IntParameter(25, 35, default=30, space="buy")
    rsi_sell = IntParameter(65, 75, default=70, space="sell")
    
    # Process only new candles
    process_only_new_candles = True
    
    # Startup candle count
    startup_candle_count: int = 20
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Add simple technical indicators
        """
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        
        # Simple Moving Averages
        dataframe['sma_10'] = ta.SMA(dataframe, timeperiod=10)
        dataframe['sma_20'] = ta.SMA(dataframe, timeperiod=20)
        
        # MACD
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        
        # Bollinger Bands
        bollinger = ta.BBANDS(dataframe)
        dataframe['bb_lower'] = bollinger['lowerband']
        dataframe['bb_upper'] = bollinger['upperband']
        
        # Volume
        dataframe['volume_avg'] = dataframe['volume'].rolling(window=10).mean()
        
        # Simple ML features
        dataframe['price_momentum'] = (dataframe['close'] / dataframe['close'].shift(5) - 1) * 100
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_avg']
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Simple entry conditions
        """
        dataframe.loc[
            (
                (dataframe['rsi'] < self.rsi_buy.value) &
                (dataframe['close'] < dataframe['bb_lower']) &
                (dataframe['macd'] > dataframe['macdsignal']) &
                (dataframe['volume'] > dataframe['volume_avg']) &
                (dataframe['price_momentum'] > -2)
            ),
            'enter_long'
        ] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Simple exit conditions
        """
        dataframe.loc[
            (
                (dataframe['rsi'] > self.rsi_sell.value) |
                (dataframe['close'] > dataframe['bb_upper']) |
                (dataframe['macd'] < dataframe['macdsignal'])
            ),
            'exit_long'
        ] = 1
        
        return dataframe