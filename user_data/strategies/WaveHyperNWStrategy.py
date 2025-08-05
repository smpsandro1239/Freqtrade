import numpy as np
import pandas as pd
from pandas import DataFrame
from functools import reduce
import talib.abstract as ta
from freqtrade.strategy import IStrategy, DecimalParameter, IntParameter, CategoricalParameter
from datetime import datetime
from typing import Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WaveHyperNWStrategy(IStrategy):
    INTERFACE_VERSION = 3
    
    # Configurações básicas
    timeframe = '5m'
    stoploss = -0.09
    minimal_roi = {
        "0": 0.04,
        "5": 0.03,
        "10": 0.02,
        "15": 0.01,
        "30": 0.001
    }
    
    # Configurações de trailing
    trailing_stop = True
    trailing_stop_positive = 0.046
    trailing_stop_positive_offset = 0.058
    trailing_only_offset_is_reached = True
    
    # Parâmetros otimizados
    wt_channel_len = IntParameter(4, 8, default=6, space='buy')
    wt_average_len = IntParameter(12, 18, default=14, space='buy')
    wt_overbought2 = DecimalParameter(48, 58, default=53, space='sell')
    wt_oversold2 = DecimalParameter(-58, -48, default=-53, space='buy')
    
    # Parâmetros de proteção
    cooldown_lookback = IntParameter(2, 48, default=5, space="protection", optimize=True)
    stop_duration = IntParameter(12, 200, default=5, space="protection", optimize=True)
    use_stop_protection = CategoricalParameter([True, False], default=True, space="protection", optimize=True)
    
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.logger = logging.getLogger(__name__)
        self.last_entry_signal_state = {}  # Dicionário para rastrear o último estado de enter_long por par
    
    def get_int_value(self, param):
        return int(param.value)
    
    @property
    def protections(self):
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
        ] if self.use_stop_protection.value else []
    
    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        # WaveTrend
        ap = (dataframe['high'] + dataframe['low'] + dataframe['close']) / 3
        wt_channel_len = self.get_int_value(self.wt_channel_len)
        wt_average_len = self.get_int_value(self.wt_average_len)
        
        esa = ta.EMA(ap, timeperiod=wt_channel_len)
        d = ta.EMA(abs(ap - esa), timeperiod=wt_channel_len)
        ci = (ap - esa) / (0.015 * d)
        tci = ta.EMA(ci, timeperiod=wt_average_len)
        
        dataframe['wt1'] = tci
        dataframe['wt2'] = ta.SMA(dataframe['wt1'], timeperiod=4)
        
        # Indicadores adicionais
        dataframe['rsi'] = ta.RSI(dataframe['close'], timeperiod=14)
        dataframe['atr'] = ta.ATR(dataframe['high'], dataframe['low'], dataframe['close'], timeperiod=14)
        dataframe['ht_atr'] = dataframe['atr'] * 1.2
        
        # Médias móveis
        dataframe['ema_8'] = ta.EMA(dataframe['close'], timeperiod=8)
        dataframe['ema_21'] = ta.EMA(dataframe['close'], timeperiod=21)
        dataframe['ema_50'] = ta.EMA(dataframe['close'], timeperiod=50)
        
        # Volume e volatilidade
        dataframe['volume_mean'] = dataframe['volume'].rolling(window=24).mean()
        dataframe['price_change'] = abs(dataframe['close'].pct_change() * 100)
        dataframe['volatility'] = dataframe['close'].rolling(window=48).std()
        
        # Nadaraya-Watson
        def gaussian_kernel(x, h):
            return np.exp(-(x**2)/(2*h**2))
        
        close = dataframe['close'].values
        h = 3.0
        weights = np.array([gaussian_kernel(i, h) for i in range(-20, 21)])
        weights = weights / np.sum(weights)
        nw = np.convolve(close, weights, mode='same')
        
        dataframe['nw_upper'] = pd.Series(nw) + 0.8 * dataframe['close'].rolling(10).std()
        dataframe['nw_lower'] = pd.Series(nw) - 0.8 * dataframe['close'].rolling(10).std()
        
        # Tendência do mercado
        dataframe['trend'] = np.where(
            (dataframe['ema_8'] > dataframe['ema_21']) & 
            (dataframe['ema_21'] > dataframe['ema_50']),
            'uptrend',
            'downtrend'
        )
        
        return dataframe
    
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []
        
        # Condições de entrada
        wt_cond = (
            (dataframe['wt1'] > dataframe['wt2']) &
            ((dataframe['wt1'] < self.wt_oversold2.value) |
             (dataframe['wt1'].shift(1) < dataframe['wt1']))
        )
        
        volume_cond = (
            (dataframe['volume'] > 0) &
            ((dataframe['volume'] > dataframe['volume_mean'] * 0.4) |
             ((dataframe['volume'] > dataframe['volume_mean'] * 0.3) &
              (dataframe['close'] > dataframe['ema_8'])))
        )
        
        trend_cond = (
            (dataframe['ema_8'] > dataframe['ema_21']) |
            ((dataframe['close'] < dataframe['nw_lower']) &
             (dataframe['rsi'] < 40)) |
            ((dataframe['close'] < dataframe['ema_8'] * 0.995) &
             (dataframe['volume'] > dataframe['volume_mean']))
        )
        
        conditions.extend([
            wt_cond,
            volume_cond,
            trend_cond,
            ((dataframe['close'] <= dataframe['nw_lower']) |
             (dataframe['rsi'] < 40) |
             (dataframe['close'] < dataframe['ema_8'] * 0.997))
        ])
        
        entry_signal = reduce(lambda x, y: x & y, conditions)
        
        # Inicializar enter_long como 0
        dataframe['enter_long'] = 0
        
        # Detectar transição de "sem sinal" para "sinal de entrada"
        dataframe.loc[
            entry_signal & (dataframe['enter_long'].shift(1).fillna(0) == 0),
            'enter_long'
        ] = 1
        
        # Registrar sinal de entrada no log apenas para novos sinais
        if dataframe['enter_long'].iloc[-1] == 1:
            logger.info(f"Novo sinal de entrada detectado para {metadata['pair']} em {dataframe['date'].iloc[-1]}")
        
        # Adicionar informações detalhadas para o Telegram
        if dataframe['enter_long'].iloc[-1] == 1:
            dataframe.loc[dataframe.index[-1], 'enter_tag'] = (
                f"WT1: {dataframe['wt1'].iloc[-1]:.2f} | "
                f"WT2: {dataframe['wt2'].iloc[-1]:.2f} | "
                f"EMA8: {dataframe['ema_8'].iloc[-1]:.2f} | "
                f"EMA21: {dataframe['ema_21'].iloc[-1]:.2f} | "
                f"EMA50: {dataframe['ema_50'].iloc[-1]:.2f} | "
                f"Volume: {dataframe['volume'].iloc[-1]:.2f} | "
                f"RSI: {dataframe['rsi'].iloc[-1]:.2f}"
            )
        
        return dataframe
    
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        conditions = []
        
        # Condições de saída
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
             (dataframe['volume'] > dataframe['volume_mean'] * 1.2))
        )
        
        exit_cond = (
            (dataframe['close'] < dataframe['ema_8']) &
            (dataframe['close'] < dataframe['ema_21']) &
            (dataframe['rsi'] > 75) &
            (dataframe['wt1'] > 0) &
            (dataframe['volume'] > dataframe['volume_mean'] * 1.2)
        )
        
        volume_cond = (dataframe['volume'] > dataframe['volume_mean'] * 0.8)
        
        conditions.extend([
            (profit_cond | (wt_cond & exit_cond)),
            volume_cond
        ])
        
        dataframe.loc[
            reduce(lambda x, y: x & y, conditions), 'exit_long'
        ] = 1
        
        return dataframe
    
    def bot_loop_start(self, **kwargs) -> None:
        for pair in self.dp.current_whitelist():
            dataframe, last_analyzed = self.dp.get_analyzed_dataframe(pair, self.timeframe)
            if dataframe is not None and not dataframe.empty:
                current_time = dataframe['date'].iloc[-1]
                
                if pair not in self.last_entry_signal_state:
                    self.last_entry_signal_state[pair] = 0
                
                current_state = dataframe['enter_long'].iloc[-1]
                previous_state = self.last_entry_signal_state[pair]
                
                if current_state == 1 and previous_state == 0:
                    logger.info(f"Novo sinal de entrada detectado para {pair} às {current_time}")
                    
                    message = (
                        f"📈 Sinal de entrada detectado para {pair}!\n"
                        f"Data: {current_time}\n"
                        f"Preço: {dataframe['close'].iloc[-1]:.2f}\n"
                        f"WT1: {dataframe['wt1'].iloc[-1]:.2f}, WT2: {dataframe['wt2'].iloc[-1]:.2f}\n"
                        f"EMA8: {dataframe['ema_8'].iloc[-1]:.2f}, EMA21: {dataframe['ema_21'].iloc[-1]:.2f}\n"
                        f"EMA50: {dataframe['ema_50'].iloc[-1]:.2f}\n"
                        f"Volume: {dataframe['volume'].iloc[-1]:.2f}\n"
                        f"RSI: {dataframe['rsi'].iloc[-1]:.2f}"
                    )
                    
                    try:
                        self.dp.send_msg(message)
                        logger.info(f"Mensagem enviada ao Telegram: {message}")
                    except Exception as e:
                        logger.error(f"Falha ao enviar mensagem ao Telegram: {e}")
                else:
                    logger.debug(f"Nenhum novo sinal de entrada para {pair} às {current_time}")
                
                self.last_entry_signal_state[pair] = current_state
    
    def custom_stoploss(self, pair: str, trade: 'Trade', current_time: datetime,
                       current_rate: float, current_profit: float, **kwargs) -> float:
        if current_profit > 0.05:
            return 0.03
        elif current_profit > 0.04:
            return 0.02
        elif current_profit > 0.03:
            return 0.015
        
        trade_duration = (current_time - trade.open_date_utc).total_seconds()
        
        if trade_duration < 3600:
            return self.stoploss
        elif trade_duration < 10800:
            return self.stoploss * 0.7
        elif trade_duration < 21600:
            return self.stoploss * 0.85
        else:
            return self.stoploss