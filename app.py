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

# --- CYBERPUNK / DEEP TECH CUSTOM CSS ---
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@400;500;600;700&display=swap');

/* Base Styles & Background */
.stApp {
    background-color: #050510;
    background-image:
        radial-gradient(circle at 15% 50%, rgba(20, 245, 238, 0.08) 0%, transparent 50%),
        radial-gradient(circle at 85% 30%, rgba(255, 0, 212, 0.08) 0%, transparent 50%);
    background-attachment: fixed;
    color: #e0e0e0;
    font-family: 'Rajdhani', sans-serif;
    overflow-x: hidden;
}

/* 3D Animated Grid Background */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: -50%; width: 200%; height: 200%;
    background-image:
        linear-gradient(rgba(20, 245, 238, 0.1) 1px, transparent 1px),
        linear-gradient(90deg, rgba(20, 245, 238, 0.1) 1px, transparent 1px);
    background-size: 50px 50px;
    transform: perspective(500px) rotateX(60deg) translateY(-100px) translateZ(-200px);
    animation: gridMove 15s linear infinite;
    z-index: -1;
    pointer-events: none;
}

@keyframes gridMove {
    0% { transform: perspective(500px) rotateX(60deg) translateY(0) translateZ(-200px); }
    100% { transform: perspective(500px) rotateX(60deg) translateY(50px) translateZ(-200px); }
}

/* Headings */
h1, h2, h3, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
    font-family: 'Orbitron', sans-serif !important;
    text-transform: uppercase;
    letter-spacing: 2px;
}

h1 {
    color: #fff;
    text-shadow: 0 0 10px #14f5ee, 0 0 20px #14f5ee, 0 0 40px #14f5ee;
    animation: pulseGlow 2s ease-in-out infinite alternate;
}

