import pandas as pd

class SignalGenerator:
    def __init__(self, data: pd.DataFrame):
        """
        Initializes the SignalGenerator with data containing momentum indicators.

        Args:
            data (pd.DataFrame): Dataframe that should include 'RSI_14', 'MACD', 'MACD_Signal',
                                 'SMA_20', 'SMA_50' and 'Close'.
        """
        self.data = data

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

        required_cols = ['RSI_14', 'MACD', 'MACD_Signal', 'SMA_20', 'SMA_50', 'Close', 'BB_High', 'BB_Low']
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
        bb_low = df['BB_Low']
        bb_high = df['BB_High']

        is_bullish = (rsi > 40) & (rsi < 70) & (macd > macd_signal) & (close > sma_20)
        is_bearish = (rsi < 60) & (rsi > 30) & (macd < macd_signal) & (close < sma_20)

        strong_buy_cond = (rsi < 30) & (macd > macd_signal) & (close < bb_low)
        strong_sell_cond = (rsi > 70) & (macd < macd_signal) & (close > bb_high)

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
            'BB_High': latest['BB_High'],
            'BB_Low': latest['BB_Low'],
            'Action': latest['Signal']
        }
