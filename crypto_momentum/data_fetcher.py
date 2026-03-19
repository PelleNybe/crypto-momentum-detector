import yfinance as yf
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataFetcher:
    def __init__(self, ticker_symbol: str = "BTC-USD"):
        """
        Initialize the DataFetcher with a specific cryptocurrency ticker.
        yfinance uses symbols like 'BTC-USD', 'ETH-USD'.
        """
        self.ticker_symbol = ticker_symbol

    def fetch_historical_data(self, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
        """
        Fetches historical market data for the initialized ticker.

        Args:
            period (str): The duration for which data is needed (e.g., '1mo', '3mo', '6mo', '1y').
            interval (str): The frequency of data (e.g., '1h', '1d', '1wk').

        Returns:
            pd.DataFrame: A pandas DataFrame containing 'Open', 'High', 'Low', 'Close', 'Volume'.
                          Returns empty DataFrame if fetching fails.
        """
        logger.info(f"Fetching {period} of data with {interval} interval for {self.ticker_symbol}")
        try:
            ticker = yf.Ticker(self.ticker_symbol)
            df = ticker.history(period=period, interval=interval)

            if df.empty:
                logger.warning(f"No data returned for {self.ticker_symbol}.")
                return pd.DataFrame()

            # Select necessary columns to standardize output
            if all(col in df.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume']):
                return df[['Open', 'High', 'Low', 'Close', 'Volume']]
            else:
                logger.error("Required columns missing from fetched data.")
                return pd.DataFrame()

        except Exception as e:
            logger.error(f"Error fetching data for {self.ticker_symbol}: {e}")
            return pd.DataFrame()
