import yfinance as yf

yf.set_tz_cache_location(".yfinance_tz_cache")

import argparse
import sys
import math
import time
from concurrent.futures import ThreadPoolExecutor
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.live import Live
from rich.layout import Layout
import pandas as pd


from crypto_momentum.data_fetcher import DataFetcher
from crypto_momentum.indicators import MomentumIndicators
from crypto_momentum.signal_generator import SignalGenerator
from crypto_momentum.backtester import Backtester
from crypto_momentum.ai_predictor import AIPredictor

console = Console(record=True, width=120)


def format_color(val, threshold1, threshold2, reverse=False):
    if reverse:
        if val <= threshold1:
            return f"[green]{val:.2f}[/green]"
        if val >= threshold2:
            return f"[red]{val:.2f}[/red]"
    else:
        if val >= threshold2:
            return f"[green]{val:.2f}[/green]"
        if val <= threshold1:
            return f"[red]{val:.2f}[/red]"
    return f"[yellow]{val:.2f}[/yellow]"


def format_ai_confidence(val):
    if isinstance(val, dict):
        val = val.get("confidence", 50.0)
    if val >= 60:
        return f"[bold cyan]{val:.1f}%[/bold cyan]"
    if val <= 40:
        return f"[bold red]{val:.1f}%[/bold red]"
    return f"[bold yellow]{val:.1f}%[/bold yellow]"


def process_ticker(ticker, period, interval, use_mtf, run_backtest):
    fetcher = DataFetcher(ticker_symbol=ticker)
    df = fetcher.fetch_historical_data(period=period, interval=interval)

    htf_df = None
    if use_mtf:
        htf_df = fetcher.fetch_htf_data(period=period, interval=interval)

    if df.empty:
        return {"ticker": ticker, "error": "No data available."}

    indicators = MomentumIndicators(data=df, htf_data=htf_df)
    df_with_indicators = indicators.calculate_all()

    generator = SignalGenerator(data=df_with_indicators, use_mtf=use_mtf)
    latest_signal = generator.get_latest_signal()

    if not latest_signal:
        return {"ticker": ticker, "error": "Failed to generate signals."}

    # Get AI Confidence
    predictor = AIPredictor(df_with_indicators)
    ai_confidence = predictor.train_and_predict()
    latest_signal["AI_Confidence"] = ai_confidence

    result = {"ticker": ticker, **latest_signal}

    if run_backtest:
        df_signals = generator.generate_signals()
        backtester = Backtester(data=df_signals)
        result["backtest"] = backtester.run()

    return result


def main():
    parser = argparse.ArgumentParser(description="⚡ NeonPulse CLI: AI Crypto Momentum")
    parser.add_argument(
        "--tickers",
        nargs="+",
        default=["BTC-USD", "ETH-USD"],
        help="List of tickers (e.g., BTC-USD ETH-USD)",
    )
    parser.add_argument("--period", default="6mo", help="Data period (e.g., 6mo, 1y)")
    parser.add_argument("--interval", default="1d", help="Data interval (e.g., 1h, 1d)")
    parser.add_argument(
        "--use-mtf", action="store_true", help="Enable Multi-Timeframe Analysis"
    )
    parser.add_argument(
        "--backtest", action="store_true", help="Run historical Monte Carlo backtest"
    )
    parser.add_argument("--export", type=str, help="Export results to CSV (file path)")
    parser.add_argument(
        "--save-svg",
        action="store_true",
        help="Save the terminal output as an SVG file",
    )

    args = parser.parse_args()

    console.print(
        Panel.fit(
            "[bold cyan]⚡ NeonPulse AI Crypto Terminal ⚡[/bold cyan]\n"
            "[dim]Neural Network + Momentum Scanning + Risk Profiling[/dim]\n"
            "[italic]Developed by Pelle Nyberg (Corax CoLAB)[/italic]",
            border_style="cyan",
        )
    )


