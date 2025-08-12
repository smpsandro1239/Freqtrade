# -*- coding: utf-8 -*-
"""
WaveHyperNWEnhanced - Versão melhorada da WaveHyperNW Strategy
Implementações nativas + melhorias de performance e sinais
"""
import logging
from datetime import datetime

import numpy as np
import pandas as pd

from freqtrade.strategy import (
    CategoricalParameter,
    DecimalParameter,
    IntParameter,
    IStrategy,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WaveHyperNWEnhanced(IStrategy):
    """
    Estratégia WaveHyperNW Melhorada

    Melhorias implementadas:
    - Implementações nativas (sem TA-Lib)
    - WaveTrend otimizado
    - Nadaraya-Watson melhorado
    - Filtros de volatilidade
    - Stop loss dinâmico
    - Gestão de risco aprimorada
    """

    INTERFACE_VERSION = 3

    # Configurações básicas
    timeframe = "5m"
    stoploss = -0.08  # Melhorado: stop mais conservador
    minimal_roi = {
        "0": 0.05,  # Melhorado: ROI mais realista
        "5": 0.035,
        "10": 0.025,
        "15": 0.015,
        "30": 0.008,
        "60": 0.003,
    }

    # Trailing stop melhorado
    trailing_stop = True
    trailing_stop_positive = 0.02
    trailing_stop_positive_offset = 0.035
    trailing_only_offset_is_reached = True

    # Parâmetros WaveTrend otimizados
    wt_channel_len = IntParameter(6, 12, default=8, space="buy")
    wt_average_len = IntParameter(14, 22, default=18, space="buy")
    wt_overbought = DecimalParameter(45, 65, default=55, space="sell")
    wt_oversold = DecimalParameter(-65, -45, default=-55, space="buy")

    # Parâmetros Nadaraya-Watson
    nw_bandwidth = DecimalParameter(2.0, 5.0, default=3.5, space="buy")
    nw_lookback = IntParameter(15, 35, default=25, space="buy")
    nw_std_multiplier = DecimalParameter(0.8, 2.0, default=1.2, space="buy")

    # Filtros de qualidade
    min_volume_ratio = DecimalParameter(0.3, 1.0, default=0.5, space="buy")
    max_volatility = DecimalParameter(0.02, 0.08, default=0.05, space="buy")
    trend_strength_min = DecimalParameter(0.4, 0.8, default=0.6, space="buy")

    # Proteções melhoradas
    cooldown_lookback = IntParameter(5, 30, default=12, space="protection")
    stop_duration = IntParameter(20, 120, default=45, space="protection")
    max_drawdown_protection = DecimalParameter(
        0.05, 0.15, default=0.10, space="protection"
    )
    use_stop_protection = CategoricalParameter(
        [True, False], default=True, space="protection"
    )

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
                "stop_duration_candles": self.get_int_value(self.stop_duration),
            },
            {
                "method": "StoplossGuard",
                "lookback_period_candles": self.get_int_value(self.cooldown_lookback),
                "trade_limit": 3,  # Mais conservador
                "stop_duration_candles": self.get_int_value(self.stop_duration),
                "only_per_pair": False,
            },
            {
                "method": "MaxDrawdown",
                "lookback_period_candles": 200,
                "trade_limit": 5,
                "stop_duration_candles": self.get_int_value(self.stop_duration) * 2,
                "max_allowed_drawdown": self.max_drawdown_protection.value,
            },
        ]

    def ema(self, series: pd.Series, period: int) -> pd.Series:
        """Implementação nativa da EMA"""
        return series.ewm(span=period, adjust=False).mean()

    def sma(self, series: pd.Series, period: int) -> pd.Series:
        """Implementação nativa da SMA"""
        return series.rolling(window=period).mean()

    def rsi(self, series: pd.Series, period: int = 14) -> pd.Series:
        """Implementação nativa do RSI"""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14):
        """Implementação nativa do ATR"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()

    def wavetrend(self, dataframe: pd.DataFrame) -> tuple:
        """
        Implementação melhorada do WaveTrend
        """
        # Average Price
        ap = (dataframe["high"] + dataframe["low"] + dataframe["close"]) / 3

        # Parâmetros
        channel_len = self.get_int_value(self.wt_channel_len)
        average_len = self.get_int_value(self.wt_average_len)

        # ESA (Exponential Smoothed Average)
        esa = self.ema(ap, channel_len)

        # Deviation
        d = self.ema(abs(ap - esa), channel_len)

        # Channel Index
        ci = (ap - esa) / (0.015 * d)

        # WaveTrend lines
        wt1 = self.ema(ci, average_len)
        wt2 = self.sma(wt1, 4)

        return wt1, wt2

    def nadaraya_watson(self, dataframe: pd.DataFrame) -> tuple:
        """
        Implementação melhorada do Nadaraya-Watson Estimator
        """
        close = dataframe["close"].values
        bandwidth = self.nw_bandwidth.value
        lookback = self.get_int_value(self.nw_lookback)

        # Kernel Gaussiano
        weights = np.array(
            [
                np.exp(-(i**2) / (2 * bandwidth**2))
                for i in range(-lookback, lookback + 1)
            ]
        )
        weights = weights / weights.sum()

        # Aplicar convolução
        nw_estimate = np.convolve(close, weights, mode="same")
        nw_series = pd.Series(nw_estimate, index=dataframe.index)

        # Bandas baseadas em desvio padrão
        std = dataframe["close"].rolling(lookback).std()
        multiplier = self.nw_std_multiplier.value

        nw_upper = nw_series + multiplier * std
        nw_lower = nw_series - multiplier * std

        return nw_series, nw_upper, nw_lower

    def calculate_trend_strength(self, dataframe: pd.DataFrame) -> pd.Series:
        """
        Calcular força da tendência (0 = bearish, 1 = bullish)
        """
        # EMA alignment
        ema_8 = dataframe["ema_8"]
        ema_21 = dataframe["ema_21"]
        ema_50 = dataframe["ema_50"]

        ema_score = (
            (ema_8 > ema_21).astype(int) * 0.4
            + (ema_21 > ema_50).astype(int) * 0.3
            + (dataframe["close"] > ema_8).astype(int) * 0.3
        )

        # RSI momentum
        rsi_normalized = (dataframe["rsi"] - 50) / 50
        rsi_score = (rsi_normalized.clip(-1, 1) + 1) / 2

        # WaveTrend momentum
        wt_score = ((dataframe["wt1"] + 100) / 200).clip(0, 1)

        # Combine scores
        trend_strength = ema_score * 0.5 + rsi_score * 0.3 + wt_score * 0.2

        return trend_strength.clip(0, 1)

    def calculate_volatility_filter(self, dataframe: pd.DataFrame) -> pd.Series:
        """
        Filtro de volatilidade para evitar mercados muito voláteis
        """
        # ATR normalizado
        atr_normalized = dataframe["atr"] / dataframe["close"]

        # Volatilidade baseada em desvio padrão
        price_volatility = dataframe["close"].rolling(20).std() / dataframe["close"]

        # Combinar métricas
        volatility = (atr_normalized + price_volatility) / 2

        return volatility < self.max_volatility.value

    def populate_indicators(self, dataframe, metadata):
        """
        Calcular todos os indicadores
        """
        # Indicadores básicos
        dataframe["rsi"] = self.rsi(dataframe["close"])
        dataframe["ema_8"] = self.ema(dataframe["close"], 8)
        dataframe["ema_21"] = self.ema(dataframe["close"], 21)
        dataframe["ema_50"] = self.ema(dataframe["close"], 50)
        dataframe["atr"] = self.atr(
            dataframe["high"], dataframe["low"], dataframe["close"]
        )

        # Volume
        dataframe["volume_sma"] = self.sma(dataframe["volume"], 24)
        dataframe["volume_ratio"] = dataframe["volume"] / dataframe["volume_sma"]

        # WaveTrend melhorado
        dataframe["wt1"], dataframe["wt2"] = self.wavetrend(dataframe)

        # Nadaraya-Watson melhorado
        dataframe["nw_estimate"], dataframe["nw_upper"], dataframe["nw_lower"] = (
            self.nadaraya_watson(dataframe)
        )

        # Trend strength
        dataframe["trend_strength"] = self.calculate_trend_strength(dataframe)

        # Filtros de qualidade
        dataframe["volatility_ok"] = self.calculate_volatility_filter(dataframe)

        # Momentum adicional
        dataframe["price_momentum"] = dataframe["close"].pct_change(5)
        dataframe["volume_momentum"] = dataframe["volume"].pct_change(3)

        # Support/Resistance dinâmico
        dataframe["resistance"] = dataframe["high"].rolling(20).max()
        dataframe["support"] = dataframe["low"].rolling(20).min()
        dataframe["price_position"] = (dataframe["close"] - dataframe["support"]) / (
            dataframe["resistance"] - dataframe["support"]
        )

        return dataframe

    def populate_entry_trend(self, dataframe, metadata):
        """
        Sinais de entrada melhorados
        """
        # Condições WaveTrend melhoradas
        wt_bullish = (
            (dataframe["wt1"] > dataframe["wt2"])
            & (dataframe["wt1"] < self.wt_oversold.value)
            & (dataframe["wt1"].shift(1) <= dataframe["wt1"])  # Momentum crescente
        )

        # Condições Nadaraya-Watson
        nw_support = (dataframe["close"] <= dataframe["nw_lower"]) | (
            (dataframe["close"] < dataframe["nw_estimate"]) & (dataframe["rsi"] < 40)
        )

        # Condições de tendência
        trend_favorable = (
            dataframe["trend_strength"] > self.trend_strength_min.value
        ) & (dataframe["ema_8"] > dataframe["ema_21"])

        # Condições de volume
        volume_ok = (dataframe["volume_ratio"] > self.min_volume_ratio.value) & (
            dataframe["volume_momentum"] > -0.2
        )  # Volume não em queda livre

        # Filtros de qualidade
        quality_filters = (
            dataframe["volatility_ok"]
            & (dataframe["price_momentum"] > -0.01)  # Não em queda livre
            & (dataframe["price_position"] < 0.8)  # Não muito próximo da resistência
        )

        # Confirmação adicional: RSI não overbought
        rsi_ok = dataframe["rsi"] < 65

        # Sinal final
        entry_signal = (
            wt_bullish
            & nw_support
            & trend_favorable
            & volume_ok
            & quality_filters
            & rsi_ok
        )

        dataframe.loc[entry_signal, "enter_long"] = 1
        dataframe.loc[entry_signal, "enter_tag"] = "WT_NW_enhanced"

        return dataframe

    def populate_exit_trend(self, dataframe, metadata):
        """
        Sinais de saída melhorados
        """
        # Saída por WaveTrend overbought
        wt_exit = (
            (dataframe["wt1"] < dataframe["wt2"])
            & (dataframe["wt1"] > self.wt_overbought.value)
            & (dataframe["wt1"].shift(1) >= dataframe["wt1"])  # Momentum decrescente
        )

        # Saída por RSI overbought
        rsi_exit = dataframe["rsi"] > 75

        # Saída por deterioração da tendência
        trend_deterioration = (dataframe["trend_strength"] < 0.3) | (
            dataframe["ema_8"] < dataframe["ema_21"]
        )

        # Saída por profit taking
        profit_taking = (
            dataframe["close"] > dataframe["ema_8"] * 1.04
        ) | (  # 4% acima da EMA
            (dataframe["close"] > dataframe["ema_8"] * 1.025)
            & (dataframe["rsi"] > 70)
            & (dataframe["volume_ratio"] > 1.5)
        )

        # Saída por Nadaraya-Watson resistance
        nw_resistance = (dataframe["close"] >= dataframe["nw_upper"]) & (
            dataframe["rsi"] > 60
        )

        # Saída por volume anômalo
        volume_spike = dataframe["volume_ratio"] > 4.0

        # Saída por posição próxima à resistência
        resistance_exit = (dataframe["price_position"] > 0.9) & (dataframe["rsi"] > 65)

        # Sinal de saída
        exit_signal = (
            wt_exit
            | rsi_exit
            | trend_deterioration
            | profit_taking
            | nw_resistance
            | volume_spike
            | resistance_exit
        )

        # Confirmar com volume mínimo
        volume_confirm = dataframe["volume_ratio"] > 0.3

        dataframe.loc[exit_signal & volume_confirm, "exit_long"] = 1

        return dataframe

    def custom_stoploss(
        self,
        pair: str,
        trade: "Trade",
        current_time: datetime,
        current_rate: float,
        current_profit: float,
        **kwargs
    ) -> float:
        """
        Stop loss dinâmico baseado no ATR e volatilidade
        """
        dataframe, _ = self.dp.get_analyzed_dataframe(pair, self.timeframe)
        last_candle = dataframe.iloc[-1].squeeze()

        if "atr" in last_candle and "trend_strength" in last_candle:
            # ATR normalizado
            atr_normalized = last_candle["atr"] / current_rate

            # Ajustar stop baseado na força da tendência
            trend_multiplier = 1.0 + (1.0 - last_candle["trend_strength"])

            # Stop loss dinâmico
            dynamic_stop = atr_normalized * 2.5 * trend_multiplier

            # Limites: mínimo 4%, máximo 12%
            dynamic_stop = max(0.04, min(0.12, dynamic_stop))

            return -dynamic_stop

        # Fallback
        return self.stoploss
