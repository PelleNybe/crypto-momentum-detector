import argparse
import sys
import concurrent.futures
import csv
import math
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from rich.panel import Panel
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
)
from rich.columns import Columns
from rich.align import Align
from rich.text import Text

from crypto_momentum.data_fetcher import DataFetcher
from crypto_momentum.indicators import MomentumIndicators
from crypto_momentum.signal_generator import SignalGenerator
from crypto_momentum.backtester import Backtester

console = Console()


def generate_sparkline(data: list) -> str:
    if not data or len(data) == 0:
        return ""

    chars = " ▂▃▄▅▆▇█"

    clean_data = [d for d in data if not math.isnan(d)]
    if not clean_data:
        return ""

    min_val = min(clean_data)
    max_val = max(clean_data)

    if max_val == min_val:
        return chars[0] * len(clean_data)

    range_val = max_val - min_val

    sparkline = ""
    for val in clean_data:
        normalized = (val - min_val) / range_val
        index = int(normalized * (len(chars) - 1))
        index = max(0, min(len(chars) - 1, index))
        sparkline += chars[index]

    if clean_data[-1] > clean_data[0]:
        return f"[green]{sparkline}[/green]"
    else:
        return f"[red]{sparkline}[/red]"


def process_ticker(
    ticker, period, interval, backtest=False, strategy_params=None, use_mtf=False
):
    try:
        fetcher = DataFetcher(ticker_symbol=ticker)
        data = fetcher.fetch_historical_data(period=period, interval=interval)

        if data.empty:
            return {"ticker": ticker, "status": "No Data", "error": True}

        htf_data = None
        if use_mtf:
            htf_data = fetcher.fetch_htf_data(period=period, interval=interval)

        indicators = MomentumIndicators(data, htf_data=htf_data)
        df_indicators = indicators.calculate_all()

        if strategy_params is None:
            strategy_params = {}

        params_with_mtf = strategy_params.copy()
        params_with_mtf["use_mtf"] = use_mtf

        generator = SignalGenerator(df_indicators, **params_with_mtf)
        latest = generator.get_latest_signal()

        if not latest:
            return {"ticker": ticker, "status": "Insufficient Data", "error": True}

        latest["ticker"] = ticker
        latest["error"] = False

        if backtest:
            df_with_signals = generator.generate_signals()
            bt = Backtester(
                df_with_signals,
                initial_balance=10000.0,
                fee_rate=0.001,
                slippage=0.0005,
                position_size=1.0,
            )
            bt_results = bt.run()
            latest["backtest"] = bt_results

        return latest

    except Exception as e:
        return {"ticker": ticker, "status": f"Error: {e}", "error": True}


def display_summary(results):
    valid_results = [r for r in results if not r["error"]]

    if not valid_results:
        return

    top_rsi = sorted(valid_results, key=lambda x: x["RSI"], reverse=True)[:3]
    bottom_rsi = sorted(valid_results, key=lambda x: x["RSI"])[:3]

    top_macd = sorted(
        valid_results, key=lambda x: x["MACD"] - x["MACD_Signal"], reverse=True
    )[:3]

    rsi_bulls = ", ".join([f"{r['ticker']} ({r['RSI']:.1f})" for r in top_rsi])
    rsi_bears = ", ".join([f"{r['ticker']} ({r['RSI']:.1f})" for r in bottom_rsi])
    macd_bulls = ", ".join([f"{r['ticker']}" for r in top_macd])

    summary_text = (
        f"[bold cyan]Highest RSI:[/bold cyan] {rsi_bulls}\n"
        f"[bold magenta]Lowest RSI:[/bold magenta] {rsi_bears}\n"
        f"[bold green]Top MACD Momentum:[/bold green] {macd_bulls}"
    )

    console.print(
        Panel(summary_text, title="📊 Portfolio Summary", border_style="cyan")
    )


def display_action_recommendations(results):
    valid_results = [r for r in results if not r["error"]]
    if not valid_results:
        return

    strong_buys = [r["ticker"] for r in valid_results if r["Action"] == "STRONG BUY"]
    buys = [r["ticker"] for r in valid_results if r["Action"] == "BUY"]
    sells = [r["ticker"] for r in valid_results if r["Action"] == "SELL"]
    strong_sells = [r["ticker"] for r in valid_results if r["Action"] == "STRONG SELL"]
    holds = [r["ticker"] for r in valid_results if r["Action"] == "HOLD"]

    action_text = []

    if strong_buys:
        action_text.append(
            f"[bold bright_green]🚀 STRONG BUY:[/bold bright_green] {len(strong_buys)} assets ({', '.join(strong_buys)}) show extreme bullish momentum."
        )
    if buys:
        action_text.append(
            f"[bold green]📈 BUY:[/bold green] {len(buys)} assets ({', '.join(buys)}) show favorable entry conditions."
        )
    if holds:
        action_text.append(
            f"[bold yellow]⏳ HOLD:[/bold yellow] {len(holds)} assets ({', '.join(holds)}) have neutral or conflicting momentum."
        )
    if sells:
        action_text.append(
            f"[bold red]📉 SELL:[/bold red] {len(sells)} assets ({', '.join(sells)}) show bearish momentum. Consider exiting."
        )
    if strong_sells:
        action_text.append(
            f"[bold bright_red]💥 STRONG SELL:[/bold bright_red] {len(strong_sells)} assets ({', '.join(strong_sells)}) show extreme bearish conditions."
        )

    if not action_text:
        action_text.append("No actionable signals at this time.")

    console.print(
        Panel(
            "\n".join(action_text),
            title="🎯 Trading Action Recommendations",
            border_style="green",
        )
    )


