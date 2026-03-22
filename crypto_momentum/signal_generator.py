import pandas as pd
from crypto_momentum.ai_predictor import AIPredictor


class SignalGenerator:
    def __init__(
        self,
        data: pd.DataFrame,
        rsi_buy_min: int = 40,
        rsi_buy_max: int = 70,
        rsi_sell_min: int = 30,
        rsi_sell_max: int = 60,
        rsi_strong_buy: int = 30,
        rsi_strong_sell: int = 70,
        use_mtf: bool = False,
        atr_sl_multiplier: float = 1.5,
        atr_tp_multiplier: float = 3.0,
    ):
        self.data = data
        self.rsi_buy_min = rsi_buy_min
        self.rsi_buy_max = rsi_buy_max
        self.rsi_sell_min = rsi_sell_min
        self.rsi_sell_max = rsi_sell_max
        self.rsi_strong_buy = rsi_strong_buy
        self.rsi_strong_sell = rsi_strong_sell
        self.use_mtf = use_mtf
        self.atr_sl_multiplier = atr_sl_multiplier
        self.atr_tp_multiplier = atr_tp_multiplier

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None or self.data.empty:
            return pd.DataFrame()

        df = self.data.copy()

        required_cols = [
            "RSI_14",
            "MACD",
            "MACD_Signal",
            "SMA_20",
            "SMA_50",
            "EMA_20",
            "EMA_50",
            "ATR_14",
            "Close",
            "BB_High",
            "BB_Low",
        ]
        if not all(col in df.columns for col in required_cols):
            df["Signal"] = "HOLD"
            return df

        valid_mask = df["SMA_50"].notna()

        rsi = df["RSI_14"]
        macd = df["MACD"]
        macd_signal = df["MACD_Signal"]
        close = df["Close"]
        sma_20 = df["SMA_20"]
        ema_50 = df["EMA_50"]
        ema_20 = df["EMA_20"]
        bb_low = df["BB_Low"]
        bb_high = df["BB_High"]

        # Optional Ichimoku Confluence Check
        if "Ichimoku_Bullish" in df.columns:
            ichimoku_bullish = df["Ichimoku_Bullish"]
            ichimoku_bearish = df["Ichimoku_Bearish"]
        else:
            ichimoku_bullish = pd.Series(True, index=df.index)
            ichimoku_bearish = pd.Series(True, index=df.index)

        if "HTF_Trend" in df.columns and self.use_mtf:
            htf_bullish = df["HTF_Trend"] == True
            htf_bearish = df["HTF_Trend"] == False
        else:
            htf_bullish = pd.Series(True, index=df.index)
            htf_bearish = pd.Series(True, index=df.index)

        is_bullish = (
            (rsi > self.rsi_buy_min)
            & (rsi < self.rsi_buy_max)
            & (macd > macd_signal)
            & (close > ema_20)
            & htf_bullish
            & (ichimoku_bullish | (close > ema_50))  # Added confluence check
        )
        is_bearish = (
            (rsi < self.rsi_sell_max)
            & (rsi > self.rsi_sell_min)
            & (macd < macd_signal)
            & (close < ema_20)
            & htf_bearish
            & (ichimoku_bearish | (close < ema_50))  # Added confluence check
        )

        strong_buy_cond = (
            (rsi < self.rsi_strong_buy)
            & (macd > macd_signal)
            & (close < bb_low)
            & htf_bullish
        )
        strong_sell_cond = (
            (rsi > self.rsi_strong_sell)
            & (macd < macd_signal)
            & (close > bb_high)
            & htf_bearish
        )

        df["Signal"] = "HOLD"

        df.loc[valid_mask & is_bullish, "Signal"] = "BUY"
        df.loc[valid_mask & is_bearish, "Signal"] = "SELL"
        df.loc[valid_mask & strong_buy_cond, "Signal"] = "STRONG BUY"
        df.loc[valid_mask & strong_sell_cond, "Signal"] = "STRONG SELL"

        df["Stop_Loss"] = float("nan")
        df["Take_Profit"] = float("nan")

        buy_mask = df["Signal"].isin(["BUY", "STRONG BUY"])
        # If we have Chandelier Long, use it, else fallback
        df.loc[buy_mask, "Stop_Loss"] = (
            df.loc[buy_mask, "Chandelier_Long"]
            if "Chandelier_Long" in df.columns
            else df.loc[buy_mask, "Close"]
            - (df.loc[buy_mask, "ATR_14"] * self.atr_sl_multiplier)
        )
        df.loc[buy_mask, "Take_Profit"] = df.loc[buy_mask, "Close"] + (
            df.loc[buy_mask, "ATR_14"] * self.atr_tp_multiplier
        )

        sell_mask = df["Signal"].isin(["SELL", "STRONG SELL"])
        df.loc[sell_mask, "Stop_Loss"] = (
            df.loc[sell_mask, "Chandelier_Short"]
            if "Chandelier_Short" in df.columns
            else df.loc[sell_mask, "Close"]
            + (df.loc[sell_mask, "ATR_14"] * self.atr_sl_multiplier)
        )
        df.loc[sell_mask, "Take_Profit"] = df.loc[sell_mask, "Close"] - (
            df.loc[sell_mask, "ATR_14"] * self.atr_tp_multiplier
        )

        return df

    def get_latest_signal(self) -> dict:
        df_with_signals = self.generate_signals()

        if df_with_signals.empty or "Signal" not in df_with_signals.columns:
            return {}

        # Get AI Prediction
        predictor = AIPredictor(df_with_signals)
        ai_confidence = predictor.train_and_predict()

        latest = df_with_signals.iloc[-1]

        date_str = (
            str(df_with_signals.index[-1].date())
            if hasattr(df_with_signals.index[-1], "date")
            else str(df_with_signals.index[-1])
        )

        sparkline_data = df_with_signals["Close"].tail(14).tolist()

        return {
            "Date": date_str,
            "Price": latest["Close"],
            "RSI": latest["RSI_14"],
            "MACD": latest["MACD"],
            "MACD_Signal": latest["MACD_Signal"],
            "SMA_20": latest["SMA_20"],
            "SMA_50": latest["SMA_50"],
            "EMA_20": latest.get("EMA_20", 0),
            "EMA_50": latest.get("EMA_50", 0),
            "ATR_14": latest.get("ATR_14", 0),
            "BB_High": latest["BB_High"],
            "BB_Low": latest["BB_Low"],
            "Action": latest["Signal"],
            "HTF_Trend": latest.get("HTF_Trend", True),
            "Stop_Loss": latest.get("Stop_Loss", float("nan")),
            "Take_Profit": latest.get("Take_Profit", float("nan")),
            "Sparkline_Data": sparkline_data,
            # NEW FEATURES
            "AI_Confidence": ai_confidence,
            "VPVR_POC": latest.get("VPVR_POC", 0),
            "Ichimoku_Bullish": latest.get("Ichimoku_Bullish", False),
            "Ichimoku_Bearish": latest.get("Ichimoku_Bearish", False),
            "Fib_0": latest.get("Fib_0", 0),
            "Fib_0.5": latest.get("Fib_0.5", 0),
            "Fib_1": latest.get("Fib_1", 0),
            "OBV_Bullish_Div": latest.get("OBV_Bullish_Div", False),
            "OBV_Bearish_Div": latest.get("OBV_Bearish_Div", False),
            "Pattern": latest.get("Pattern", "None"),
            "Chandelier_Long": latest.get("Chandelier_Long", float("nan")),
            "Chandelier_Short": latest.get("Chandelier_Short", float("nan")),
            "Market_Regime": latest.get("Market_Regime", "Ranging"),
            "Stoch_Bullish_Cross": latest.get("Stoch_Bullish_Cross", False),
            "Stoch_Bearish_Cross": latest.get("Stoch_Bearish_Cross", False),
        }
