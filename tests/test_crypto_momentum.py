import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock

from crypto_momentum.data_fetcher import DataFetcher
from crypto_momentum.indicators import MomentumIndicators
from crypto_momentum.signal_generator import SignalGenerator

@pytest.fixture
def sample_data():
    dates = pd.date_range(start='1/1/2023', periods=100)
    data = pd.DataFrame({
        'Open': np.random.rand(100) * 100 + 20000,
        'High': np.random.rand(100) * 100 + 20100,
        'Low': np.random.rand(100) * 100 + 19900,
        'Close': np.random.rand(100) * 100 + 20050,
        'Volume': np.random.rand(100) * 1000
    }, index=dates)
    return data

def test_data_fetcher_init():
    fetcher = DataFetcher("ETH-USD")
    assert fetcher.ticker_symbol == "ETH-USD"

@patch("crypto_momentum.data_fetcher.yf.Ticker")
def test_data_fetcher_fetch_historical_data(mock_ticker, sample_data):
    # Setup mock to return sample_data when history() is called
    mock_ticker_instance = MagicMock()
    mock_ticker_instance.history.return_value = sample_data
    mock_ticker.return_value = mock_ticker_instance

    fetcher = DataFetcher("BTC-USD")
    df = fetcher.fetch_historical_data(period="5d", interval="1d")

    assert not df.empty
    assert all(col in df.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume'])
    mock_ticker.assert_called_once_with("BTC-USD")
    mock_ticker_instance.history.assert_called_once_with(period="5d", interval="1d")

def test_indicators_calculate_all(sample_data):
    indicators = MomentumIndicators(sample_data)
    df_with_indicators = indicators.calculate_all()

    assert 'RSI_14' in df_with_indicators.columns
    assert 'MACD' in df_with_indicators.columns
    assert 'MACD_Signal' in df_with_indicators.columns
    assert 'SMA_20' in df_with_indicators.columns
    assert 'SMA_50' in df_with_indicators.columns

def test_signal_generator_generate_signals(sample_data):
    indicators = MomentumIndicators(sample_data)
    df_with_indicators = indicators.calculate_all()

    generator = SignalGenerator(df_with_indicators)
    df_with_signals = generator.generate_signals()

    assert 'Signal' in df_with_signals.columns

def test_signal_generator_get_latest_signal(sample_data):
    indicators = MomentumIndicators(sample_data)
    df_with_indicators = indicators.calculate_all()

    generator = SignalGenerator(df_with_indicators)
    latest = generator.get_latest_signal()

    assert isinstance(latest, dict)
    assert 'Action' in latest
    assert latest['Action'] in ['BUY', 'SELL', 'HOLD', 'STRONG BUY', 'STRONG SELL']
