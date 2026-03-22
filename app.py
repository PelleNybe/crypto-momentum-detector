import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import math
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Adjust imports to correctly path to module
from crypto_momentum.data_fetcher import DataFetcher
from crypto_momentum.indicators import MomentumIndicators
from crypto_momentum.signal_generator import SignalGenerator
from crypto_momentum.backtester import Backtester

# --- CUSTOM CSS FOR "DEEP TECH / CYBERPUNK" AESTHETIC ---
st.set_page_config(
    page_title="NeonPulse | Crypto AI Momentum",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* Main Backgrounds */
    .stApp {
        background-color: #05050f;
        color: #e0e0e0;
        font-family: 'Rajdhani', sans-serif;
    }

    /* Neon Glow Headers */
    h1, h2, h3 {
        color: #ffffff;
        text-shadow: 0 0 10px #14f5ee, 0 0 20px #14f5ee;
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
    }

    /* Sidebar */
    .css-1d391kg, .css-1lcbmhc {
        background-color: #0a0a1a !important;
        border-right: 1px solid #ff00d4;
    }

    /* Metrics Cards */
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #14f5ee;
        font-family: 'Orbitron', sans-serif;
        text-shadow: 0 0 5px #14f5ee;
    }
    div[data-testid="stMetricLabel"] {
        color: #ff00d4;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    div[data-testid="stMetricDelta"] svg {
        fill: #f9ca24;
    }
    div[data-testid="stMetricDelta"] {
        color: #f9ca24 !important;
    }

    /* DataFrame styling */
    .stDataFrame {
        border: 1px solid rgba(20, 245, 238, 0.3);
        border-radius: 5px;
        box-shadow: 0 0 15px rgba(20, 245, 238, 0.1);
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: rgba(255, 0, 212, 0.1);
        border: 1px solid #ff00d4;
        border-radius: 5px;
        color: #14f5ee;
        font-family: 'Orbitron', sans-serif;
    }

    /* Custom glowing divider */
    hr {
        border: 0;
        height: 1px;
        background-image: linear-gradient(to right, rgba(0, 0, 0, 0), rgba(20, 245, 238, 0.75), rgba(0, 0, 0, 0));
        box-shadow: 0 0 10px rgba(20, 245, 238, 0.5);
    }

    /* Buttons */
    .stButton>button {
        background-color: transparent;
        color: #14f5ee;
        border: 1px solid #14f5ee;
        border-radius: 4px;
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        font-weight: bold;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        box-shadow: 0 0 5px rgba(20, 245, 238, 0.5);
    }
    .stButton>button:hover {
        background-color: rgba(20, 245, 238, 0.1);
        border-color: #ff00d4;
        color: #ff00d4;
        box-shadow: 0 0 15px rgba(255, 0, 212, 0.8);
        transform: translateY(-2px);
    }

    /* Subheader specific */
    .st-emotion-cache-12w0qpk.e1f1d6gn2 {
         color: #f9ca24;
         text-shadow: 0 0 5px #f9ca24;
    }

    /* AI Confidence specific styling */
    .ai-confidence-high { color: #14f5ee; text-shadow: 0 0 8px #14f5ee; }
    .ai-confidence-mid { color: #f9ca24; text-shadow: 0 0 8px #f9ca24; }
    .ai-confidence-low { color: #ff00d4; text-shadow: 0 0 8px #ff00d4; }

    </style>
    """,
    unsafe_allow_html=True,
)

st.title("⚡ NeonPulse: AI Crypto Terminal")
st.markdown("*Advanced Momentum Detection & Machine Learning Predictions*")


# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.image(
        "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMjM1YzlkOGU4MjM2ZjY4ZjY4YmRjYzE2ZDZlNzY1MWRkODMwMjJjZiZlcD12MV9pbnRlcm5hbF9naWZzX2dpZklkJmN0PWc/JtBZm3Getg3dqxEX1E/giphy.gif",
        use_container_width=True,
    )
    st.header("⚙️ System Config")

    tickers_input = st.text_area(
        "Target Assets (Comma separated)", "BTC-USD, ETH-USD, SOL-USD"
    )

    col1, col2 = st.columns(2)
    with col1:
        period = st.selectbox(
            "Time Horizon", ["1mo", "3mo", "6mo", "1y", "2y", "max"], index=3
        )
    with col2:
        interval = st.selectbox(
            "Resolution", ["1h", "1d", "1wk", "1mo"], index=1
        )

    st.subheader("Neural Network & Risk")
    use_mtf = st.checkbox(
        "Multi-Timeframe Confluence (MTF)",
        value=True,
        help="Validates short-term signals against higher timeframe trend.",
    )
    run_backtest = st.checkbox(
        "Monte Carlo Backtest Simulation",
        value=True,
        help="Run historical simulation with 1000 iteration Monte Carlo risk analysis.",
    )

    st.divider()
    analyze_button = st.button("🚀 INITIATE SCAN", use_container_width=True)

# --- MAIN LOGIC ---
if analyze_button:
    tickers = [t.strip() for t in tickers_input.split(",") if t.strip()]

    if not tickers:
        st.error("⚠️ Please specify at least one target asset.")
        st.stop()

    results_container = st.empty()
    progress_bar = st.progress(0)
    status_text = st.empty()

    successful_results = []
    total_tickers = len(tickers)

    def process_ticker(ticker):
        try:
            fetcher = DataFetcher(ticker_symbol=ticker)
            df = fetcher.fetch_historical_data(period=period, interval=interval)

            htf_df = None
            if use_mtf:
                htf_df = fetcher.fetch_htf_data(period=period, interval=interval)

            if df.empty:
                return {"ticker": ticker, "error": "No data available."}

            indicators = MomentumIndicators(data=df, htf_data=htf_df)
            df_with_indicators = indicators.calculate_all()

            # Extract VPVR profile for charting before passing to signal generator
            vpvr_profile = indicators.calculate_vpvr(df_with_indicators)['profile']

            generator = SignalGenerator(data=df_with_indicators, use_mtf=use_mtf)
            latest_signal = generator.get_latest_signal()

            if not latest_signal:
                return {"ticker": ticker, "error": "Failed to generate signals."}

            result = {
                "ticker": ticker,
                "df": df_with_indicators,
                "vpvr_profile": vpvr_profile,
                **latest_signal,
            }

            if run_backtest:
                df_signals = generator.generate_signals()
                backtester = Backtester(data=df_signals)
                bt_results = backtester.run()
                result["backtest"] = bt_results

            return result
        except Exception as e:
            return {"ticker": ticker, "error": str(e)}

    # Execute Concurrently
    with ThreadPoolExecutor(max_workers=min(10, total_tickers)) as executor:
        futures = {executor.submit(process_ticker, t): t for t in tickers}
        completed = 0
        for future in futures:
            res = future.result()
            if "error" not in res:
                successful_results.append(res)
            completed += 1
            progress_bar.progress(completed / total_tickers)
            status_text.text(f"Scanning the matrix... {completed}/{total_tickers}")

    progress_bar.empty()
    status_text.empty()

    if not successful_results:
        st.error("🚨 System Failure: Could not establish connection to market data.")
        st.stop()

    # Portfolio Summary
    st.header("📊 AI Terminal Summary")

    col1, col2, col3, col4 = st.columns(4)

    highest_ai = max(successful_results, key=lambda x: x.get("AI_Confidence", 0))
    highest_rsi = max(successful_results, key=lambda x: x["RSI"])

    buy_signals = [r for r in successful_results if "BUY" in r["Action"]]
    sell_signals = [r for r in successful_results if "SELL" in r["Action"]]

    with col1:
        st.metric("Top AI Pick", f"{highest_ai['ticker']}", f"{highest_ai.get('AI_Confidence', 0):.1f}% Conf")

    with col2:
        st.markdown(f"**📈 BUY Configs:** {len(buy_signals)}")
        st.markdown(f"**📉 SELL Configs:** {len(sell_signals)}")

    with col3:
        st.metric("Highest RSI", f"{highest_rsi['ticker']}", f"{highest_rsi['RSI']:.1f}")

    with col4:
        top_mc = max(successful_results, key=lambda x: x.get("backtest", {}).get("MC Median Return %", 0)) if run_backtest and successful_results[0].get("backtest") else None
        if top_mc:
             st.metric("Best MC Return", f"{top_mc['ticker']}", f"{top_mc['backtest']['MC Median Return %']:.1f}%")

    st.divider()

    # Detailed Charts
    st.header("📈 Deep Tech Chart Analysis")

    for r in successful_results:
        df = r["df"]
        ticker = r["ticker"]
        ai_conf = r.get("AI_Confidence", 50)

        conf_class = "ai-confidence-high" if ai_conf > 60 else "ai-confidence-mid" if ai_conf >= 40 else "ai-confidence-low"

        with st.expander(f"{ticker} | SIGNAL: {r['Action']} | AI CONFIDENCE: {ai_conf:.1f}%", expanded=True):

            st.markdown(f"<h3 style='text-align: center; margin-bottom: 0;'><span class='{conf_class}'>AI CONFIDENCE: {ai_conf:.1f}%</span></h3>", unsafe_allow_html=True)

            # Create subplots including Volume Profile
            fig = make_subplots(
                rows=3,
                cols=2,
                column_widths=[0.8, 0.2],
                shared_xaxes=True,
                vertical_spacing=0.05,
                horizontal_spacing=0.01,
                row_heights=[0.6, 0.2, 0.2],
                specs=[[{"type": "xy"}, {"type": "xy"}],
                       [{"type": "xy", "colspan": 2}, None],
                       [{"type": "xy", "colspan": 2}, None]]
            )

            # --- Candlestick chart ---
            fig.add_trace(
                go.Candlestick(
                    x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"],
                    name="Price",
                    increasing_line_color="#14f5ee", decreasing_line_color="#ff00d4",
                    increasing_fillcolor="rgba(20, 245, 238, 0.4)", decreasing_fillcolor="rgba(255, 0, 212, 0.4)",
                ),
                row=1, col=1,
            )

            # --- WORLD CLASS FEATURE: Ichimoku Cloud Plotting ---
            if "Ichimoku_SpanA" in df.columns and "Ichimoku_SpanB" in df.columns:
                 # Standard Ichimoku plots are shifted 26 periods forward, but we align them with price here for display.
                 # To draw a filled cloud, we add Span A and Span B.
                 fig.add_trace(go.Scatter(x=df.index, y=df['Ichimoku_SpanA'], line=dict(color='rgba(20, 245, 238, 0.3)', width=1), name='Span A'), row=1, col=1)
                 fig.add_trace(go.Scatter(x=df.index, y=df['Ichimoku_SpanB'], line=dict(color='rgba(255, 0, 212, 0.3)', width=1), fill='tonexty', fillcolor='rgba(100, 100, 100, 0.1)', name='Span B'), row=1, col=1)

            # --- WORLD CLASS FEATURE: Fibonacci Retracements ---
            if "Fib_0" in df.columns:
                last_fib0 = df['Fib_0'].iloc[-1]
                last_fib5 = df['Fib_0.5'].iloc[-1]
                last_fib1 = df['Fib_1'].iloc[-1]

                fig.add_hline(y=last_fib0, line_dash="dash", line_color="red", opacity=0.3, row=1, col=1, annotation_text="Fib 0")
                fig.add_hline(y=last_fib5, line_dash="dash", line_color="yellow", opacity=0.3, row=1, col=1, annotation_text="Fib 0.5")
                fig.add_hline(y=last_fib1, line_dash="dash", line_color="green", opacity=0.3, row=1, col=1, annotation_text="Fib 1")

            # --- WORLD CLASS FEATURE: Volume Profile (VPVR) ---
            vpvr_profile = r.get("vpvr_profile", pd.DataFrame())
            if not vpvr_profile.empty:
                 y_vals = (vpvr_profile['Price_Start'] + vpvr_profile['Price_End']) / 2
                 fig.add_trace(
                     go.Bar(y=y_vals, x=vpvr_profile['Volume'], orientation='h', marker_color='rgba(249, 202, 36, 0.3)', showlegend=False),
                     row=1, col=2
                 )
                 # Add POC Line on Main Chart
                 poc_price = r.get('VPVR_POC', 0)
                 if poc_price > 0:
                      fig.add_hline(y=poc_price, line_width=2, line_color="#f9ca24", row=1, col=1, annotation_text="POC")

            # --- RSI ---
            if "RSI_14" in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df["RSI_14"], line=dict(color="#ff00d4", width=2), name="RSI 14"), row=2, col=1)
                fig.add_hline(y=70, line_dash="dash", line_color="#ff00d4", opacity=0.5, row=2, col=1)
                fig.add_hline(y=30, line_dash="dash", line_color="#14f5ee", opacity=0.5, row=2, col=1)

            # --- MACD ---
            if "MACD" in df.columns and "MACD_Signal" in df.columns:
                fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], line=dict(color="#686de0", width=1.5), name="MACD"), row=3, col=1)
                fig.add_trace(go.Scatter(x=df.index, y=df["MACD_Signal"], line=dict(color="#f9ca24", width=1.5), name="Signal"), row=3, col=1)
                macd_hist = df["MACD"] - df["MACD_Signal"]
                colors = ["#14f5ee" if val >= 0 else "#ff00d4" for val in macd_hist]
                fig.add_trace(go.Bar(x=df.index, y=macd_hist, marker_color=colors, name="Histogram"), row=3, col=1)

            # Update layout
            fig.update_layout(
                title=dict(text=f"<b>{ticker} AI & TECHNICAL ANALYSIS</b>", font=dict(family="Orbitron", size=20, color="#14f5ee")),
                xaxis_rangeslider_visible=False,
                height=900,
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(15, 15, 30, 0.6)",
                font=dict(family="Rajdhani", color="#e0e0e0", size=14),
                hovermode="x unified",
                margin=dict(l=20, r=20, t=60, b=20),
            )

            # Hide axes for VPVR
            fig.update_xaxes(showticklabels=False, showgrid=False, zeroline=False, row=1, col=2)
            fig.update_yaxes(showticklabels=False, showgrid=False, zeroline=False, row=1, col=2)

            st.plotly_chart(fig, use_container_width=True)

            # Additional info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.subheader("Signal Logic")
                st.write(f"**Final Action:** {r['Action']}")
                st.write(f"**Ichimoku Bullish:** {'Yes' if r.get('Ichimoku_Bullish') else 'No'}")
                if r.get("Stop_Loss") and not math.isnan(r.get("Stop_Loss")):
                    st.write(f"**Stop Loss:** ${r['Stop_Loss']:.2f}")
                if r.get("Take_Profit") and not math.isnan(r.get("Take_Profit")):
                    st.write(f"**Take Profit:** ${r['Take_Profit']:.2f}")

            with col2:
                 st.subheader("Key Levels (VPVR/Fib)")
                 st.write(f"**Volume POC:** ${r.get('VPVR_POC', 0):.2f}")
                 st.write(f"**Fib High (0):** ${r.get('Fib_0', 0):.2f}")
                 st.write(f"**Fib Mid (0.5):** ${r.get('Fib_0.5', 0):.2f}")
                 st.write(f"**Fib Low (1):** ${r.get('Fib_1', 0):.2f}")

            if run_backtest and "backtest" in r:
                with col3:
                    st.subheader("Monte Carlo Risk Profile")
                    bt = r["backtest"]
                    st.write(f"**Historical Return:** {bt.get('Return %', 0):.2f}%")
                    st.write(f"**Win Rate:** {bt.get('Win Rate %', 0):.2f}%")
                    st.write(f"**MC Median Return:** <span style='color:#14f5ee'>{bt.get('MC Median Return %', 0):.2f}%</span>", unsafe_allow_html=True)
                    risk_color = "#ff00d4" if bt.get('Risk of Ruin %', 0) > 10 else "#f9ca24" if bt.get('Risk of Ruin %', 0) > 5 else "#14f5ee"
                    st.write(f"**Risk of Ruin (>20% DD):** <span style='color:{risk_color}'>{bt.get('Risk of Ruin %', 0):.2f}%</span>", unsafe_allow_html=True)
