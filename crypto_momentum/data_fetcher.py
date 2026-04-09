import yfinance as yf
import pandas as pd
import logging
import requests_cache
import os
import time
from datetime import datetime, timedelta
from crypto_momentum.mtf_utils import get_htf_interval, get_htf_period

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DataFetcher:
    def __init__(self, ticker_symbol: str = "BTC-USD", cache_dir: str = ".data_cache"):
        """
        Initialize the DataFetcher with a specific cryptocurrency ticker and file-based caching.
        """
        self.ticker_symbol = ticker_symbol
        self.cache_dir = cache_dir
        self.session = requests_cache.CachedSession(
            ".yfinance_cache", expire_after=3600
        )

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _get_cache_path(self, period: str, interval: str) -> str:
        return os.path.join(
            self.cache_dir, f"{self.ticker_symbol}_{period}_{interval}.parquet"
        )

    def clean_outliers(
        self, df: pd.DataFrame, window: int = 20, num_std: float = 4.0
    ) -> pd.DataFrame:
        """Removes significant outliers from the price data using a rolling z-score and interpolates them."""
        if df.empty or len(df) < window:
            return df

        import numpy as np

        df_clean = df.copy()
        for col in ["Open", "High", "Low", "Close"]:
            if col in df_clean.columns:
                rolling_mean = (
                    df_clean[col]
                    .rolling(window=window, min_periods=1, center=True)
                    .mean()
                )
                rolling_std = (
                    df_clean[col]
                    .rolling(window=window, min_periods=1, center=True)
                    .std()
                )

                # For the first few rows where std is 0 or NaN, fill with overall std
                rolling_std = rolling_std.bfill().fillna(df_clean[col].std())

                z_scores = np.abs((df_clean[col] - rolling_mean) / (rolling_std + 1e-9))

                # Mask outliers
                outlier_mask = z_scores > num_std
                if outlier_mask.any():
                    df_clean.loc[outlier_mask, col] = np.nan
                    df_clean[col] = df_clean[col].interpolate(
                        method="linear", limit_direction="both"
                    )

        return df_clean

    def fetch_historical_data(
        self, period: str = "6mo", interval: str = "1d", max_cache_age_hours: int = 1
    ) -> pd.DataFrame:
        """
        Fetches historical market data with file-based Parquet caching.
        """
        cache_path = self._get_cache_path(period, interval)

        # Check if cache exists and is fresh
        if os.path.exists(cache_path):
            file_mod_time = os.path.getmtime(cache_path)
            cache_age = datetime.now().timestamp() - file_mod_time

            if cache_age < max_cache_age_hours * 3600:
                logger.info(
                    f"Loading {period}/{interval} for {self.ticker_symbol} from local Parquet cache"
                )
                try:
                    df = pd.read_parquet(cache_path)
                    return df
                except Exception as e:
                    logger.warning(
                        f"Failed to load cache for {self.ticker_symbol}: {e}"
                    )

        logger.info(
            f"Fetching {period} of data with {interval} interval for {self.ticker_symbol} from API"
        )
        try:
            ticker = yf.Ticker(self.ticker_symbol)
            df = ticker.history(period=period, interval=interval)

            if df.empty:
                logger.warning(f"No data returned for {self.ticker_symbol}.")
                return pd.DataFrame()

            if all(
                col in df.columns for col in ["Open", "High", "Low", "Close", "Volume"]
            ):
                result_df = df[["Open", "High", "Low", "Close", "Volume"]]

                # Save to cache
                try:
                    result_df.to_parquet(cache_path)
                except Exception as e:
                    logger.warning(
                        f"Failed to write cache for {self.ticker_symbol}: {e}"
                    )

                result_df = self.clean_outliers(result_df)
                return result_df
            else:
                logger.error("Required columns missing from fetched data.")
                return pd.DataFrame()

        except Exception as e:
            logger.error(f"Error fetching data for {self.ticker_symbol}: {e}")
            return pd.DataFrame()

    def fetch_htf_data(
        self, period: str, interval: str, max_cache_age_hours: int = 1
    ) -> pd.DataFrame:
        """
        Fetches data for a higher timeframe with caching.
        """
        htf_interval = get_htf_interval(interval)
        htf_period = get_htf_period(period)

        if not htf_interval:
            logger.info(
                f"No higher timeframe mapping for {interval}, returning empty df for HTF"
            )
            return pd.DataFrame()

        cache_path = self._get_cache_path(htf_period, htf_interval)

        # Check cache
        if os.path.exists(cache_path):
            file_mod_time = os.path.getmtime(cache_path)
            cache_age = datetime.now().timestamp() - file_mod_time

            if cache_age < max_cache_age_hours * 3600:
                logger.info(
                    f"Loading HTF {htf_period}/{htf_interval} for {self.ticker_symbol} from cache"
                )
                try:
                    df = pd.read_parquet(cache_path)
                    return df
                except Exception as e:
                    logger.warning(
                        f"Failed to load HTF cache for {self.ticker_symbol}: {e}"
                    )

        logger.info(
            f"Fetching HTF data: {htf_period} with {htf_interval} for {self.ticker_symbol} from API"
        )
        try:
            ticker = yf.Ticker(self.ticker_symbol)
            df = ticker.history(period=htf_period, interval=htf_interval)

            if df.empty:
                return pd.DataFrame()

            if all(
                col in df.columns for col in ["Open", "High", "Low", "Close", "Volume"]
            ):
                result_df = df[["Open", "High", "Low", "Close", "Volume"]]
                try:
                    result_df.to_parquet(cache_path)
                except Exception as e:
                    logger.warning(
                        f"Failed to write HTF cache for {self.ticker_symbol}: {e}"
                    )
                result_df = self.clean_outliers(result_df)
                return result_df
            else:
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error fetching HTF data for {self.ticker_symbol}: {e}")
            return pd.DataFrame()