def display_backtest_results(results):
    valid_bt_results = [r for r in results if not r["error"] and "backtest" in r]
    if not valid_bt_results:
        return

    bt_panels = []

    for r in valid_bt_results:
        bt = r["backtest"]
        ticker = r["ticker"]

        ret = bt.get("Return %", 0)
        ret_color = "green" if ret > 0 else "red"

        dd = bt.get("Max Drawdown %", 0)
        wr = bt.get("Win Rate %", 0)
        trades = bt.get("Total Trades", 0)
        init_bal = bt.get("Initial Balance", 0)
        final_bal = bt.get("Final Balance", 0)

        content = (
            f"[bold]Initial:[/bold] ${init_bal:,.2f}\n"
            f"[bold]Final:[/bold] ${final_bal:,.2f}\n"
            f"[bold]Return:[/bold] [{ret_color}]{ret:.2f}%[/{ret_color}]\n"
            f"──────────────\n"
            f"[bold]Max DD:[/bold] [red]{dd:.2f}%[/red]\n"
            f"[bold]Win Rate:[/bold] {wr:.1f}%\n"
            f"[bold]Trades:[/bold] {trades}"
        )

        panel = Panel(
            content,
            title=f"[bold {ret_color}]{ticker}[/bold {ret_color}]",
            border_style=ret_color,
            expand=False,
        )
        bt_panels.append(panel)

    console.print(
        Panel(
            Columns(bt_panels, equal=True, expand=True),
            title="[bold]⏪ Backtest Results (Historical)[/bold]",
            border_style="yellow",
        )
    )


