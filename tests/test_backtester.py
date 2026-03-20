import pytest
import pandas as pd
from crypto_momentum.backtester import Backtester

def test_backtester_run():
    # Create simple test data
    data = pd.DataFrame({
        'Close': [100, 110, 120, 115, 130],
        'Signal': ['HOLD', 'BUY', 'HOLD', 'SELL', 'HOLD']
    })

    # Initial balance 10000
    # Day 1: HOLD
    # Day 2: BUY at 110. Holdings = 10000 / 110 = 90.909
    # Day 3: HOLD
    # Day 4: SELL at 115. Balance = 90.909 * 115 = 10454.54
    # Day 5: HOLD
    # Final Balance = 10454.54
    # Return = 4.545%

    bt = Backtester(data, initial_balance=10000)
    results = bt.run()

    assert results is not None
    assert 'Initial Balance' in results
    assert 'Final Balance' in results
    assert 'Return %' in results

    assert results['Initial Balance'] == 10000
    assert abs(results['Final Balance'] - 10454.54) < 0.1
    assert abs(results['Return %'] - 4.545) < 0.1

def test_backtester_no_signals():
    data = pd.DataFrame({
        'Close': [100, 110, 120, 115, 130],
        'Signal': ['HOLD', 'HOLD', 'HOLD', 'HOLD', 'HOLD']
    })

    bt = Backtester(data, initial_balance=10000)
    results = bt.run()

    assert results['Final Balance'] == 10000
    assert results['Return %'] == 0.0

def test_backtester_invalid_data():
    data = pd.DataFrame({'Close': [100, 110]})
    bt = Backtester(data)
    results = bt.run()
    assert results == {}
