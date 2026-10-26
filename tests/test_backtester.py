import pytest
import pandas as pd
from crypto_momentum.backtester import Backtester


@pytest.fixture
def mock_data():
    data = {
        "Close": [100.0, 110.0, 120.0, 115.0, 105.0],
        "Signal": ["HOLD", "BUY", "HOLD", "SELL", "HOLD"],
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

    assert "Initial Balance" in results
    assert "Final Balance" in results
    assert "Return %" in results
    assert "Max Drawdown %" in results
    assert "Win Rate %" in results
    assert "Total Trades" in results

    # We should have a positive return due to price going from 110 to 115
    assert results["Final Balance"] > 900.0  # Allow for fees and slippage


def test_backtester_empty_data():
    bt = Backtester(pd.DataFrame())
    results = bt.run()
    assert results == {}


def test_backtester_trade_return_with_fees():
    # Buy at 100, Sell at 100.2
    # Gain is 0.2%, but fee is 0.1% per trade + slippage 0.05% per trade
    # Buy execution: 100 * (1 + 0.0005) = 100.05
    # Fee: 100.05 * 0.001 = 0.10005
    # Sell execution: 100.2 * (1 - 0.0005) = 100.1499
    # Fee: 100.1499 * 0.001 = 0.1001499
    # We expect a net loss.
    data = {
        "Close": [100.0, 100.0, 100.2, 100.2],
        "Signal": ["HOLD", "BUY", "SELL", "HOLD"],
    }
    df = pd.DataFrame(data)
    bt = Backtester(df, initial_balance=1000.0, fee_rate=0.001, slippage=0.0005)
    results = bt.run()

    assert results["Total Trades"] == 1
    # Trade should be a loss, meaning Win Rate % should be 0.0
    assert results["Win Rate %"] == 0.0
    assert results["Trade Log"][0]["Return %"] < 0
