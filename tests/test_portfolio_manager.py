import pytest
import pandas as pd
import numpy as np
from crypto_momentum.portfolio_manager import MPTAllocator


@pytest.fixture
def returns_data():
    dates = pd.date_range(start="1/1/2023", periods=100)
    data = pd.DataFrame(
        {
            "BTC-USD": np.random.normal(0.001, 0.02, 100),
            "ETH-USD": np.random.normal(0.002, 0.03, 100),
            "SOL-USD": np.random.normal(0.003, 0.04, 100),
        },
        index=dates,
    )
    return data


def test_mpt_allocator_init(returns_data):
    allocator = MPTAllocator(returns_data=returns_data)
    assert not allocator.returns.empty
    assert allocator.risk_free_rate == 0.02


def test_portfolio_annualised_performance(returns_data):
    allocator = MPTAllocator(returns_data=returns_data)
    weights = np.array([0.4, 0.4, 0.2])
    mean_returns = returns_data.mean()
    cov_matrix = returns_data.cov()
    std, ret = allocator._portfolio_annualised_performance(
        weights, mean_returns, cov_matrix
    )
    assert isinstance(std, float)
    assert isinstance(ret, float)


def test_neg_sharpe_ratio(returns_data):
    allocator = MPTAllocator(returns_data=returns_data)
    weights = np.array([0.4, 0.4, 0.2])
    mean_returns = returns_data.mean()
    cov_matrix = returns_data.cov()
    neg_sharpe = allocator._neg_sharpe_ratio(weights, mean_returns, cov_matrix, 0.02)
    assert isinstance(neg_sharpe, float)


def test_optimize_portfolio(returns_data):
    allocator = MPTAllocator(returns_data=returns_data)
    result = allocator.optimize_portfolio()
    assert "weights" in result
    assert "expected_return_annual" in result
    assert "expected_volatility_annual" in result
    assert "sharpe_ratio" in result


def test_optimize_portfolio_insufficient_data():
    allocator = MPTAllocator(returns_data=pd.DataFrame({"BTC-USD": [0.01, 0.02]}))
    result = allocator.optimize_portfolio()
    assert result == {}


def test_optimize_portfolio_exception_handling():
    allocator = MPTAllocator(returns_data=pd.DataFrame({"A": [1], "B": [2]}))
    allocator.returns.cov = lambda: None  # Force exception
    result = allocator.optimize_portfolio()
    assert result == {}