def main():
    parser = argparse.ArgumentParser(description="Crypto Momentum Detector CLI")
    parser.add_argument(
        "--tickers",
        type=str,
        nargs="+",
        default=["BTC-USD", "ETH-USD"],
        help="List of cryptocurrency tickers to analyze",
    )
    parser.add_argument(
        "--period", type=str, default="6mo", help="Historical data period to fetch"
    )
    parser.add_argument(
        "--interval", type=str, default="1d", help="Interval of historical data"
    )
    parser.add_argument(
        "--export",
        type=str,
        default=None,
        help="File path to export the results as CSV",
    )
    parser.add_argument(
        "--backtest",
        action="store_true",
        help="Run a backtest on historical data and show performance",
    )
    parser.add_argument(
        "--use-mtf",
        action="store_true",
        help="Enable Multi-Timeframe (MTF) analysis for signal confirmation",
    )

    args = parser.parse_args()
    tickers = args.tickers
    period = args.period
    interval = args.interval
    export_path = args.export
    backtest = args.backtest
    use_mtf = args.use_mtf

    strategy_params = {
        "rsi_buy_min": 40,
        "rsi_buy_max": 70,
        "rsi_sell_min": 30,
        "rsi_sell_max": 60,
        "rsi_strong_buy": 30,
        "rsi_strong_sell": 70,
    }

    mtf_status = (
        "[bold green]Enabled[/bold green]"
        if use_mtf
        else "[bold red]Disabled[/bold red]"
    )

    console.print(
        Panel.fit(
            f"[bold blue]Crypto Momentum Detector[/bold blue]\n"
            f"Analyzing: {len(tickers)} assets\n"
            f"Period: {period} | Interval: {interval} | MTF: {mtf_status}",
            title="Settings",
            border_style="blue",
        )
    )

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Ticker", style="dim", width=12)
    table.add_column("Date", justify="center")
    table.add_column("Price (USD)", justify="right")
    table.add_column("Trend (14p)", justify="center")
    table.add_column("RSI (14)", justify="right")
    table.add_column("MACD", justify="right")
    table.add_column("BB (L-H)", justify="center")
    if use_mtf:
        table.add_column("HTF Trend", justify="center")
    table.add_column("Signal", justify="center")
    table.add_column("Risk (SL/TP)", justify="center")

    results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[green]Analyzing assets...", total=len(tickers))

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(
                    process_ticker,
                    ticker,
                    period,
                    interval,
                    backtest,
                    strategy_params,
                    use_mtf,
                ): ticker
                for ticker in tickers
            }
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())
                progress.advance(task)

    results.sort(key=lambda x: x["ticker"])

    export_data = []

    for result in results:
        ticker = result["ticker"]
        if result["error"]:
            row_vals = [
                ticker,
                result["status"],
                "-",
                "-",
                "-",
                "-",
                "-",
                "[red]ERROR[/red]",
                "-",
            ]
            if use_mtf:
                row_vals.insert(7, "-")
            table.add_row(*row_vals)

            row_data = {
                "Ticker": ticker,
                "Date": result["status"],
                "Price (USD)": "-",
                "RSI (14)": "-",
                "MACD": "-",
                "BB_Low": "-",
                "BB_High": "-",
                "Signal": "ERROR",
                "Stop_Loss": "-",
                "Take_Profit": "-",
            }
            if use_mtf:
                row_data["HTF_Trend"] = "-"
            if backtest:
                row_data["BT_Return_Pct"] = "-"
                row_data["Max_DD_Pct"] = "-"
                row_data["Win_Rate_Pct"] = "-"
                row_data["Total_Trades"] = "-"
            export_data.append(row_data)
        else:
            latest = result
            rsi = latest["RSI"]
            rsi_color = "green" if rsi < 30 else "red" if rsi > 70 else "white"
            rsi_str = f"[{rsi_color}]{rsi:.2f}[/{rsi_color}]"

            macd_diff = latest["MACD"] - latest["MACD_Signal"]
            macd_color = "green" if macd_diff > 0 else "red"
            macd_str = f"[{macd_color}]{latest['MACD']:.2f}[/{macd_color}]"

            signal = latest["Action"]
            if "BUY" in signal:
                signal_color = "bold green"
            elif "SELL" in signal:
                signal_color = "bold red"
            else:
                signal_color = "bold yellow"
            signal_str = f"[{signal_color}]{signal}[/{signal_color}]"

            sl = latest.get("Stop_Loss")
            tp = latest.get("Take_Profit")
            if (
                sl is not None
                and tp is not None
                and not math.isnan(sl)
                and not math.isnan(tp)
            ):
                risk_str = f"[red]SL: ${sl:.2f}[/red]\n[green]TP: ${tp:.2f}[/green]"
            else:
                risk_str = "-"

            sparkline_str = generate_sparkline(latest.get("Sparkline_Data", []))

            row_vals = [
                ticker,
                latest["Date"],
                f"${latest['Price']:.2f}",
                sparkline_str,
                rsi_str,
                macd_str,
                f"${latest['BB_Low']:.0f} - ${latest['BB_High']:.0f}",
            ]

            if use_mtf:
                htf_trend = latest.get("HTF_Trend", True)
                htf_str = "[green]BULL[/green]" if htf_trend else "[red]BEAR[/red]"
                row_vals.append(htf_str)

            row_vals.append(signal_str)
            row_vals.append(risk_str)

            table.add_row(*row_vals)

            row_data = {
                "Ticker": ticker,
                "Date": latest["Date"],
                "Price (USD)": f"{latest['Price']:.2f}",
                "RSI (14)": f"{rsi:.2f}",
                "MACD": f"{latest['MACD']:.2f}",
                "BB_Low": f"{latest['BB_Low']:.2f}",
                "BB_High": f"{latest['BB_High']:.2f}",
                "Signal": signal,
                "Stop_Loss": (
                    f"{sl:.2f}" if sl is not None and not math.isnan(sl) else "-"
                ),
                "Take_Profit": (
                    f"{tp:.2f}" if tp is not None and not math.isnan(tp) else "-"
                ),
            }
            if use_mtf:
                row_data["HTF_Trend"] = (
                    "BULL" if latest.get("HTF_Trend", True) else "BEAR"
                )
            if backtest:
                row_data["BT_Return_Pct"] = (
                    f"{latest['backtest'].get('Return %', 0):.2f}%"
                )
                row_data["Max_DD_Pct"] = (
                    f"{latest['backtest'].get('Max Drawdown %', 0):.2f}%"
                )
                row_data["Win_Rate_Pct"] = (
                    f"{latest['backtest'].get('Win Rate %', 0):.2f}%"
                )
                row_data["Total_Trades"] = latest["backtest"].get("Total Trades", 0)
            export_data.append(row_data)

    display_summary(results)
    display_action_recommendations(results)

    if backtest:
        display_backtest_results(results)

    console.print(table)

    if export_path:
        try:
            with open(export_path, "w", newline="") as csvfile:
                fieldnames = [
                    "Ticker",
                    "Date",
                    "Price (USD)",
                    "RSI (14)",
                    "MACD",
                    "BB_Low",
                    "BB_High",
                ]
                if use_mtf:
                    fieldnames.append("HTF_Trend")
                fieldnames.extend(["Signal", "Stop_Loss", "Take_Profit"])
                if backtest:
                    fieldnames.extend(
                        ["BT_Return_Pct", "Max_DD_Pct", "Win_Rate_Pct", "Total_Trades"]
                    )
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in export_data:
                    writer.writerow(row)
            console.print(
                f"[green]Results successfully exported to {export_path}[/green]"
            )
        except Exception as e:
            console.print(f"[red]Error exporting results to {export_path}: {e}[/red]")


if __name__ == "__main__":
    main()
