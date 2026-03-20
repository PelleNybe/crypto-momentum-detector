import pytest
import pandas as pd
from crypto_momentum.backtester import Backtester

@pytest.fixture
def mock_data():
    data = {
        'Close': [100.0, 110.0, 120.0, 115.0, 105.0],
        'Signal': ['HOLD', 'BUY', 'HOLD', 'SELL', 'HOLD']
    }
    return pd.DataFrame(data)

def test_backtester_initialization(mock_data):
    bt = Backtester(mock_data)
    assert bt.initial_balance == 10000.0
    assert bt.fee_rate == 0.001
    assert bt.slippage == 0.0005

def test_backtester_run(mock_data):
    # Buy at 110, Sell at 115
    bt = Backtester(mock_data, initial_balance=1000.0)
    results = bt.run()

    assert 'Initial Balance' in results
    assert 'Final Balance' in results
    assert 'Return %' in results
    assert 'Max Drawdown %' in results
    assert 'Win Rate %' in results
    assert 'Total Trades' in results

    # We should have a positive return due to price going from 110 to 115
    assert results['Final Balance'] > 900.0  # Allow for fees and slippage

def test_backtester_empty_data():
    bt = Backtester(pd.DataFrame())
    results = bt.run()
    assert results == {}