@keyframes pulseGlow {
    from { text-shadow: 0 0 10px #14f5ee, 0 0 20px #14f5ee; }
    to { text-shadow: 0 0 20px #14f5ee, 0 0 30px #14f5ee, 0 0 40px #14f5ee; }
}

h2 {
    color: #ff00d4;
    text-shadow: 0 0 5px #ff00d4, 0 0 10px #ff00d4;
    border-bottom: 2px solid rgba(255, 0, 212, 0.3);
    padding-bottom: 5px;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: rgba(10, 10, 25, 0.8) !important;
    backdrop-filter: blur(10px);
    border-right: 1px solid rgba(20, 245, 238, 0.2);
    box-shadow: 5px 0 15px rgba(0,0,0,0.5);
}

[data-testid="stSidebar"]::before {
    content: 'SYSTEM ACTIVE';
    position: absolute;
    top: 10px; right: 10px;
    font-family: 'Orbitron', sans-serif;
    font-size: 10px;
    color: #14f5ee;
    letter-spacing: 1px;
    animation: blink 2s infinite;
}

@keyframes blink { 0%, 100% {opacity: 1;} 50% {opacity: 0.3;} }

/* Inputs and Selectboxes */
.stTextInput>div>div>input, .stSelectbox>div>div>div {
    background-color: rgba(15, 15, 30, 0.6) !important;
    border: 1px solid rgba(20, 245, 238, 0.3) !important;
    color: #fff !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1.1rem;
    border-radius: 4px;
    transition: all 0.3s ease;
}

.stTextInput>div>div>input:focus, .stSelectbox>div>div>div:focus {
    border-color: #14f5ee !important;
    box-shadow: 0 0 15px rgba(20, 245, 238, 0.4) !important;
    transform: scale(1.02);
}

/* Buttons */
.stButton>button {
    background: linear-gradient(45deg, #14f5ee, #ff00d4);
    border: none;
    color: white;
    font-family: 'Orbitron', sans-serif;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 10px 20px;
    border-radius: 4px;
    text-transform: uppercase;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    position: relative;
    overflow: hidden;
    z-index: 1;
}

.stButton>button::before {
    content: '';
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background: linear-gradient(45deg, #ff00d4, #14f5ee);
    z-index: -1;
    transition: opacity 0.4s ease;
    opacity: 0;
}

.stButton>button:hover {
    transform: translateY(-3px) scale(1.05);
    box-shadow: 0 10px 20px rgba(255, 0, 212, 0.4), 0 0 15px rgba(20, 245, 238, 0.4);
    color: white;
}

.stButton>button:hover::before {
    opacity: 1;
}

.stButton>button:active {
    transform: translateY(1px) scale(0.98);
}

/* Metrics Cards (3D Hover Effect) */
[data-testid="stMetric"] {
    background: rgba(15, 15, 30, 0.6);
    border: 1px solid rgba(20, 245, 238, 0.2);
    border-radius: 8px;
    padding: 15px;
    backdrop-filter: blur(5px);
    transition: all 0.4s ease;
    transform-style: preserve-3d;
    perspective: 1000px;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-5px) rotateX(5deg) rotateY(-5deg);
    border-color: #14f5ee;
    box-shadow: -5px 10px 20px rgba(0,0,0,0.5), 0 0 15px rgba(20, 245, 238, 0.3);
}

[data-testid="stMetricValue"] {
    font-family: 'Orbitron', sans-serif;
    color: #fff;
    text-shadow: 0 0 5px #ff00d4;
}

[data-testid="stMetricLabel"] {
    color: #14f5ee;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Dataframe/Table */
[data-testid="stDataFrame"] {
    background: rgba(10, 10, 20, 0.7);
    border: 1px solid rgba(255, 0, 212, 0.3);
    border-radius: 8px;
    padding: 10px;
    box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
}

/* Expanders */
.streamlit-expanderHeader {
    background-color: rgba(20, 245, 238, 0.05) !important;
    border: 1px solid rgba(20, 245, 238, 0.3) !important;
    border-radius: 4px;
    font-family: 'Orbitron', sans-serif !important;
    color: #14f5ee !important;
    transition: all 0.3s ease;
}

.streamlit-expanderHeader:hover {
    background-color: rgba(20, 245, 238, 0.1) !important;
    border-color: #14f5ee !important;
    box-shadow: 0 0 10px rgba(20, 245, 238, 0.3);
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: #050510;
}
::-webkit-scrollbar-thumb {
    background: #14f5ee;
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: #ff00d4;
}

/* Alert/Warning Boxes */
.stAlert {
    background: rgba(255, 0, 212, 0.1) !important;
    border: 1px solid #ff00d4 !important;
    color: #fff !important;
    border-radius: 4px;
    border-left: 4px solid #ff00d4 !important;
}

/* Spinner */
.stSpinner > div > div {
    border-color: #14f5ee transparent #ff00d4 transparent !important;
}

/* Glitch Effect Text Utility */
.glitch {
    position: relative;
    color: white;
    font-size: 3rem;
    font-family: 'Orbitron', sans-serif;
    font-weight: 900;
    text-transform: uppercase;
    text-shadow: 0.05em 0 0 #14f5ee, -0.05em -0.05em 0 #ff00d4,
                 0.025em 0.05em 0 #fff;
    animation: glitch 1s infinite linear alternate-reverse;
}

@keyframes glitch {
  0% { text-shadow: 0.05em 0 0 #14f5ee, -0.05em -0.05em 0 #ff00d4, 0.025em 0.05em 0 #fff; }
  14% { text-shadow: 0.05em 0 0 #14f5ee, -0.05em -0.05em 0 #ff00d4, 0.025em 0.05em 0 #fff; }
  15% { text-shadow: -0.05em -0.025em 0 #14f5ee, 0.025em 0.025em 0 #ff00d4, -0.05em -0.05em 0 #fff; }
  49% { text-shadow: -0.05em -0.025em 0 #14f5ee, 0.025em 0.025em 0 #ff00d4, -0.05em -0.05em 0 #fff; }
  50% { text-shadow: 0.025em 0.05em 0 #14f5ee, 0.05em 0 0 #ff00d4, 0 -0.05em 0 #fff; }
  99% { text-shadow: 0.025em 0.05em 0 #14f5ee, 0.05em 0 0 #ff00d4, 0 -0.05em 0 #fff; }
  100% { text-shadow: -0.025em 0 0 #14f5ee, -0.025em -0.025em 0 #ff00d4, -0.025em -0.05em 0 #fff; }
}

/* Floating Orbs */
.orb {
    position: fixed;
    border-radius: 50%;
    filter: blur(50px);
    z-index: -1;
    animation: floatOrb 10s ease-in-out infinite alternate;
}
.orb1 { top: 10%; left: 20%; width: 200px; height: 200px; background: rgba(20, 245, 238, 0.15); animation-delay: 0s; }
.orb2 { bottom: 20%; right: 10%; width: 300px; height: 300px; background: rgba(255, 0, 212, 0.1); animation-delay: -3s; }
.orb3 { top: 50%; left: 60%; width: 150px; height: 150px; background: rgba(138, 43, 226, 0.15); animation-delay: -6s; }

@keyframes floatOrb {
    0% { transform: translate(0, 0) scale(1); }
    100% { transform: translate(30px, 50px) scale(1.1); }
}

/* 3D Expanders */
.streamlit-expander {
    background: rgba(15, 15, 30, 0.4) !important;
    border: 1px solid rgba(20, 245, 238, 0.2) !important;
    border-radius: 8px;
    margin-bottom: 15px;
    transition: all 0.4s ease;
    transform-style: preserve-3d;
    perspective: 1000px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}

.streamlit-expander:hover {
    transform: translateZ(10px);
    border-color: rgba(255, 0, 212, 0.5) !important;
    box-shadow: 0 10px 25px rgba(255, 0, 212, 0.2), inset 0 0 15px rgba(20, 245, 238, 0.1);
}

</style>

<div class="orb orb1"></div>
<div class="orb orb2"></div>
<div class="orb orb3"></div>
""",
    unsafe_allow_html=True,
)


st.markdown(
    '<div class="glitch" style="text-align: center; margin-bottom: 1rem;">NEONPULSE</div><h3 style="text-align: center; color: #14f5ee; letter-spacing: 5px;">CRYPTO MOMENTUM TERMINAL</h3>',
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center; font-size: 1.2rem; color: #a0a0a0;'>INITIALIZING QUANTITATIVE ANALYSIS PROTOCOLS...</p>",
    unsafe_allow_html=True,
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
                    increasing_line_color="#14f5ee",
                    decreasing_line_color="#ff00d4",
                    increasing_fillcolor="rgba(20, 245, 238, 0.4)",
                    decreasing_fillcolor="rgba(255, 0, 212, 0.4)",
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
                        line=dict(color="rgba(20, 245, 238, 0.5)", width=1, dash="dot"),
                        name="BB High",
                    ),
                    row=1,
                    col=1,
                )
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df["BB_Low"],
                        line=dict(color="rgba(20, 245, 238, 0.5)", width=1, dash="dot"),
                        name="BB Low",
                        fill="tonexty",
                        fillcolor="rgba(20, 245, 238, 0.05)",
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
                        line=dict(color="#f9ca24", width=1.5),
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
                        line=dict(color="#686de0", width=1.5),
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
                        line=dict(color="#ff00d4", width=2),
                        name="RSI 14",
                    ),
                    row=2,
                    col=1,
                )
                # RSI Overbought/Oversold lines
                fig.add_hline(
                    y=70,
                    line_dash="dash",
                    line_color="#ff00d4",
                    opacity=0.5,
                    row=2,
                    col=1,
                )
                fig.add_hline(
                    y=30,
                    line_dash="dash",
                    line_color="#14f5ee",
                    opacity=0.5,
                    row=2,
                    col=1,
                )

            # MACD
            if "MACD" in df.columns and "MACD_Signal" in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df["MACD"],
                        line=dict(color="#686de0", width=1.5),
                        name="MACD",
                    ),
                    row=3,
                    col=1,
                )
                fig.add_trace(
                    go.Scatter(
                        x=df.index,
                        y=df["MACD_Signal"],
                        line=dict(color="#f9ca24", width=1.5),
                        name="Signal",
                    ),
                    row=3,
                    col=1,
                )

                # MACD Histogram
                macd_hist = df["MACD"] - df["MACD_Signal"]
                colors = ["#14f5ee" if val >= 0 else "#ff00d4" for val in macd_hist]
                fig.add_trace(
                    go.Bar(
                        x=df.index, y=macd_hist, marker_color=colors, name="Histogram"
                    ),
                    row=3,
                    col=1,
                )

            # Update layout
            fig.update_layout(
                title=dict(
                    text=f"<b>{ticker} TECHNICAL ANALYSIS</b>",
                    font=dict(family="Orbitron", size=20, color="#14f5ee"),
                ),
                xaxis_rangeslider_visible=False,
                height=800,
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15, 15, 30, 0.6)",
                font=dict(family="Rajdhani", color="#e0e0e0", size=14),
                hoverlabel=dict(
                    bgcolor="rgba(10, 10, 25, 0.9)",
                    font_size=16,
                    font_family="Rajdhani",
                ),
                margin=dict(l=50, r=50, t=60, b=50),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(family="Rajdhani", color="#14f5ee"),
                ),
            )

            # Update axes for all subplots
            fig.update_xaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(20, 245, 238, 0.1)",
                zeroline=False,
                showline=True,
                linewidth=1,
                linecolor="rgba(20, 245, 238, 0.3)",
            )
            fig.update_yaxes(
                showgrid=True,
                gridwidth=1,
                gridcolor="rgba(20, 245, 238, 0.1)",
                zeroline=False,
                showline=True,
                linewidth=1,
                linecolor="rgba(20, 245, 238, 0.3)",
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
