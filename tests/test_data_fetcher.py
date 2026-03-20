import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
from crypto_momentum.data_fetcher import DataFetcher


@patch("crypto_momentum.data_fetcher.yf.Ticker")
def test_fetch_historical_data_success(mock_ticker):
    mock_df = pd.DataFrame(
        {
            "Open": [1, 2],
            "High": [2, 3],
            "Low": [1, 1],
            "Close": [2, 2],
            "Volume": [100, 200],
        }
    )
    mock_instance = MagicMock()
    mock_instance.history.return_value = mock_df
    mock_ticker.return_value = mock_instance

    fetcher = DataFetcher(cache_dir=".test_cache")
    result = fetcher.fetch_historical_data(max_cache_age_hours=0)  # force fetch

    assert not result.empty
    assert list(result.columns) == ["Open", "High", "Low", "Close", "Volume"]


@patch("crypto_momentum.data_fetcher.yf.Ticker")
def test_fetch_htf_data_success(mock_ticker):
    mock_df = pd.DataFrame(
        {"Open": [1], "High": [2], "Low": [1], "Close": [2], "Volume": [100]}
    )
    mock_instance = MagicMock()
    mock_instance.history.return_value = mock_df
    mock_ticker.return_value = mock_instance

    fetcher = DataFetcher(cache_dir=".test_cache")
    result = fetcher.fetch_htf_data(period="1mo", interval="1d", max_cache_age_hours=0)

    assert not result.empty
    assert list(result.columns) == ["Open", "High", "Low", "Close", "Volume"]