def generate_table(results, args):
    table = Table(box=box.MINIMAL_DOUBLE_HEAD, header_style="bold cyan")
    table.add_column("Asset", justify="left", style="bold white")
    table.add_column("Price", justify="right")
    table.add_column("AI Conf", justify="right")
    table.add_column("AI CV Acc", justify="right")
    table.add_column("RSI", justify="right")
    table.add_column("VPVR POC", justify="right")
    table.add_column("Regime", justify="center")
    table.add_column("Pattern", justify="center")
    table.add_column("StochRSI", justify="center")
    table.add_column("Cloud", justify="center")
    table.add_column("HTF Trend", justify="center")
    table.add_column("Action", justify="center", style="bold")

    if args.backtest:
        table.add_column("MC Return", justify="right")
        table.add_column("Risk Ruin", justify="right")
        table.add_column("Sharpe", justify="right")

    for res in results:
        if "error" in res:
            table.add_row(
                res["ticker"],
                f"[red]{res['error']}[/red]",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
                "",
            )
            continue

        action = res["Action"]
        action_fmt = (
            f"[bold green]{action}[/bold green]"
            if "BUY" in action
            else (
                f"[bold red]{action}[/bold red]"
                if "SELL" in action
                else f"[bold yellow]{action}[/bold yellow]"
            )
        )

        htf_fmt = "[green]BULL[/green]" if res.get("HTF_Trend") else "[red]BEAR[/red]"
        cloud = (
            "[green]BULL[/green]"
            if res.get("Ichimoku_Bullish")
            else (
                "[red]BEAR[/red]"
                if res.get("Ichimoku_Bearish")
                else "[yellow]NEUTRAL[/yellow]"
            )
        )

        row = [
            res["ticker"],
            f"${res['Price']:.2f}",
            format_ai_confidence(res.get("AI_Confidence", 50.0)),
            f"{res.get('AI_CV_Accuracy', 0.0):.1f}%",
            format_color(res["RSI"], 30, 70),
            f"${res.get('VPVR_POC', 0):.2f}",
            res.get("Market_Regime", "N/A"),
            res.get("Pattern", "None"),
            (
                "[green]Bullish[/green]"
                if res.get("Stoch_Bullish_Cross")
                else (
                    "[red]Bearish[/red]"
                    if res.get("Stoch_Bearish_Cross")
                    else "Neutral"
                )
            ),
            cloud,
            htf_fmt,
            action_fmt,
        ]

        if args.backtest and "backtest" in res:
            bt = res["backtest"]
            mc_ret = bt.get("MC Median Return %", 0)
            ruin = bt.get("Risk of Ruin %", 0)
            sharpe = bt.get("Sharpe Ratio", 0)

            mc_fmt = (
                f"[green]{mc_ret:.1f}%[/green]"
                if mc_ret > 0
                else f"[red]{mc_ret:.1f}%[/red]"
            )
            ruin_fmt = (
                f"[red]{ruin:.1f}%[/red]"
                if ruin > 10
                else (
                    f"[yellow]{ruin:.1f}%[/yellow]"
                    if ruin > 5
                    else f"[green]{ruin:.1f}%[/green]"
                )
            )
            sharpe_fmt = (
                f"[green]{sharpe:.2f}[/green]"
                if sharpe > 1
                else (
                    f"[yellow]{sharpe:.2f}[/yellow]"
                    if sharpe > 0
                    else f"[red]{sharpe:.2f}[/red]"
                )
            )

            row.extend([mc_fmt, ruin_fmt, sharpe_fmt])

        table.add_row(*row)
    return table

    layout = Layout()
    layout.split(Layout(name="header", size=5), Layout(name="body"))
    layout["header"].update(
        Panel.fit(
            "[bold cyan]⚡ NeonPulse AI Crypto Terminal ⚡[/bold cyan]\n"
            "[dim]Neural Network + Momentum Scanning + Risk Profiling[/dim]\n"
            "[italic]Developed by Pelle Nyberg (Corax CoLAB)[/italic]",
            border_style="cyan",
        )
    )

    results = []

    with Live(layout, refresh_per_second=4, console=console) as live:
        with ThreadPoolExecutor(max_workers=min(10, len(args.tickers))) as executor:
            futures = {
                executor.submit(
                    process_ticker,
                    t,
                    args.period,
                    args.interval,
                    args.use_mtf,
                    args.backtest,
                ): t
                for t in args.tickers
            }

            # Create a progress table while loading
            for future in futures:
                res = future.result()
                results.append(res)

                # Update layout body with current table
                layout["body"].update(generate_table(results, args))

    if args.save_svg:
        console.save_svg("docs/assets/ui_default.svg", title="NeonPulse UI")
        console.print(
            f"[bold green]✓[/bold green] Saved terminal output to docs/assets/ui_default.svg"
        )

    if args.save_svg:
        console.save_svg("docs/assets/ui_default.svg", title="NeonPulse UI")
        console.print(
            f"[bold green]✓[/bold green] Saved terminal output to docs/assets/ui_default.svg"
        )

    # Export logic
    if args.export:
        export_data = []
        for r in results:
            if "error" in r:
                continue
            row = {
                "Ticker": r["ticker"],
                "Price": r["Price"],
                "Action": r["Action"],
                "AI_Confidence": r.get("AI_Confidence", 50),
                "RSI": r["RSI"],
                "MACD": r["MACD"],
                "VPVR_POC": r.get("VPVR_POC", 0),
                "Ichimoku_Bullish": r.get("Ichimoku_Bullish", False),
            }
            if args.backtest and "backtest" in r:
                row["MC_Return_Pct"] = r["backtest"].get("MC Median Return %", 0)
                row["Risk_of_Ruin_Pct"] = r["backtest"].get("Risk of Ruin %", 0)
            export_data.append(row)

        pd.DataFrame(export_data).to_csv(args.export, index=False)
        console.print(f"[bold green]✓[/bold green] Results exported to {args.export}")


if __name__ == "__main__":
    main()
