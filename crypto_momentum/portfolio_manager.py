import pandas as pd
import numpy as np
from scipy.optimize import minimize
import logging

logger = logging.getLogger(__name__)


class MPTAllocator:
    def __init__(self, returns_data: pd.DataFrame, risk_free_rate: float = 0.02):
        """
        Initializes the allocator.
        :param returns_data: A DataFrame where each column is a ticker's daily return series, aligned by date.
        """
        self.returns = returns_data.dropna()
        self.risk_free_rate = risk_free_rate

    def _portfolio_annualised_performance(self, weights, mean_returns, cov_matrix):
        returns = np.sum(mean_returns * weights) * 365
        std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(365)
        return std, returns

    def _neg_sharpe_ratio(self, weights, mean_returns, cov_matrix, risk_free_rate):
        p_var, p_ret = self._portfolio_annualised_performance(
            weights, mean_returns, cov_matrix
        )
        if p_var == 0:
            return 0
        return -(p_ret - risk_free_rate) / p_var

    def optimize_portfolio(self) -> dict:
        """
        Finds the portfolio weights that maximize the Sharpe ratio.
        """
        if self.returns.empty or len(self.returns.columns) < 2:
            logger.warning("Not enough data or tickers to run MPT optimization.")
            return {}

        try:
            mean_returns = self.returns.mean()
            cov_matrix = self.returns.cov()
            num_assets = len(self.returns.columns)

            args = (mean_returns, cov_matrix, self.risk_free_rate)
            constraints = {"type": "eq", "fun": lambda x: np.sum(x) - 1}
            bounds = tuple((0.0, 1.0) for asset in range(num_assets))

            # Start with equal allocation
            initial_guess = num_assets * [
                1.0 / num_assets,
            ]

            result = minimize(
                self._neg_sharpe_ratio,
                initial_guess,
                args=args,
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
            )

            if not result.success:
                logger.warning(f"Optimization failed: {result.message}")
                return {}

            optimal_weights = result.x
            std, ret = self._portfolio_annualised_performance(
                optimal_weights, mean_returns, cov_matrix
            )
            sharpe = (ret - self.risk_free_rate) / std if std > 0 else 0

            allocation = {
                self.returns.columns[i]: float(optimal_weights[i])
                for i in range(num_assets)
            }

            # Clean up tiny weights
            allocation = {k: v for k, v in allocation.items() if v > 0.001}

            return {
                "weights": allocation,
                "expected_return_annual": float(ret),
                "expected_volatility_annual": float(std),
                "sharpe_ratio": float(sharpe),
            }

        except Exception as e:
            logger.error(f"Error in MPT optimization: {e}")
            return {}
