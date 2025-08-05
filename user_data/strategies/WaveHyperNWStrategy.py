# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from functools import reduce
import talib.abstract as ta
from freqtrade.strategy import IStrategy, DecimalParameter, IntParameter, CategoricalParameter
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WaveHyperNWStrategy(IStrategy):
    INTERFACE_VERSION = 3
    
    timeframe = '5m'
    stoploss = -0.09
    minimal_roi = {
        "0": 0.04,
        "5": 0.03,
        "10": 0.02,
        "15": 0.01,
        "30": 0.001
    }
    
    trailing_stop = True
    trailing_stop_positive = 0.046
    trailing_stop_positive_offset = 0.058
    trailing_only_offset_is_reached = True
    
    # Parâmetros ajustados para mais sinais
    wt_channel_len = IntParameter(4, 8, default=6, space='buy')
    wt_average_len = IntParameter(12, 18, default=14, space='buy')
    wt_overbought2 = DecimalParameter(48, 58, default=53, space='sell')
    wt_oversold2 = DecimalParameter(-58, -48, default=-58, space='buy')  # mais largo
    
    # Proteções
    cooldown_lookback = IntParameter(2, 48, default=5, space="protection")
    stop_duration = IntParameter(12, 200, default=5, space="protection")
    use_stop_protection = CategoricalParameter([True, False], default=True, space="protection")
    
    def get_int_value(self, param):
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
                "trade_limit": 4,
                "stop_duration_candles": self.get_int_value(self.stop_duration),
                "only_per_pair": False
            }
        ]
    
    def populate_indicators(self, dataframe, metadata):
        # WaveTrend
        ap = (dataframe['high'] + dataframe['low'] + dataframe['close']) / 3
        c_len = self.get_int_value(self.wt_channel_len)
        a_len = self.get_int_value(self.wt_average_len)
        
        esa = ta.EMA(ap, timeperiod=c_len)
        d = ta.EMA(abs(ap - esa), timeperiod=c_len)
        ci = (ap - esa) / (0.015 * d)
        tci = ta.EMA(ci, timeperiod=a_len)
        
        dataframe['wt1'] = tci
        dataframe['wt2'] = ta.SMA(dataframe['wt1'], timeperiod=4)
        
        # Auxiliares
        dataframe['rsi'] = ta.RSI(dataframe['close'], timeperiod=14)
        dataframe['atr'] = ta.ATR(dataframe['high'], dataframe['low'], dataframe['close'], timeperiod=14)
        dataframe['ema_8'] = ta.EMA(dataframe['close'], timeperiod=8)
        dataframe['ema_21'] = ta.EMA(dataframe['close'], timeperiod=21)
        dataframe['ema_50'] = ta.EMA(dataframe['close'], timeperiod=50)
        dataframe['vol_mean'] = dataframe['volume'].rolling(window=24).mean()
        
        # Nadaraya-Watson (kernel gaussiano)
        close = dataframe['close'].values
        h = 3.0
        weights = np.array([np.exp(-(i**2)/(2*h**2)) for i in range(-20, 21)])
        weights = weights / weights.sum()
        nw = np.convolve(close, weights, mode='same')
        std = dataframe['close'].rolling(10).std()
        dataframe['nw_upper'] = pd.Series(nw) + 1.0 * std  # banda + larga
        dataframe['nw_lower'] = pd.Series(nw) - 1.0 * std  # banda + larga
        
        return dataframe
    
    def populate_entry_trend(self, dataframe, metadata):
        # Condições relaxadas
        wt_cond = (
            (dataframe['wt1'] > dataframe['wt2']) &
            (dataframe['wt1'] < self.wt_oversold2.value)
        )
        
        volume_cond = (
            (dataframe['volume'] > 0) &
            (dataframe['volume'] > dataframe['vol_mean'] * 0.25)  # 0.4 → 0.25
        )
        
        trend_cond = (
            (dataframe['ema_8'] > dataframe['ema_21']) |
            ((dataframe['close'] < dataframe['nw_lower']) & (dataframe['rsi'] < 45)) |  # 40→45
            ((dataframe['close'] < dataframe['ema_8'] * 1.005) & (dataframe['volume'] > dataframe['vol_mean']))
        )
        
        entry_signal = wt_cond & volume_cond & trend_cond
        
        dataframe['enter_long'] = 0
        dataframe.loc[entry_signal, 'enter_long'] = 1
        dataframe.loc[entry_signal, 'enter_tag'] = 'WT_relaxed'
        
        return dataframe
    
    def populate_exit_trend(self, dataframe, metadata):
        wt_cond = (
            (dataframe['wt1'] < dataframe['wt2']) &
            (dataframe['wt1'] > self.wt_overbought2.value) &
            (dataframe['wt1'].shift(1) > dataframe['wt1']) &
            (dataframe['rsi'] > 70)
        )
        
        profit_cond = (
            (dataframe['close'] > dataframe['ema_8'] * 1.03) |
            ((dataframe['close'] > dataframe['ema_8'] * 1.025) & 
             (dataframe['rsi'] > 75) & 
             (dataframe['volume'] > dataframe['vol_mean'] * 1.2))
        )
        
        exit_signal = (profit_cond | wt_cond) & (dataframe['volume'] > dataframe['vol_mean'] * 0.8)
        
        dataframe.loc[exit_signal, 'exit_long'] = 1
        return dataframe