import streamlit as st
import pandas as pd
import concurrent.futures
import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from crypto_momentum.data_fetcher import DataFetcher
from crypto_momentum.indicators import MomentumIndicators
from crypto_momentum.signal_generator import SignalGenerator
from crypto_momentum.backtester import Backtester

st.set_page_config(
    page_title="Crypto Momentum Detector",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("⚡ Crypto Momentum Detector")
st.markdown(
    "Analyze cryptocurrency momentum, calculate technical indicators, and generate actionable trading signals!"
)

# Sidebar parameters
st.sidebar.header("Settings")

tickers_input = st.sidebar.text_input(
    "Tickers (space-separated)", "BTC-USD ETH-USD SOL-USD"
)
tickers = [t.strip().upper() for t in tickers_input.split() if t.strip()]

period = st.sidebar.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "max"], index=2)
interval = st.sidebar.selectbox("Interval", ["1h", "1d", "1wk"], index=1)

use_mtf = st.sidebar.checkbox("Enable MTF (Multi-Timeframe) Analysis", value=False)
run_backtest = st.sidebar.checkbox("Run Strategy Backtest", value=False)

st.sidebar.markdown("---")
st.sidebar.subheader("Strategy Parameters (RSI)")
rsi_buy_min = st.sidebar.number_input("RSI Buy Min", value=40)
rsi_buy_max = st.sidebar.number_input("RSI Buy Max", value=70)
rsi_sell_min = st.sidebar.number_input("RSI Sell Min", value=30)
rsi_sell_max = st.sidebar.number_input("RSI Sell Max", value=60)

strategy_params = {
    "rsi_buy_min": rsi_buy_min,
    "rsi_buy_max": rsi_buy_max,
    "rsi_sell_min": rsi_sell_min,
    "rsi_sell_max": rsi_sell_max,
    "rsi_strong_buy": 30,
    "rsi_strong_sell": 70,
}


def process_ticker(ticker, period, interval, run_backtest, strategy_params, use_mtf):
    try:
        fetcher = DataFetcher(ticker_symbol=ticker)
        df = fetcher.fetch_historical_data(period=period, interval=interval)

        if df.empty:
            return {"ticker": ticker, "error": True, "status": "No data"}

        htf_df = pd.DataFrame()
        if use_mtf:
            htf_df = fetcher.fetch_htf_data(period=period, interval=interval)

        indicators = MomentumIndicators(df, htf_df if use_mtf else None)
        df_with_indicators = indicators.calculate_all()

        generator = SignalGenerator(
            data=df_with_indicators,
            rsi_buy_min=strategy_params["rsi_buy_min"],
            rsi_buy_max=strategy_params["rsi_buy_max"],
            rsi_sell_min=strategy_params["rsi_sell_min"],
            rsi_sell_max=strategy_params["rsi_sell_max"],
            use_mtf=use_mtf,
        )

        # Get df with signals for charting
        df_with_signals = generator.generate_signals()

        latest_signal = generator.get_latest_signal()
        if not latest_signal:
            return {"ticker": ticker, "error": True, "status": "No signals"}

        latest_signal["ticker"] = ticker
        latest_signal["error"] = False
        latest_signal["status"] = "Success"
        latest_signal["df"] = df_with_signals

        if run_backtest:
            backtester = Backtester(df_with_signals)
            bt_results = backtester.run_backtest()
            latest_signal["backtest"] = bt_results

        return latest_signal
    except Exception as e:
        return {"ticker": ticker, "error": True, "status": str(e)}


