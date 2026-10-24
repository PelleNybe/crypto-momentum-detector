import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from crypto_momentum.ga_optimizer import GeneticOptimizer


@pytest.fixture
def sample_data():
    dates = pd.date_range(start="1/1/2023", periods=100)
    data = pd.DataFrame(
        {
            "Open": np.random.rand(100) * 100 + 20000,
            "High": np.random.rand(100) * 100 + 20100,
            "Low": np.random.rand(100) * 100 + 19900,
            "Close": np.random.rand(100) * 100 + 20050,
            "Volume": np.random.rand(100) * 1000,
        },
        index=dates,
    )
    # Add required indicators to avoid errors in signal generator
    data["RSI_14"] = np.random.rand(100) * 100
    data["MACD"] = np.random.randn(100)
    data["MACD_Signal"] = np.random.randn(100)
    data["SMA_20"] = data["Close"].rolling(20).mean().bfill()
    data["SMA_50"] = data["Close"].rolling(50).mean().bfill()
    data["ATR_14"] = np.random.rand(100) * 50
    return data


def test_ga_optimizer_init(sample_data):
    optimizer = GeneticOptimizer(data=sample_data, population_size=10, generations=2)
    assert optimizer.population_size == 10
    assert optimizer.generations == 2
    assert "rsi_buy_min" in optimizer.param_bounds


def test_create_random_individual(sample_data):
    optimizer = GeneticOptimizer(data=sample_data)
    ind = optimizer._create_random_individual()
    assert "rsi_buy_min" in ind
    assert "atr_sl_multiplier" in ind
    assert ind["rsi_buy_min"] < ind["rsi_buy_max"]
    assert ind["rsi_sell_min"] < ind["rsi_sell_max"]


def test_fitness(sample_data):
    optimizer = GeneticOptimizer(data=sample_data)
    ind = optimizer._create_random_individual()
    fitness = optimizer._fitness(ind)
    assert isinstance(fitness, float)


def test_crossover(sample_data):
    optimizer = GeneticOptimizer(data=sample_data)
    p1 = optimizer._create_random_individual()
    p2 = optimizer._create_random_individual()
    child = optimizer._crossover(p1, p2)
    assert child["rsi_buy_min"] < child["rsi_buy_max"]


def test_mutate(sample_data):
    optimizer = GeneticOptimizer(data=sample_data, mutation_rate=1.0)
    ind = optimizer._create_random_individual()
    mutated = optimizer._mutate(ind)
    assert mutated["rsi_buy_min"] < mutated["rsi_buy_max"]


def test_run_optimization(sample_data):
    # Use very small parameters for quick test execution
    optimizer = GeneticOptimizer(
        data=sample_data, population_size=4, generations=2, elite_size=1
    )
    results = optimizer.run_optimization()
    assert "best_parameters" in results
    assert "best_fitness" in results
    assert "history" in results
    assert "final_backtest" in results
    assert len(results["history"]) == 2


def test_run_optimization_insufficient_data():
    optimizer = GeneticOptimizer(data=pd.DataFrame({"Close": [1, 2, 3]}))
    results = optimizer.run_optimization()
    assert results == {}
