import pytest
import pandas as pd
import numpy as np
from crypto_momentum.optimizer import WalkForwardOptimizer


@pytest.fixture
def sample_data():
    dates = pd.date_range(start="1/1/2023", periods=150)
    data = pd.DataFrame(
        {
            "Open": np.random.rand(150) * 100 + 20000,
            "High": np.random.rand(150) * 100 + 20100,
            "Low": np.random.rand(150) * 100 + 19900,
            "Close": np.random.rand(150) * 100 + 20050,
            "Volume": np.random.rand(150) * 1000,
        },
        index=dates,
    )
    # Add required indicators to avoid errors in signal generator
    data["RSI_14"] = np.random.rand(150) * 100
    data["MACD"] = np.random.randn(150)
    data["MACD_Signal"] = np.random.randn(150)
    data["SMA_20"] = data["Close"].rolling(20).mean().bfill()
    data["SMA_50"] = data["Close"].rolling(50).mean().bfill()
    data["ATR_14"] = np.random.rand(150) * 50
    return data


def test_wfo_init(sample_data):
    wfo = WalkForwardOptimizer(data=sample_data, n_splits=3)
    assert wfo.n_splits == 3
    assert wfo.initial_balance == 10000.0


def test_generate_param_combinations(sample_data):
    wfo = WalkForwardOptimizer(data=sample_data)
    # Modify grid to make it smaller for tests
    wfo.param_grid = {
        "rsi_buy_min": [30],
        "rsi_buy_max": [70],
        "rsi_sell_min": [30],
        "rsi_sell_max": [60],
        "atr_sl_multiplier": [1.5],
        "atr_tp_multiplier": [3.0],
    }
    combinations = wfo._generate_param_combinations()
    assert isinstance(combinations, list)
    assert len(combinations) > 0
    assert "rsi_buy_min" in combinations[0]

    # Test valid filter
    wfo.param_grid = {
        "rsi_buy_min": [70],
        "rsi_buy_max": [30],
        "rsi_sell_min": [30],
        "rsi_sell_max": [60],
        "atr_sl_multiplier": [1.5],
        "atr_tp_multiplier": [3.0],
    }
    combinations_invalid = wfo._generate_param_combinations()
    assert len(combinations_invalid) == 0


def test_run_optimization(sample_data):
    wfo = WalkForwardOptimizer(data=sample_data, n_splits=2)
    # Reduce grid space for speed
    wfo.param_grid = {
        "rsi_buy_min": [30],
        "rsi_buy_max": [70],
        "rsi_sell_min": [30],
        "rsi_sell_max": [60],
        "atr_sl_multiplier": [1.5],
        "atr_tp_multiplier": [3.0],
    }
    results = wfo.run_optimization()
    assert "Initial Balance" in results
    assert "OOS Return %" in results
    assert "Window Results" in results
    assert len(results["Window Results"]) == 2


def test_run_optimization_insufficient_data():
    wfo = WalkForwardOptimizer(data=pd.DataFrame({"Close": [1, 2, 3]}))
    results = wfo.run_optimization()
    assert results == {}