if st.sidebar.button("Run Analysis", type="primary"):
    if not tickers:
        st.warning("Please enter at least one ticker.")
        st.stop()

    results = []

    with st.spinner("Analyzing assets..."):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(
                    process_ticker,
                    ticker,
                    period,
                    interval,
                    run_backtest,
                    strategy_params,
                    use_mtf,
                ): ticker
                for ticker in tickers
            }
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result())

    results.sort(key=lambda x: x["ticker"])

    successful_results = [r for r in results if not r["error"]]
    error_results = [r for r in results if r["error"]]

    if error_results:
        st.error(
            f"Failed to process: {', '.join([r['ticker'] for r in error_results])}"
        )

    if not successful_results:
        st.error("No valid data could be processed.")
        st.stop()

    # Portfolio Summary
    st.header("📊 Portfolio Summary")

    col1, col2, col3 = st.columns(3)

    highest_rsi = max(successful_results, key=lambda x: x["RSI"])
    lowest_rsi = min(successful_results, key=lambda x: x["RSI"])

    buy_signals = [r for r in successful_results if "BUY" in r["Action"]]
    sell_signals = [r for r in successful_results if "SELL" in r["Action"]]
    hold_signals = [r for r in successful_results if r["Action"] == "HOLD"]

    with col1:
        st.metric("Highest RSI", f"{highest_rsi['ticker']} ({highest_rsi['RSI']:.1f})")
        st.metric("Lowest RSI", f"{lowest_rsi['ticker']} ({lowest_rsi['RSI']:.1f})")

    with col2:
        st.markdown(f"**📈 BUY Signals:** {len(buy_signals)}")
        st.markdown(f"**📉 SELL Signals:** {len(sell_signals)}")
        st.markdown(f"**⏳ HOLD Signals:** {len(hold_signals)}")

    with col3:
        top_macd = sorted(
            successful_results,
            key=lambda x: x["MACD"] - x["MACD_Signal"],
            reverse=True,
        )[:2]
        st.markdown("**🔥 Top MACD Momentum**")
        for r in top_macd:
            st.markdown(f"- {r['ticker']}")

    st.divider()

    # Data Table
    st.header("📋 Detailed Overview")

    table_data = []
    for r in successful_results:
        row = {
            "Ticker": r["ticker"],
            "Price": f"${r['Price']:.2f}",
            "RSI (14)": round(r["RSI"], 2),
            "MACD": round(r["MACD"], 2),
            "Signal": r["Action"],
        }
        if use_mtf:
            row["HTF Trend"] = "BULL" if r.get("HTF_Trend", True) else "BEAR"

        sl = r.get("Stop_Loss")
        tp = r.get("Take_Profit")
        if (
            sl is not None
            and tp is not None
            and not math.isnan(sl)
            and not math.isnan(tp)
        ):
            row["SL/TP"] = f"SL: ${sl:.2f} / TP: ${tp:.2f}"
        else:
            row["SL/TP"] = "-"

        if run_backtest and "backtest" in r:
            row["BT Return %"] = f"{r['backtest'].get('Return %', 0):.2f}%"
            row["Win Rate %"] = f"{r['backtest'].get('Win Rate %', 0):.2f}%"

        table_data.append(row)

    st.dataframe(pd.DataFrame(table_data), use_container_width=True)

    st.divider()

    # Detailed Charts
    st.header("📈 Asset Charts")

    for r in successful_results:
        df = r["df"]
        ticker = r["ticker"]

        with st.expander(
            f"{ticker} - {r['Action']} - Price: ${r['Price']:.2f}", expanded=True
        ):

            # Create subplots
            fig = make_subplots(
                rows=3,
                cols=1,
                shared_xaxes=True,
                vertical_spacing=0.05,
                row_heights=[0.6, 0.2, 0.2],
            )

            # Candlestick chart
            fig.add_trace(
                go.Candlestick(
                    x=df.index,
                    open=df["Open"],
                    high=df["High"],
                    low=df["Low"],
                    close=df["Close"],
                    name="Price",
                ),
                row=1,
                col=1,
            )

            # Bollinger Bands
            if "BB_High" in df.columns and "BB_Low" in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df["BB_High"],
                        line=dict(color="gray", width=1, dash="dash"),
                        name="BB High",
                    ),
                    row=1,
                    col=1,
                )
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df["BB_Low"],
                        line=dict(color="gray", width=1, dash="dash"),
                        name="BB Low",
                        fill="tonexty",
                        fillcolor="rgba(128,128,128,0.1)",
                    ),
                    row=1,
                    col=1,
                )

            # Moving averages
            if "SMA_20" in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df["SMA_20"],
                        line=dict(color="orange", width=1),
                        name="SMA 20",
                    ),
                    row=1,
                    col=1,
                )
            if "SMA_50" in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df["SMA_50"],
                        line=dict(color="blue", width=1),
                        name="SMA 50",
                    ),
                    row=1,
                    col=1,
                )

            # RSI
            if "RSI_14" in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df["RSI_14"],
                        line=dict(color="purple", width=2),
                        name="RSI 14",
                    ),
                    row=2,
                    col=1,
                )
                # RSI Overbought/Oversold lines
                fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

            # MACD
            if "MACD" in df.columns and "MACD_Signal" in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df["MACD"],
                        line=dict(color="blue", width=1),
                        name="MACD",
                    ),
                    row=3,
                    col=1,
                )
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df["MACD_Signal"],
                        line=dict(color="orange", width=1),
                        name="Signal",
                    ),
                    row=3,
                    col=1,
                )

                # MACD Histogram
                macd_hist = df["MACD"] - df["MACD_Signal"]
                colors = ["green" if val >= 0 else "red" for val in macd_hist]
                fig.add_trace(
                    go.Bar(
                        x=df.index, y=macd_hist, marker_color=colors, name="Histogram"
                    ),
                    row=3,
                    col=1,
                )

            # Update layout
            fig.update_layout(
                title=f"{ticker} Technical Analysis",
                xaxis_rangeslider_visible=False,
                height=800,
                template="plotly_dark",
            )

            st.plotly_chart(fig, use_container_width=True)

            # Additional info
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Signal Details")
                st.write(f"**Action:** {r['Action']}")
                if r.get("Stop_Loss") and not math.isnan(r.get("Stop_Loss")):
                    st.write(f"**Stop Loss:** ${r['Stop_Loss']:.2f}")
                if r.get("Take_Profit") and not math.isnan(r.get("Take_Profit")):
                    st.write(f"**Take Profit:** ${r['Take_Profit']:.2f}")

            if run_backtest and "backtest" in r:
                with col2:
                    st.subheader("Backtest Performance")
                    bt = r["backtest"]
                    st.write(f"**Total Return:** {bt.get('Return %', 0):.2f}%")
                    st.write(f"**Max Drawdown:** {bt.get('Max Drawdown %', 0):.2f}%")
                    st.write(f"**Win Rate:** {bt.get('Win Rate %', 0):.2f}%")
                    st.write(f"**Total Trades:** {bt.get('Total Trades', 0)}")
