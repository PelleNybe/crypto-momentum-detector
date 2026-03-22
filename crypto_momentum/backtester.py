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

        sim_returns = []
        ruin_count = 0
        ruin_threshold = 0.8  # 20% drawdown limit

        for _ in range(self.mc_simulations):
            # Resample with replacement
            sim_trades = np.random.choice(trades, size=len(trades), replace=True)

            sim_balance = self.initial_balance
            max_balance = sim_balance
            ruin = False

            for t_return in sim_trades:
                trade_amount = sim_balance * self.position_size
                net_profit = trade_amount * t_return
                sim_balance += net_profit

                if sim_balance > max_balance:
                    max_balance = sim_balance
                elif sim_balance < max_balance * ruin_threshold:
                    ruin = True
                    break  # hit max drawdown limit

            if ruin:
                ruin_count += 1

            sim_return_pct = (
                (sim_balance - self.initial_balance) / self.initial_balance
            ) * 100
            sim_returns.append(sim_return_pct)

        median_return = np.median(sim_returns)
        risk_of_ruin = (ruin_count / self.mc_simulations) * 100

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
        entry_price = 0.0
        equity_curve = []

        for index, row in self.data.iterrows():
            signal = row["Signal"]
            price = row["Close"]

            if pd.isna(price) or pd.isna(signal):
                current_value = (
                    balance + (crypto_holdings * price)
                    if not pd.isna(price)
                    else balance
                )
                equity_curve.append(current_value)
                continue

            if signal in ["BUY", "STRONG BUY"] and balance > 0:
                trade_amount = balance * self.position_size
                if trade_amount > 0:
                    execution_price = price * (1 + self.slippage)
                    crypto_bought = trade_amount / execution_price
                    fee = crypto_bought * execution_price * self.fee_rate

                    crypto_holdings += crypto_bought - (fee / execution_price)
                    balance -= trade_amount

                    if entry_price == 0.0:
                        entry_price = execution_price

            elif signal in ["SELL", "STRONG SELL"] and crypto_holdings > 0:
                execution_price = price * (1 - self.slippage)
                revenue = crypto_holdings * execution_price
                fee = revenue * self.fee_rate
                net_revenue = revenue - fee

                if entry_price > 0:
                    trade_return = (execution_price - entry_price) / entry_price
                    trades.append(trade_return)

                balance += net_revenue
                crypto_holdings = 0.0
                entry_price = 0.0

            current_value = balance + (crypto_holdings * price)
            equity_curve.append(current_value)

        final_price = self.data["Close"].iloc[-1]
        final_balance = balance + (crypto_holdings * final_price)

        return_pct = (
            (final_balance - self.initial_balance) / self.initial_balance
        ) * 100

        if equity_curve:
            equity_series = pd.Series(equity_curve)
            peak = equity_series.cummax()
            drawdown = (equity_series - peak) / peak
            max_drawdown = drawdown.min() * 100
        else:
            max_drawdown = 0.0

        winning_trades = [t for t in trades if t > 0]
        win_rate = (len(winning_trades) / len(trades) * 100) if trades else 0.0

        # --- NEW WORLD CLASS FEATURE 4: Monte Carlo Analysis ---
        mc_results = self._run_monte_carlo(trades)

        return {
            "Initial Balance": self.initial_balance,
            "Final Balance": final_balance,
            "Return %": return_pct,
            "Max Drawdown %": max_drawdown,
            "Win Rate %": win_rate,
            "Total Trades": len(trades),
            "MC Median Return %": mc_results["MC Median Return %"],
            "Risk of Ruin %": mc_results["Risk of Ruin %"],
        }
