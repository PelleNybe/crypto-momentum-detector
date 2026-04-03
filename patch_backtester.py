import re

with open("crypto_momentum/backtester.py", "r") as f:
    content = f.read()

run_func = """
    def run(self) -> dict:
        \"\"\"
        Simulates trading based on the 'Signal' column.
        \"\"\"
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

        for index, row in self.data.iterrows():
            signal = row["Signal"]
            price = row["Close"]
            high = row.get("High", price)
            low = row.get("Low", price)

            if pd.isna(price):
                current_value = balance + (crypto_holdings * price) if not pd.isna(price) else balance
                equity_curve.append({"Date": index, "Equity": current_value})
                continue

            # Check if SL or TP is hit before evaluating new signals
            if crypto_holdings > 0 and entry_price > 0:
                hit_sl = low <= stop_loss
                hit_tp = high >= take_profit

                if hit_sl or hit_tp:
                    exit_price = stop_loss if hit_sl else take_profit
                    # If market gapped below SL, exit at Open/Low (simplification: use SL price)

                    execution_price = exit_price * (1 - self.slippage)
                    revenue = crypto_holdings * execution_price
                    fee = revenue * self.fee_rate
                    net_revenue = revenue - fee

                    trade_return = (execution_price - entry_price) / entry_price
                    trades.append(trade_return)

                    trade_log.append({
                        "Exit Date": index,
                        "Type": "SL Hit" if hit_sl else "TP Hit",
                        "Entry Price": entry_price,
                        "Exit Price": execution_price,
                        "Return %": trade_return * 100
                    })

                    balance += net_revenue
                    crypto_holdings = 0.0
                    entry_price = 0.0
                    stop_loss = 0.0
                    take_profit = 0.0

                    current_value = balance
                    equity_curve.append({"Date": index, "Equity": current_value})
                    continue

            # Process new signals
            if signal in ["BUY", "STRONG BUY"] and balance > 0 and crypto_holdings == 0:
                # Volatility-based sizing (Risk / (Entry - SL))
                sl_price = row.get("Stop_Loss", price * 0.95)
                tp_price = row.get("Take_Profit", price * 1.10)

                if pd.isna(sl_price) or sl_price >= price:
                    sl_price = price * 0.95
                if pd.isna(tp_price) or tp_price <= price:
                    tp_price = price * 1.10

                risk_amount = balance * risk_per_trade
                price_risk = price - sl_price

                if price_risk > 0:
                    position_size_usd = min(balance, risk_amount / (price_risk / price))
                else:
                    position_size_usd = balance * self.position_size # Fallback

                if position_size_usd > 0:
                    execution_price = price * (1 + self.slippage)
                    crypto_bought = position_size_usd / execution_price
                    fee = crypto_bought * execution_price * self.fee_rate

                    crypto_holdings += crypto_bought - (fee / execution_price)
                    balance -= position_size_usd

                    entry_price = execution_price
                    stop_loss = sl_price
                    take_profit = tp_price

            elif signal in ["SELL", "STRONG SELL"] and crypto_holdings > 0:
                execution_price = price * (1 - self.slippage)
                revenue = crypto_holdings * execution_price
                fee = revenue * self.fee_rate
                net_revenue = revenue - fee

                if entry_price > 0:
                    trade_return = (execution_price - entry_price) / entry_price
                    trades.append(trade_return)

                    trade_log.append({
                        "Exit Date": index,
                        "Type": "Signal Exit",
                        "Entry Price": entry_price,
                        "Exit Price": execution_price,
                        "Return %": trade_return * 100
                    })

                balance += net_revenue
                crypto_holdings = 0.0
                entry_price = 0.0
                stop_loss = 0.0
                take_profit = 0.0

            current_value = balance + (crypto_holdings * price)
            equity_curve.append({"Date": index, "Equity": current_value})

        final_price = self.data["Close"].iloc[-1]
        final_balance = balance + (crypto_holdings * final_price)

        return_pct = (
            (final_balance - self.initial_balance) / self.initial_balance
        ) * 100

        if equity_curve:
            equity_df = pd.DataFrame(equity_curve).set_index("Date")
            equity_series = equity_df["Equity"]
            peak = equity_series.cummax()
            drawdown = (equity_series - peak) / peak
            max_drawdown = drawdown.min() * 100

            # Daily returns from equity curve
            daily_returns = equity_series.pct_change().dropna()

            # Sharpe Ratio (annualized, assuming daily data)
            if daily_returns.std() != 0:
                sharpe_ratio = (daily_returns.mean() / daily_returns.std()) * np.sqrt(
                    365
                )
            else:
                sharpe_ratio = 0.0

            # Sortino Ratio
            downside_returns = daily_returns[daily_returns < 0]
            if not downside_returns.empty and downside_returns.std() != 0:
                sortino_ratio = (
                    daily_returns.mean() / downside_returns.std()
                ) * np.sqrt(365)
            else:
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
            "Equity Curve": equity_curve,
            "Trade Log": trade_log
        }
"""

content = re.sub(r"    def run\(self\) -> dict:.*", run_func, content, flags=re.DOTALL)

with open("crypto_momentum/backtester.py", "w") as f:
    f.write(content)
