import pytest
import pandas as pd
import numpy as np
from crypto_momentum.indicators import MomentumIndicators

@pytest.fixture
def sample_data():
    dates = pd.date_range('2023-01-01', periods=100)
    data = {
        'Open': np.random.rand(100) * 100,
        'High': np.random.rand(100) * 110,
        'Low': np.random.rand(100) * 90,
        'Close': np.random.rand(100) * 100 + np.linspace(0, 50, 100),  # Upward trend
        'Volume': np.random.rand(100) * 1000
    }
    return pd.DataFrame(data, index=dates)

@pytest.fixture
def htf_data():
    dates = pd.date_range('2023-01-01', periods=20, freq='W')
    data = {
        'Open': np.random.rand(20) * 100,
        'High': np.random.rand(20) * 110,
        'Low': np.random.rand(20) * 90,
        'Close': np.random.rand(20) * 100 + np.linspace(0, 50, 20),
        'Volume': np.random.rand(20) * 1000
    }
    return pd.DataFrame(data, index=dates)

def test_indicators_calculation(sample_data):
    indicators = MomentumIndicators(sample_data)
    result = indicators.calculate_all()

    expected_cols = ['RSI_14', 'MACD', 'MACD_Signal', 'SMA_20', 'SMA_50', 'EMA_20', 'ATR_14', 'BB_High', 'BB_Low', 'HTF_Trend']
    for col in expected_cols:
        assert col in result.columns

def test_indicators_with_empty_data():
    indicators = MomentumIndicators(pd.DataFrame())
    result = indicators.calculate_all()
    assert result.empty

def test_indicators_with_htf(sample_data, htf_data):
    indicators = MomentumIndicators(sample_data, htf_data=htf_data)
    result = indicators.calculate_all()
    assert 'HTF_Trend' in result.columns
