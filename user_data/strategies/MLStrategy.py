# -*- coding: utf-8 -*-
"""
MLStrategy - Machine Learning Based Trading Strategy
Uses scikit-learn for predictions based on technical features
"""
import logging
import os
import pickle
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from pandas import DataFrame
from freqtrade.strategy import IStrategy, DecimalParameter, IntParameter
import talib.abstract as ta

logger = logging.getLogger(__name__)

class MLStrategy(IStrategy):
    """
    Machine Learning Strategy using Random Forest for predictions
    """
    
    INTERFACE_VERSION = 3
    
    # Strategy parameters
    minimal_roi = {
        "0": 0.05,
        "10": 0.03,
        "20": 0.02,
        "30": 0.01
    }
    
    stoploss = -0.05
    timeframe = '5m'
    
    # Hyperopt parameters
    buy_rsi_threshold = IntParameter(20, 40, default=30, space="buy")
    sell_rsi_threshold = IntParameter(60, 80, default=70, space="sell")
    
    # Process only new candles
    process_only_new_candles = True
    
    # Startup candle count
    startup_candle_count: int = 30
    
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.model = None
        self.model_path = Path("user_data/ml_models/ml_model.pkl")
        
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Add technical indicators for ML features
        """
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        
        # MACD
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']
        
        # Bollinger Bands
        bollinger = ta.BBANDS(dataframe)
        dataframe['bb_lowerband'] = bollinger['lowerband']
        dataframe['bb_middleband'] = bollinger['middleband']
        dataframe['bb_upperband'] = bollinger['upperband']
        
        # SMA
        dataframe['sma_20'] = ta.SMA(dataframe, timeperiod=20)
        dataframe['sma_50'] = ta.SMA(dataframe, timeperiod=50)
        
        # EMA
        dataframe['ema_12'] = ta.EMA(dataframe, timeperiod=12)
        dataframe['ema_26'] = ta.EMA(dataframe, timeperiod=26)
        
        # Volume indicators
        dataframe['volume_sma'] = dataframe['volume'].rolling(window=20).mean()
        
        # Price features
        dataframe['price_change'] = dataframe['close'].pct_change()
        dataframe['high_low_ratio'] = dataframe['high'] / dataframe['low']
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Entry signal based on ML prediction and technical indicators
        """
        conditions = []
        
        # Basic technical conditions
        conditions.append(dataframe['rsi'] < self.buy_rsi_threshold.value)
        conditions.append(dataframe['close'] < dataframe['bb_lowerband'])
        conditions.append(dataframe['volume'] > dataframe['volume_sma'])
        
        # ML prediction (if model is available)
        if self.model is not None:
            try:
                features = self._prepare_features(dataframe)
                if features is not None and len(features) > 0:
                    predictions = self.model.predict_proba(features)[:, 1]  # Probability of positive class
                    dataframe['ml_prediction'] = predictions
                    conditions.append(dataframe['ml_prediction'] > 0.6)
            except Exception as e:
                logger.warning(f"ML prediction failed: {e}")
        
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'enter_long'
            ] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Exit signal based on technical indicators
        """
        conditions = []
        
        conditions.append(dataframe['rsi'] > self.sell_rsi_threshold.value)
        conditions.append(dataframe['close'] > dataframe['bb_upperband'])
        
        if conditions:
            dataframe.loc[
                reduce(lambda x, y: x & y, conditions),
                'exit_long'
            ] = 1
        
        return dataframe
    
    def _prepare_features(self, dataframe: DataFrame) -> Optional[np.ndarray]:
        """
        Prepare features for ML model
        """
        try:
            feature_columns = [
                'rsi', 'macd', 'macdsignal', 'macdhist',
                'bb_lowerband', 'bb_middleband', 'bb_upperband',
                'sma_20', 'sma_50', 'ema_12', 'ema_26',
                'volume_sma', 'price_change', 'high_low_ratio'
            ]
            
            # Check if all features are available
            available_features = [col for col in feature_columns if col in dataframe.columns]
            
            if len(available_features) < len(feature_columns):
                logger.warning(f"Missing features: {set(feature_columns) - set(available_features)}")
                return None
            
            features = dataframe[available_features].fillna(0).values
            return features
            
        except Exception as e:
            logger.error(f"Error preparing features: {e}")
            return None

def reduce(function, iterable):
    """Simple reduce implementation"""
    it = iter(iterable)
    value = next(it)
    for element in it:
        value = function(value, element)
    return value