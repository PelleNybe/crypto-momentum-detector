import re

with open("main.py", "r") as f:
    content = f.read()

imports = """
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
"""
content = re.sub(
    r"import yfinance as yf.*?import pandas as pd", imports, content, flags=re.DOTALL
)


generate_table_func = """
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
                res["ticker"], f"[red]{res['error']}[/red]", "", "", "", "", "", "", "", "", "", ""
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
"""

main_loop = """
    layout = Layout()
    layout.split(
        Layout(name="header", size=5),
        Layout(name="body")
    )
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
"""

content = re.sub(
    r"    results = \[\]\n.*?console\.print\(table\)",
    generate_table_func + "\n" + main_loop,
    content,
    flags=re.DOTALL,
)

with open("main.py", "w") as f:
    f.write(content)
