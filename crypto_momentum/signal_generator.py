import pandas as pd

class SignalGenerator:
    def __init__(self, data: pd.DataFrame, rsi_buy_min: int = 40, rsi_buy_max: int = 70,
                 rsi_sell_min: int = 30, rsi_sell_max: int = 60, rsi_strong_buy: int = 30, rsi_strong_sell: int = 70):
        """
        Initializes the SignalGenerator with data containing momentum indicators.

        Args:
            data (pd.DataFrame): Dataframe that should include 'RSI_14', 'MACD', 'MACD_Signal',
                                 'SMA_20', 'SMA_50', 'EMA_20', 'EMA_50', 'ATR_14' and 'Close'.
            rsi_buy_min (int): Minimum RSI for a regular buy signal.
            rsi_buy_max (int): Maximum RSI for a regular buy signal.
            rsi_sell_min (int): Minimum RSI for a regular sell signal.
            rsi_sell_max (int): Maximum RSI for a regular sell signal.
            rsi_strong_buy (int): RSI threshold for a strong buy signal (below this).
            rsi_strong_sell (int): RSI threshold for a strong sell signal (above this).
        """
        self.data = data
        self.rsi_buy_min = rsi_buy_min
        self.rsi_buy_max = rsi_buy_max
        self.rsi_sell_min = rsi_sell_min
        self.rsi_sell_max = rsi_sell_max
        self.rsi_strong_buy = rsi_strong_buy
        self.rsi_strong_sell = rsi_strong_sell

    def generate_signals(self) -> pd.DataFrame:
        """
        Generates trading signals based on predefined momentum strategies.
        Returns 'BUY', 'SELL', or 'HOLD'.

        Returns:
            pd.DataFrame: A copy of input DataFrame with an additional 'Signal' column.
        """
        if self.data is None or self.data.empty:
            return pd.DataFrame()

        df = self.data.copy()

        required_cols = ['RSI_14', 'MACD', 'MACD_Signal', 'SMA_20', 'SMA_50', 'EMA_20', 'EMA_50', 'ATR_14', 'Close', 'BB_High', 'BB_Low']
        if not all(col in df.columns for col in required_cols):
            # If indicators are missing, default to HOLD
            df['Signal'] = 'HOLD'
            return df

        # Filter out rows where moving averages aren't available yet
        valid_mask = df['SMA_50'].notna()

        rsi = df['RSI_14']
        macd = df['MACD']
        macd_signal = df['MACD_Signal']
        close = df['Close']
        sma_20 = df['SMA_20']
        ema_20 = df['EMA_20']
        bb_low = df['BB_Low']
        bb_high = df['BB_High']

        is_bullish = (rsi > self.rsi_buy_min) & (rsi < self.rsi_buy_max) & (macd > macd_signal) & (close > ema_20)
        is_bearish = (rsi < self.rsi_sell_max) & (rsi > self.rsi_sell_min) & (macd < macd_signal) & (close < ema_20)

        strong_buy_cond = (rsi < self.rsi_strong_buy) & (macd > macd_signal) & (close < bb_low)
        strong_sell_cond = (rsi > self.rsi_strong_sell) & (macd < macd_signal) & (close > bb_high)

        # Initialize all signals as 'HOLD'
        df['Signal'] = 'HOLD'

        # We apply conditions
        df.loc[valid_mask & is_bullish, 'Signal'] = 'BUY'
        df.loc[valid_mask & is_bearish, 'Signal'] = 'SELL'

        # Extreme Oversold/Overbought overrides
        df.loc[valid_mask & strong_buy_cond, 'Signal'] = 'STRONG BUY'
        df.loc[valid_mask & strong_sell_cond, 'Signal'] = 'STRONG SELL'

        return df

    def get_latest_signal(self) -> dict:
        """
        Retrieves the most recent signal and associated metrics.

        Returns:
            dict: Dictionary with latest date, price, RSI, MACD status, and signal.
                  Returns empty dict if data is insufficient.
        """
        df_with_signals = self.generate_signals()

        if df_with_signals.empty or 'Signal' not in df_with_signals.columns:
            return {}

        latest = df_with_signals.iloc[-1]

        # Format the date if index is datetime
        date_str = str(df_with_signals.index[-1].date()) if hasattr(df_with_signals.index[-1], 'date') else str(df_with_signals.index[-1])

        return {
            'Date': date_str,
            'Price': latest['Close'],
            'RSI': latest['RSI_14'],
            'MACD': latest['MACD'],
            'MACD_Signal': latest['MACD_Signal'],
            'SMA_20': latest['SMA_20'],
            'SMA_50': latest['SMA_50'],
            'EMA_20': latest.get('EMA_20', 0),
            'EMA_50': latest.get('EMA_50', 0),
            'ATR_14': latest.get('ATR_14', 0),
            'BB_High': latest['BB_High'],
            'BB_Low': latest['BB_Low'],
            'Action': latest['Signal']
        }
