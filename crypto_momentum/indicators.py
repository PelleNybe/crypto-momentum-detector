import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volatility import BollingerBands, AverageTrueRange


class MomentumIndicators:
    def __init__(self, data: pd.DataFrame, htf_data: pd.DataFrame = None):
        """
        Initializes the indicators with OHLCV data.

        Args:
            data (pd.DataFrame): Data containing at least a 'Close' column.
            htf_data (pd.DataFrame): Optional higher timeframe data.
        """
        self.data = data
        self.htf_data = htf_data

    def calculate_all(self) -> pd.DataFrame:
        """
        Calculates a suite of momentum and trend indicators.
        """
        if self.data is None or self.data.empty or "Close" not in self.data.columns:
            return self.data

        df = self.data.copy()
        close = df["Close"]
        high = df.get("High", df["Close"])
        low = df.get("Low", df["Close"])

        # 1. Relative Strength Index (RSI) - standard 14 period
        rsi = RSIIndicator(close=close, window=14)
        df["RSI_14"] = rsi.rsi()

        # 2. Moving Average Convergence Divergence (MACD)
        macd = MACD(close=close, window_slow=26, window_fast=12, window_sign=9)
        df["MACD"] = macd.macd()
        df["MACD_Signal"] = macd.macd_signal()
        df["MACD_Hist"] = macd.macd_diff()

        # 3. Simple Moving Averages (SMA) - 20 and 50 period
        sma_20 = SMAIndicator(close=close, window=20)
        df["SMA_20"] = sma_20.sma_indicator()

        sma_50 = SMAIndicator(close=close, window=50)
        df["SMA_50"] = sma_50.sma_indicator()

        # 4. Bollinger Bands (20 period, 2 std dev)
        bollinger = BollingerBands(close=close, window=20, window_dev=2)
        df["BB_High"] = bollinger.bollinger_hband()
        df["BB_Low"] = bollinger.bollinger_lband()
        df["BB_Mid"] = bollinger.bollinger_mavg()

        # 5. Exponential Moving Averages (EMA) - 20 and 50 period
        ema_20 = EMAIndicator(close=close, window=20)
        df["EMA_20"] = ema_20.ema_indicator()

        ema_50 = EMAIndicator(close=close, window=50)
        df["EMA_50"] = ema_50.ema_indicator()

        # 6. Average True Range (ATR) - standard 14 period
        atr = AverageTrueRange(high=high, low=low, close=close, window=14)
        df["ATR_14"] = atr.average_true_range()

        # Calculate HTF indicators if HTF data exists
        if (
            self.htf_data is not None
            and not self.htf_data.empty
            and "Close" in self.htf_data.columns
        ):
            htf_df = self.htf_data.copy()

            htf_close = htf_df["Close"]

            htf_sma_20 = SMAIndicator(close=htf_close, window=20)
            htf_df["SMA_20"] = htf_sma_20.sma_indicator()

            htf_sma_50 = SMAIndicator(close=htf_close, window=50)
            htf_df["SMA_50"] = htf_sma_50.sma_indicator()

            # Simple trend identification on HTF: SMA 20 > SMA 50
            htf_df["HTF_Trend"] = htf_df["SMA_20"] > htf_df["SMA_50"]

            # Since index is dates, we want to align HTF trend with the lower timeframe
            # Forward fill the HTF values to the LTF index
            # Align the HTF trend by reindexing and forward filling

            # Extract just the trend column
            htf_trend_series = htf_df[["HTF_Trend"]].copy()

            # Ensure timezones match if both have them, or remove them
            if df.index.tz is not None and htf_trend_series.index.tz is not None:
                if df.index.tz != htf_trend_series.index.tz:
                    htf_trend_series.index = htf_trend_series.index.tz_convert(
                        df.index.tz
                    )
            elif df.index.tz is not None and htf_trend_series.index.tz is None:
                htf_trend_series.index = htf_trend_series.index.tz_localize(df.index.tz)
            elif df.index.tz is None and htf_trend_series.index.tz is not None:
                df.index = df.index.tz_localize(htf_trend_series.index.tz)

            # Merge HTF trend into df
            try:
                # Merge using merge_asof requires sorted indices
                df = df.sort_index()
                htf_trend_series = htf_trend_series.sort_index()
                df = pd.merge_asof(
                    df,
                    htf_trend_series,
                    left_index=True,
                    right_index=True,
                    direction="backward",
                )
                df["HTF_Trend"] = df["HTF_Trend"].fillna(True)
            except Exception as e:
                print(f"Error merging HTF data: {e}")
                df["HTF_Trend"] = True
        else:
            df["HTF_Trend"] = True  # Default to true if no HTF data available

        return df
