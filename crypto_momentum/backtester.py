import pandas as pd
import logging
import numpy as np

logger = logging.getLogger(__name__)


class Backtester:
    def __init__(
        self,
        data: pd.DataFrame,
        initial_balance: float = 10000.0,
        fee_rate: float = 0.001,
        slippage: float = 0.0005,
        position_size: float = 1.0,
        mc_simulations: int = 1000,
    ):
        """
        Initializes the Backtester with Monte Carlo capabilities.
        """
        self.data = data
        self.initial_balance = initial_balance
        self.fee_rate = fee_rate
        self.slippage = slippage
        self.position_size = position_size
        self.mc_simulations = mc_simulations

    def _run_monte_carlo(self, trades: list) -> dict:
        """
        Runs Monte Carlo simulations by resampling the historical trades.
        """
        if not trades or len(trades) < 5:
            return {"MC Median Return %": 0.0, "Risk of Ruin %": 0.0}

        ruin_threshold = 0.8  # 20% drawdown limit

        # Vectorized Monte Carlo simulation
        # Create a matrix of resampled trades: shape (mc_simulations, len(trades))
        sim_trades_mat = np.random.choice(
            trades, size=(self.mc_simulations, len(trades)), replace=True
        )

        # Calculate step multipliers based on position size
        multipliers = 1 + self.position_size * sim_trades_mat

        # Calculate balance paths using cumulative product
        balance_paths = self.initial_balance * np.cumprod(multipliers, axis=1)

        # Prepend initial balance to properly calculate max drawdowns from the start
        full_paths = np.insert(balance_paths, 0, self.initial_balance, axis=1)

        # Calculate running maximums
        running_max = np.maximum.accumulate(full_paths, axis=1)

        # Calculate drawdowns at each step
        drawdowns = full_paths / running_max

        # Find paths that hit the ruin threshold
        ruin_mask = drawdowns < ruin_threshold
        ruins = np.any(ruin_mask, axis=1)
        ruin_count = np.sum(ruins)

        # Find the first index where ruin occurs for each path
        ruin_indices = np.argmax(ruin_mask, axis=1)

        # Final balances are normally the last element, but if ruin occurred, it's the balance at ruin
        final_balances = full_paths[:, -1].copy()
        if ruin_count > 0:
            ruined_sims = np.where(ruins)[0]
            final_balances[ruins] = full_paths[ruined_sims, ruin_indices[ruins]]

        # Calculate return percentage
        sim_returns_new = (
            (final_balances - self.initial_balance) / self.initial_balance
        ) * 100

        median_return = float(np.median(sim_returns_new))
        risk_of_ruin = float((ruin_count / self.mc_simulations) * 100)

        return {"MC Median Return %": median_return, "Risk of Ruin %": risk_of_ruin}

    def run(self) -> dict:
        """
        Simulates trading based on the 'Signal' column.
        """
        if (
            self.data is None
            or self.data.empty
            or "Signal" not in self.data.columns
            or "Close" not in self.data.columns
        ):
            logger.error("Data must contain 'Signal' and 'Close' columns to backtest.")
            return {}

        balance = self.initial_balance
        crypto_holdings = 0.0

        trades = []
        trade_log = []
        entry_price = 0.0
        stop_loss = 0.0
        take_profit = 0.0
        equity_curve = []

        # Risk management: Risk 2% of capital per trade
        risk_per_trade = 0.02

        has_high = "High" in self.data.columns
        has_low = "Low" in self.data.columns
        has_stop_loss = "Stop_Loss" in self.data.columns
        has_take_profit = "Take_Profit" in self.data.columns

        # Pre-extract numpy arrays for critical fast paths where possible or use itertuples
        # itertuples is fast, but getattr is slow.
        # OPTIMIZATION: Replacing itertuples with numpy array zipping. ~2x performance speedup.
        # OPTIMIZATION: Map string signals to integers before the hot loop.
        signal_map = {
            "BUY": 1,
            "STRONG BUY": 1,
            "SELL": -1,
            "STRONG SELL": -1,
            "HOLD": 0,
        }
        _indexes = self.data.index.values
        _signals = np.array([signal_map.get(s, 0) for s in self.data["Signal"].values])
        _closes = self.data["Close"].values
        _highs = self.data["High"].values if has_high else _closes
        _lows = self.data["Low"].values if has_low else _closes
        _sls = self.data["Stop_Loss"].values if has_stop_loss else _closes * 0.95
        _tps = self.data["Take_Profit"].values if has_take_profit else _closes * 1.10

        for index, signal, price, high, low, sl_val, tp_val in zip(
            _indexes, _signals, _closes, _highs, _lows, _sls, _tps
        ):

            if pd.isna(price):
                equity_curve.append((index, balance))
                continue

            # Check if SL or TP is hit before evaluating new signals
            if crypto_holdings > 0 and entry_price > 0:
                hit_sl = low <= stop_loss
                hit_tp = high >= take_profit

                if hit_sl or hit_tp:
                    exit_price = stop_loss if hit_sl else take_profit

                    execution_price = exit_price * (1 - self.slippage)
                    revenue = crypto_holdings * execution_price
                    fee = revenue * self.fee_rate
                    net_revenue = revenue - fee

                    trade_return = (execution_price - entry_price) / entry_price
                    trades.append(trade_return)

                    trade_log.append(
                        {
                            "Exit Date": index,
                            "Type": "SL Hit" if hit_sl else "TP Hit",
                            "Entry Price": entry_price,
                            "Exit Price": execution_price,
                            "Return %": trade_return * 100,
                        }
                    )

                    balance += net_revenue
                    crypto_holdings = 0.0
                    entry_price = 0.0
                    stop_loss = 0.0
                    take_profit = 0.0

                    equity_curve.append((index, balance))
                    continue

            # Process new signals
            if signal == 1 and balance > 0 and crypto_holdings == 0:
                sl_price = sl_val
                tp_price = tp_val

                if pd.isna(sl_price) or sl_price >= price:
                    sl_price = price * 0.95
                if pd.isna(tp_price) or tp_price <= price:
                    tp_price = price * 1.10

                risk_amount = balance * risk_per_trade
                price_risk = price - sl_price

                if price_risk > 0:
                    position_size_usd = min(balance, risk_amount / (price_risk / price))
                else:
                    position_size_usd = balance * self.position_size  # Fallback

                if position_size_usd > 0:
                    execution_price = price * (1 + self.slippage)
                    crypto_bought = position_size_usd / execution_price
                    fee = crypto_bought * execution_price * self.fee_rate

                    crypto_holdings += crypto_bought - (fee / execution_price)
                    balance -= position_size_usd

                    entry_price = execution_price
                    stop_loss = sl_price
                    take_profit = tp_price

            elif signal == -1 and crypto_holdings > 0:
                execution_price = price * (1 - self.slippage)
                revenue = crypto_holdings * execution_price
                fee = revenue * self.fee_rate
                net_revenue = revenue - fee

                if entry_price > 0:
                    trade_return = (execution_price - entry_price) / entry_price
                    trades.append(trade_return)

                    trade_log.append(
                        {
                            "Exit Date": index,
                            "Type": "Signal Exit",
                            "Entry Price": entry_price,
                            "Exit Price": execution_price,
                            "Return %": trade_return * 100,
                        }
                    )

                balance += net_revenue
                crypto_holdings = 0.0
                entry_price = 0.0
                stop_loss = 0.0
                take_profit = 0.0

            # Performance Optimization: Construct dictionary directly instead of tuple
            # to avoid the later O(n) conversion loop
            equity_curve.append(
                {"Date": index, "Equity": balance + (crypto_holdings * price)}
            )

        final_price = _closes[-1] if len(_closes) > 0 else self.data["Close"].iloc[-1]
        final_balance = balance + (crypto_holdings * final_price)

        return_pct = (
            (final_balance - self.initial_balance) / self.initial_balance
        ) * 100

        if equity_curve:
            equity_curve_dicts = equity_curve

            # Fast numpy-based calculations for drawdown and metrics
            equity_arr = np.array([e["Equity"] for e in equity_curve])
            peak = np.maximum.accumulate(equity_arr)
            drawdown = (equity_arr - peak) / peak
            max_drawdown = drawdown.min() * 100

            # Daily returns
            returns_arr = np.diff(equity_arr) / equity_arr[:-1]

            if len(returns_arr) > 0 and returns_arr.std() != 0:
                sharpe_ratio = (returns_arr.mean() / returns_arr.std()) * np.sqrt(365)
                downside = returns_arr[returns_arr < 0]
                if len(downside) > 0 and downside.std() != 0:
                    sortino_ratio = (returns_arr.mean() / downside.std()) * np.sqrt(365)
                else:
                    sortino_ratio = 0.0
            else:
                sharpe_ratio = 0.0
                sortino_ratio = 0.0

        else:
            max_drawdown = 0.0
            sharpe_ratio = 0.0
            sortino_ratio = 0.0

        winning_trades = [t for t in trades if t > 0]
        losing_trades = [t for t in trades if t < 0]
        win_rate = (len(winning_trades) / len(trades) * 100) if trades else 0.0

        # Profit Factor
        gross_profit = sum(winning_trades) if winning_trades else 0.0
        gross_loss = abs(sum(losing_trades)) if losing_trades else 0.0
        profit_factor = (
            (gross_profit / gross_loss)
            if gross_loss > 0
            else (float("inf") if gross_profit > 0 else 0.0)
        )

        # --- NEW WORLD CLASS FEATURE 4: Monte Carlo Analysis ---
        mc_results = self._run_monte_carlo(trades)

        return {
            "Initial Balance": self.initial_balance,
            "Final Balance": final_balance,
            "Return %": return_pct,
            "Max Drawdown %": max_drawdown,
            "Sharpe Ratio": sharpe_ratio,
            "Sortino Ratio": sortino_ratio,
            "Profit Factor": profit_factor,
            "Win Rate %": win_rate,
            "Total Trades": len(trades),
            "MC Median Return %": mc_results["MC Median Return %"],
            "Risk of Ruin %": mc_results["Risk of Ruin %"],
            "Equity Curve": equity_curve_dicts if equity_curve else [],
            "Trade Log": trade_log,
        }
