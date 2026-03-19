import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands, AverageTrueRange

class MomentumIndicators:
    def __init__(self, data: pd.DataFrame):
        """
        Initializes the indicators with OHLCV data.

        Args:
            data (pd.DataFrame): Data containing at least a 'Close' column.
        """
        self.data = data

    def calculate_all(self) -> pd.DataFrame:
        """
        Calculates a suite of momentum and trend indicators.

        Returns:
            pd.DataFrame: A copy of the input DataFrame with new columns for:
                          - RSI_14
                          - MACD, MACD_Signal, MACD_Hist
                          - SMA_20, SMA_50
                          - EMA_20, EMA_50
                          - ATR_14
        """
        if self.data is None or self.data.empty or 'Close' not in self.data.columns:
            return self.data

        df = self.data.copy()
        close = df['Close']
        high = df.get('High', df['Close'])
        low = df.get('Low', df['Close'])

        # 1. Relative Strength Index (RSI) - standard 14 period
        rsi = RSIIndicator(close=close, window=14)
        df['RSI_14'] = rsi.rsi()

        # 2. Moving Average Convergence Divergence (MACD)
        macd = MACD(close=close, window_slow=26, window_fast=12, window_sign=9)
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        df['MACD_Hist'] = macd.macd_diff()

        # 3. Simple Moving Averages (SMA) - 20 and 50 period
        sma_20 = SMAIndicator(close=close, window=20)
        df['SMA_20'] = sma_20.sma_indicator()

        sma_50 = SMAIndicator(close=close, window=50)
        df['SMA_50'] = sma_50.sma_indicator()

        # 4. Bollinger Bands (20 period, 2 std dev)
        bollinger = BollingerBands(close=close, window=20, window_dev=2)
        df['BB_High'] = bollinger.bollinger_hband()
        df['BB_Low'] = bollinger.bollinger_lband()
        df['BB_Mid'] = bollinger.bollinger_mavg()

        # 5. Exponential Moving Averages (EMA) - 20 and 50 period
        ema_20 = EMAIndicator(close=close, window=20)
        df['EMA_20'] = ema_20.ema_indicator()

        ema_50 = EMAIndicator(close=close, window=50)
        df['EMA_50'] = ema_50.ema_indicator()

        # 6. Average True Range (ATR) - standard 14 period
        atr = AverageTrueRange(high=high, low=low, close=close, window=14)
        df['ATR_14'] = atr.average_true_range()

        return df
