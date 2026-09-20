import numpy as np
import pandas as pd
from typing import Dict, List, Any
import logging
from sklearn.model_selection import TimeSeriesSplit
import itertools

from crypto_momentum.signal_generator import SignalGenerator
from crypto_momentum.backtester import Backtester
from crypto_momentum.indicators import MomentumIndicators

logger = logging.getLogger(__name__)


class WalkForwardOptimizer:
    def __init__(
        self,
        data: pd.DataFrame,
        initial_balance: float = 10000.0,
        risk_per_trade: float = 0.02,
        slippage: float = 0.001,
        fee_rate: float = 0.001,
        n_splits: int = 5,
        test_size_days: int = 30,  # approximate number of days for test set if not using TimeSeriesSplit purely
    ):
        self.data = data
        self.initial_balance = initial_balance
        self.risk_per_trade = risk_per_trade
        self.slippage = slippage
        self.fee_rate = fee_rate
        self.n_splits = n_splits

        # Parameter grid for grid search optimization
        self.param_grid = {
            "rsi_buy_min": [30, 40],
            "rsi_buy_max": [60, 70],
            "rsi_sell_min": [30, 40],
            "rsi_sell_max": [60, 70],
            "atr_sl_multiplier": [1.5, 2.0],
            "atr_tp_multiplier": [2.0, 3.0],
        }

    def _generate_param_combinations(self) -> List[Dict[str, Any]]:
        keys, values = zip(*self.param_grid.items())
        combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
        # Filter invalid combinations where min >= max
        valid_combinations = []
        for p in combinations:
            if (
                p["rsi_buy_min"] < p["rsi_buy_max"]
                and p["rsi_sell_min"] < p["rsi_sell_max"]
            ):
                valid_combinations.append(p)
        return valid_combinations

    def run_optimization(self) -> Dict[str, Any]:
        """
        Runs the Walk-Forward Optimization process.
        """
        if self.data is None or len(self.data) < 100:
            logger.error("Not enough data for Walk-Forward Optimization.")
            return {}

        logger.info(f"Starting Walk-Forward Optimization with {self.n_splits} splits.")

        tscv = TimeSeriesSplit(n_splits=self.n_splits)

        param_combinations = self._generate_param_combinations()

        window_results = []
        out_of_sample_equity_curve = []
        current_oos_balance = self.initial_balance

        overall_trade_log = []

        for i, (train_index, test_index) in enumerate(tscv.split(self.data)):
            train_data = self.data.iloc[train_index].copy()
            test_data = self.data.iloc[test_index].copy()

            logger.info(
                f"Window {i+1}/{self.n_splits}: Training on {len(train_data)} rows, Testing on {len(test_data)} rows"
            )

            # 1. Optimize on Training Set
            best_params = None
            best_fitness = -float("inf")

            for params in param_combinations:
                # Generate signals for train data with current params
                sg = SignalGenerator(
                    data=train_data,
                    rsi_buy_min=params["rsi_buy_min"],
                    rsi_buy_max=params["rsi_buy_max"],
                    rsi_sell_min=params["rsi_sell_min"],
                    rsi_sell_max=params["rsi_sell_max"],
                    atr_sl_multiplier=params["atr_sl_multiplier"],
                    atr_tp_multiplier=params["atr_tp_multiplier"],
                )
                train_signals = sg.generate_signals()

                # Backtest on train data
                bt = Backtester(
                    data=train_signals,
                    initial_balance=10000.0,  # Fixed for evaluation
                    risk_per_trade=self.risk_per_trade,
                    slippage=self.slippage,
                    fee_rate=self.fee_rate,
                    mc_simulations=0,  # Disable MC during inner optimization for speed
                )
                bt_results = bt.run()

                # Fitness function: Profit Factor or Return
                fitness = bt_results.get("Return %", -float("inf"))

                if fitness > best_fitness:
                    best_fitness = fitness
                    best_params = params

            if best_params is None:
                # Fallback to defaults
                best_params = {
                    "rsi_buy_min": 40,
                    "rsi_buy_max": 70,
                    "rsi_sell_min": 30,
                    "rsi_sell_max": 60,
                    "atr_sl_multiplier": 1.5,
                    "atr_tp_multiplier": 3.0,
                }

            logger.info(
                f"Best params for window {i+1}: {best_params} (Train Return: {best_fitness:.2f}%)"
            )

            # 2. Test on Out-of-Sample (Test) Set
            # Generate signals for test data with best params
            sg_test = SignalGenerator(
                data=test_data,
                rsi_buy_min=best_params["rsi_buy_min"],
                rsi_buy_max=best_params["rsi_buy_max"],
                rsi_sell_min=best_params["rsi_sell_min"],
                rsi_sell_max=best_params["rsi_sell_max"],
                atr_sl_multiplier=best_params["atr_sl_multiplier"],
                atr_tp_multiplier=best_params["atr_tp_multiplier"],
            )
            test_signals = sg_test.generate_signals()

            bt_test = Backtester(
                data=test_signals,
                initial_balance=current_oos_balance,
                risk_per_trade=self.risk_per_trade,
                slippage=self.slippage,
                fee_rate=self.fee_rate,
                mc_simulations=1000,  # Run MC on out of sample test
            )
            test_results = bt_test.run()

            # Record window results
            window_results.append(
                {
                    "Window": i + 1,
                    "Start Date": test_data.index[0],
                    "End Date": test_data.index[-1],
                    "Best Params": best_params,
                    "OOS Return %": test_results.get("Return %", 0),
                    "OOS Max Drawdown %": test_results.get("Max Drawdown %", 0),
                    "OOS Profit Factor": test_results.get("Profit Factor", 0),
                    "OOS Win Rate %": test_results.get("Win Rate %", 0),
                    "OOS Trades": test_results.get("Total Trades", 0),
                }
            )

            # Stitch equity curve
            eq_curve = test_results.get("Equity Curve", [])
            if eq_curve:
                # Adjust equity to continue from previous OOS balance
                out_of_sample_equity_curve.extend(eq_curve)
                current_oos_balance = eq_curve[-1]["Equity"]

            # Stitch trade log
            trade_log = test_results.get("Trade Log", [])
            overall_trade_log.extend(trade_log)

        # Calculate overall OOS metrics
        total_oos_return = (
            (current_oos_balance - self.initial_balance) / self.initial_balance
        ) * 100

        # Calculate OOS Max Drawdown
        oos_max_drawdown = 0.0
        oos_sharpe_ratio = 0.0

        if out_of_sample_equity_curve:
            equity_arr = np.array([e["Equity"] for e in out_of_sample_equity_curve])
            peak = np.maximum.accumulate(equity_arr)
            drawdown = (equity_arr - peak) / peak
            oos_max_drawdown = drawdown.min() * 100

            returns_arr = np.diff(equity_arr) / equity_arr[:-1]
            if len(returns_arr) > 0 and returns_arr.std() != 0:
                oos_sharpe_ratio = (returns_arr.mean() / returns_arr.std()) * np.sqrt(
                    365
                )

        # Overall trades metrics
        winning_trades = [t for t in overall_trade_log if t.get("Return %", 0) > 0]
        losing_trades = [t for t in overall_trade_log if t.get("Return %", 0) < 0]
        total_trades = len(overall_trade_log)

        oos_win_rate = (
            (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0.0
        )

        gross_profit = sum(
            [
                t.get("Return %", 0) / 100 * t.get("Entry Price", 0)
                for t in winning_trades
            ]
        )  # Approx for profit factor
        gross_loss = abs(
            sum(
                [
                    t.get("Return %", 0) / 100 * t.get("Entry Price", 0)
                    for t in losing_trades
                ]
            )
        )
        oos_profit_factor = (
            (gross_profit / gross_loss)
            if gross_loss > 0
            else (float("inf") if gross_profit > 0 else 0.0)
        )

        return {
            "Initial Balance": self.initial_balance,
            "Final Balance": current_oos_balance,
            "OOS Return %": total_oos_return,
            "OOS Max Drawdown %": oos_max_drawdown,
            "OOS Sharpe Ratio": oos_sharpe_ratio,
            "OOS Profit Factor": oos_profit_factor,
            "OOS Win Rate %": oos_win_rate,
            "Total Trades": total_trades,
            "Window Results": window_results,
            "OOS Equity Curve": out_of_sample_equity_curve,
            "OOS Trade Log": overall_trade_log,
        }
