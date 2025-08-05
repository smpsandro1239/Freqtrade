from freqtrade.strategy import IStrategy
import talib.abstract as ta
import pandas as pd


class SampleStrategyA(IStrategy):
    timeframe = "15m"
    minimal_roi = {"0": 0.05}
    stoploss = -0.10
    trailing_stop = True

    def populate_indicators(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe["rsi"] = ta.RSI(dataframe, timeperiod=14)
        return dataframe

    def populate_entry_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe.loc[
            (dataframe["rsi"] < 30),
            "enter_long"
        ] = 1
        return dataframe

    def populate_exit_trend(self, dataframe: pd.DataFrame, metadata: dict) -> pd.DataFrame:
        dataframe.loc[
            (dataframe["rsi"] > 70),
            "exit_long"
        ] = 1
        return dataframe