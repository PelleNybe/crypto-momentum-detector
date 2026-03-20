import pandas as pd
import logging

logger = logging.getLogger(__name__)

class Backtester:
    def __init__(self, data: pd.DataFrame, initial_balance: float = 10000.0):
        """
        Initializes the Backtester.

        Args:
            data (pd.DataFrame): Dataframe containing 'Close' and 'Signal' columns.
            initial_balance (float): Starting balance in USD.
        """
        self.data = data
        self.initial_balance = initial_balance

    def run(self) -> dict:
        """
        Simulates trading based on the 'Signal' column.

        Returns:
            dict: Performance metrics including initial balance, final balance, and return percentage.
        """
        if self.data is None or self.data.empty or 'Signal' not in self.data.columns or 'Close' not in self.data.columns:
            logger.error("Data must contain 'Signal' and 'Close' columns to backtest.")
            return {}

        balance = self.initial_balance
        crypto_holdings = 0.0

        for index, row in self.data.iterrows():
            signal = row['Signal']
            price = row['Close']

            if pd.isna(price) or pd.isna(signal):
                continue

            if signal in ['BUY', 'STRONG BUY']:
                # Buy as much as possible with current balance
                if balance > 0:
                    crypto_bought = balance / price
                    crypto_holdings += crypto_bought
                    balance = 0.0

            elif signal in ['SELL', 'STRONG SELL']:
                # Sell all holdings
                if crypto_holdings > 0:
                    balance += crypto_holdings * price
                    crypto_holdings = 0.0

        # Calculate final value (balance + value of any remaining crypto)
        final_price = self.data['Close'].iloc[-1]
        final_balance = balance + (crypto_holdings * final_price)

        return_pct = ((final_balance - self.initial_balance) / self.initial_balance) * 100

        return {
            'Initial Balance': self.initial_balance,
            'Final Balance': final_balance,
            'Return %': return_pct
        }
