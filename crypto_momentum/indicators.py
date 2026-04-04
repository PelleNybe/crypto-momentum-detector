import pandas as pd
from ta.momentum import RSIIndicator, StochRSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator, IchimokuIndicator, ADXIndicator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, VolumeWeightedAveragePrice
import numpy as np


class MomentumIndicators:
    def __init__(self, data: pd.DataFrame, htf_data: pd.DataFrame = None):
        self.data = data
        self.htf_data = htf_data

    def calculate_vpvr(self, df: pd.DataFrame, bins: int = 50) -> dict:
        """Calculates Volume Profile Visible Range (VPVR) to find the Point of Control (POC)."""
        if df.empty or "Volume" not in df.columns:
            return {"poc_price": 0, "profile": pd.DataFrame()}

        recent_df = df.tail(100).copy()
        min_price = recent_df["Low"].min()
        max_price = recent_df["High"].max()

        if pd.isna(min_price) or pd.isna(max_price) or min_price == max_price:
            return {
                "poc_price": recent_df["Close"].iloc[-1] if not recent_df.empty else 0,
                "profile": pd.DataFrame(),
            }

        price_bins = np.linspace(min_price, max_price, bins + 1)
        recent_df["Typical_Price"] = (
            recent_df["High"] + recent_df["Low"] + recent_df["Close"]
        ) / 3
        bin_indices = np.digitize(recent_df["Typical_Price"], price_bins)

        volume_profile = np.zeros(bins)
        for i in range(len(recent_df)):
            bin_idx = bin_indices[i] - 1
            if 0 <= bin_idx < bins:
                volume_profile[bin_idx] += recent_df["Volume"].iloc[i]

        poc_idx = np.argmax(volume_profile)
        poc_price = (price_bins[poc_idx] + price_bins[poc_idx + 1]) / 2

        profile_df = pd.DataFrame(
            {
                "Price_Start": price_bins[:-1],
                "Price_End": price_bins[1:],
                "Volume": volume_profile,
            }
        )
        return {"poc_price": poc_price, "profile": profile_df}

    def calculate_fibonacci_retracements(
        self, df: pd.DataFrame, period: int = 100
    ) -> pd.DataFrame:
        """Calculates dynamic Fibonacci retracement levels based on a rolling high/low window."""
        rolling_high = df["High"].rolling(window=period, min_periods=10).max()
        rolling_low = df["Low"].rolling(window=period, min_periods=10).min()

        diff = rolling_high - rolling_low

        df["Fib_0"] = rolling_high
        df["Fib_0.236"] = rolling_high - 0.236 * diff
        df["Fib_0.382"] = rolling_high - 0.382 * diff
        df["Fib_0.5"] = rolling_high - 0.5 * diff
        df["Fib_0.618"] = rolling_high - 0.618 * diff
        df["Fib_0.786"] = rolling_high - 0.786 * diff
        df["Fib_1"] = rolling_low

        return df

    def calculate_obv_divergence(
        self, df: pd.DataFrame, window: int = 14
    ) -> pd.DataFrame:
        if "Volume" not in df.columns:
            df["OBV"] = 0
            df["OBV_Bullish_Div"] = False
            df["OBV_Bearish_Div"] = False
            return df

        obv = OnBalanceVolumeIndicator(close=df["Close"], volume=df["Volume"])
        df["OBV"] = obv.on_balance_volume()

        price_roc = df["Close"].pct_change(periods=window, fill_method=None)
        obv_roc = df["OBV"].pct_change(periods=window, fill_method=None)

        df["OBV_Bullish_Div"] = (price_roc < 0) & (obv_roc > 0)
        df["OBV_Bearish_Div"] = (price_roc > 0) & (obv_roc < 0)

        return df

    def detect_patterns(self, df: pd.DataFrame, window: int = 5) -> pd.DataFrame:
        """Detects Double Top and Double Bottom patterns"""
        df["Pattern"] = "None"
        df["Local_Max"] = (
            df["High"].rolling(window=window * 2 + 1, center=True).max() == df["High"]
        )
        df["Local_Min"] = (
            df["Low"].rolling(window=window * 2 + 1, center=True).min() == df["Low"]
        )

        tolerance = 0.02

        # Vectorized Double Top detection
        peaks = df["High"].where(df["Local_Max"])
        last_peaks = peaks.shift(1).ffill()
        df["Double_Top"] = df["Local_Max"] & (
            np.abs(df["High"] - last_peaks) / last_peaks < tolerance
        )

        # Vectorized Double Bottom detection
        troughs = df["Low"].where(df["Local_Min"])
        last_troughs = troughs.shift(1).ffill()
        df["Double_Bottom"] = df["Local_Min"] & (
            np.abs(df["Low"] - last_troughs) / last_troughs < tolerance
        )

        df.loc[df["Double_Top"], "Pattern"] = "Double Top"
        df.loc[df["Double_Bottom"], "Pattern"] = "Double Bottom"

        return df

    def calculate_chandelier_exit(
        self, df: pd.DataFrame, period: int = 22, multiplier: float = 3.0
    ) -> pd.DataFrame:
        """Calculates Chandelier Exit (Dynamic Trailing Stop)"""
        rolling_high = df["High"].rolling(window=period).max()
        rolling_low = df["Low"].rolling(window=period).min()

        atr = AverageTrueRange(
            high=df["High"], low=df["Low"], close=df["Close"], window=period
        )
        atr_val = atr.average_true_range()

        df["Chandelier_Long"] = rolling_high - (atr_val * multiplier)
        df["Chandelier_Short"] = rolling_low + (atr_val * multiplier)

        return df

    def calculate_all(self) -> pd.DataFrame:
        if self.data is None or self.data.empty or "Close" not in self.data.columns:
            return self.data

        df = self.data.copy()
        close = df["Close"]
        high = df.get("High", df["Close"])
        low = df.get("Low", df["Close"])

        rsi = RSIIndicator(close=close, window=14)
        df["RSI_14"] = rsi.rsi()

        macd = MACD(close=close, window_slow=26, window_fast=12, window_sign=9)
        df["MACD"] = macd.macd()
        df["MACD_Signal"] = macd.macd_signal()
        df["MACD_Hist"] = macd.macd_diff()

        sma_20 = SMAIndicator(close=close, window=20)
        df["SMA_20"] = sma_20.sma_indicator()

        sma_50 = SMAIndicator(close=close, window=50)
        df["SMA_50"] = sma_50.sma_indicator()

        bollinger = BollingerBands(close=close, window=20, window_dev=2)
        df["BB_High"] = bollinger.bollinger_hband()
        df["BB_Low"] = bollinger.bollinger_lband()
        df["BB_Mid"] = bollinger.bollinger_mavg()

        ema_20 = EMAIndicator(close=close, window=20)
        df["EMA_20"] = ema_20.ema_indicator()

        ema_50 = EMAIndicator(close=close, window=50)
        df["EMA_50"] = ema_50.ema_indicator()

        atr = AverageTrueRange(high=high, low=low, close=close, window=14)
        df["ATR_14"] = atr.average_true_range()

        try:
            ichimoku = IchimokuIndicator(
                high=high, low=low, window1=9, window2=26, window3=52
            )
            df["Ichimoku_Conv"] = ichimoku.ichimoku_conversion_line()
            df["Ichimoku_Base"] = ichimoku.ichimoku_base_line()
            df["Ichimoku_SpanA"] = ichimoku.ichimoku_a()
            df["Ichimoku_SpanB"] = ichimoku.ichimoku_b()
            df["Ichimoku_Bullish"] = (close > df["Ichimoku_SpanA"]) & (
                close > df["Ichimoku_SpanB"]
            )
            df["Ichimoku_Bearish"] = (close < df["Ichimoku_SpanA"]) & (
                close < df["Ichimoku_SpanB"]
            )
        except Exception as e:
            df["Ichimoku_Bullish"] = False
            df["Ichimoku_Bearish"] = False

        df = self.calculate_fibonacci_retracements(df, period=100)

        vpvr_data = self.calculate_vpvr(df)
        df["VPVR_POC"] = vpvr_data["poc_price"]

        # NEW FEATURES
        # VWAP
        if "Volume" in df.columns:
            vwap = VolumeWeightedAveragePrice(
                high=high, low=low, close=close, volume=df["Volume"], window=14
            )
            df["VWAP"] = vwap.volume_weighted_average_price()
        else:
            df["VWAP"] = close

        df = self.calculate_obv_divergence(df)
        df = self.detect_patterns(df)
        df = self.calculate_chandelier_exit(df)

        adx = ADXIndicator(high=high, low=low, close=close, window=14)
        df["ADX"] = adx.adx()
        df["DI_Plus"] = adx.adx_pos()
        df["DI_Minus"] = adx.adx_neg()

        df["Market_Regime"] = "Ranging"
        df.loc[(df["ADX"] > 25) & (df["DI_Plus"] > df["DI_Minus"]), "Market_Regime"] = (
            "Trending Bullish"
        )
        df.loc[(df["ADX"] > 25) & (df["DI_Minus"] > df["DI_Plus"]), "Market_Regime"] = (
            "Trending Bearish"
        )

        stoch_rsi = StochRSIIndicator(close=close, window=14, smooth1=3, smooth2=3)
        df["Stoch_RSI_K"] = stoch_rsi.stochrsi_k()
        df["Stoch_RSI_D"] = stoch_rsi.stochrsi_d()
        df["Stoch_Bullish_Cross"] = (df["Stoch_RSI_K"] > df["Stoch_RSI_D"]) & (
            df["Stoch_RSI_K"].shift(1) <= df["Stoch_RSI_D"].shift(1)
        )
        df["Stoch_Bearish_Cross"] = (df["Stoch_RSI_K"] < df["Stoch_RSI_D"]) & (
            df["Stoch_RSI_K"].shift(1) >= df["Stoch_RSI_D"].shift(1)
        )

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
            htf_df["HTF_Trend"] = htf_df["SMA_20"] > htf_df["SMA_50"]
            htf_trend_series = htf_df[["HTF_Trend"]].copy()

            if df.index.tz is not None and htf_trend_series.index.tz is not None:
                if df.index.tz != htf_trend_series.index.tz:
                    htf_trend_series.index = htf_trend_series.index.tz_convert(
                        df.index.tz
                    )
            elif df.index.tz is not None and htf_trend_series.index.tz is None:
                htf_trend_series.index = htf_trend_series.index.tz_localize(df.index.tz)
            elif df.index.tz is None and htf_trend_series.index.tz is not None:
                df.index = df.index.tz_localize(htf_trend_series.index.tz)

            try:
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
                df["HTF_Trend"] = True
        else:
            df["HTF_Trend"] = True

        return df
