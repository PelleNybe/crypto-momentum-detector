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
        signals = []

        required_cols = ['RSI_14', 'MACD', 'MACD_Signal', 'SMA_20', 'SMA_50', 'Close']
        if not all(col in df.columns for col in required_cols):
            # If indicators are missing, default to HOLD
            df['Signal'] = 'HOLD'
            return df

        for i in range(len(df)):
            # Skip rows where moving averages aren't available yet
            if pd.isna(df['SMA_50'].iloc[i]):
                signals.append('HOLD')
                continue

            rsi = df['RSI_14'].iloc[i]
            macd = df['MACD'].iloc[i]
            macd_signal = df['MACD_Signal'].iloc[i]
            close = df['Close'].iloc[i]
            sma_20 = df['SMA_20'].iloc[i]
            sma_50 = df['SMA_50'].iloc[i]

            # Simplified Momentum Strategy Logic:

            # 1. Bullish conditions:
            # - RSI is recovering from oversold (RSI > 30) or showing strong momentum (RSI > 50)
            # - MACD crossed above Signal line (MACD > Signal)
            # - Short-term trend is up (Price > SMA 20 or SMA 20 > SMA 50)
            is_bullish = (rsi > 40 and rsi < 70) and (macd > macd_signal) and (close > sma_20)

            # 2. Bearish conditions:
            # - RSI is overbought (RSI > 70) or showing weak momentum (RSI < 50)
            # - MACD crossed below Signal line (MACD < Signal)
            # - Short-term trend is down (Price < SMA 20 or SMA 20 < SMA 50)
            is_bearish = (rsi < 60 and rsi > 30) and (macd < macd_signal) and (close < sma_20)

            # Extreme Oversold/Overbought overrides
            if rsi < 30 and macd > macd_signal:
                # Strong buy signal on reversal
                signals.append('STRONG BUY')
            elif rsi > 70 and macd < macd_signal:
                # Strong sell signal on reversal
                signals.append('STRONG SELL')
            elif is_bullish:
                signals.append('BUY')
            elif is_bearish:
                signals.append('SELL')
            else:
                signals.append('HOLD')

        df['Signal'] = signals
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
            'Action': latest['Signal']
        }
