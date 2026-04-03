import re

with open("app.py", "r") as f:
    content = f.read()

ai_ui = """
            # --- AI DASHBOARD ---
            st.markdown("<h3 style='text-align: center; color: #14f5ee; font-family: Orbitron;'>AI PREDICTIVE ENGINE</h3>", unsafe_allow_html=True)

            ai_col1, ai_col2 = st.columns([1, 2])

            with ai_col1:
                # V2: Plotly Gauge chart for AI Confidence
                conf = r.get("AI_Confidence", 50.0)
                cv_acc = r.get("AI_CV_Accuracy", 0.0)

                gauge_fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = conf,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Confidence (Bullish)", 'font': {'color': '#14f5ee'}},
                    gauge = {
                        'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#e0e0e0"},
                        'bar': {'color': "#14f5ee" if conf >= 50 else "#ff00d4"},
                        'bgcolor': "rgba(0,0,0,0)",
                        'borderwidth': 2,
                        'bordercolor': "#686de0",
                        'steps': [
                            {'range': [0, 40], 'color': "rgba(255, 0, 212, 0.2)"},
                            {'range': [40, 60], 'color': "rgba(249, 202, 36, 0.2)"},
                            {'range': [60, 100], 'color': "rgba(20, 245, 238, 0.2)"}],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 50}
                    }
                ))
                gauge_fig.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20), paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#e0e0e0"))
                st.plotly_chart(gauge_fig, use_container_width=True)
                st.markdown(f"<p style='text-align:center;'>CV Accuracy: {cv_acc:.1f}%</p>", unsafe_allow_html=True)

            with ai_col2:
                # V1: Plotly horizontal bar chart for AI Feature Importances
                fi = r.get("AI_Feature_Importances", {})
                if fi:
                    # Take top 10 features
                    top_fi = dict(list(fi.items())[:10])
                    fi_df = pd.DataFrame({'Feature': list(top_fi.keys()), 'Importance': list(top_fi.values())})
                    fi_df = fi_df.sort_values('Importance', ascending=True)

                    fi_fig = px.bar(fi_df, x='Importance', y='Feature', orientation='h', title='Top 10 AI Features')
                    fi_fig.update_layout(
                        height=250, margin=dict(l=20, r=20, t=30, b=20),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(color="#e0e0e0"),
                        xaxis=dict(showgrid=True, gridcolor="rgba(100,100,100,0.2)", zeroline=False),
                        yaxis=dict(showgrid=False)
                    )
                    fi_fig.update_traces(marker_color='#686de0')
                    st.plotly_chart(fi_fig, use_container_width=True)
                else:
                    st.write("Not enough data to calculate feature importances.")

            st.markdown("---")

            # Additional info
"""

content = re.sub(r"            # Additional info", ai_ui, content)


bt_ui = """
            if run_backtest and "backtest" in r:
                st.markdown("---")
                st.markdown("<h3 style='text-align: center; color: #14f5ee; font-family: Orbitron;'>MONTE CARLO BACKTEST RESULTS</h3>", unsafe_allow_html=True)

                with col4:
                    st.subheader("Risk Profile")
                    bt = r["backtest"]
                    st.write(f"**Historical Return:** {bt.get('Return %', 0):.2f}%")
                    st.write(f"**Win Rate:** {bt.get('Win Rate %', 0):.2f}%")
                    st.write(
                        f"**MC Median Return:** <span style='color:#14f5ee'>{bt.get('MC Median Return %', 0):.2f}%</span>",
                        unsafe_allow_html=True,
                    )
                    risk_color = (
                        "#ff00d4"
                        if bt.get("Risk of Ruin %", 0) > 10
                        else "#f9ca24" if bt.get("Risk of Ruin %", 0) > 5 else "#14f5ee"
                    )
                    st.write(
                        f"**Risk of Ruin (>20% DD):** <span style='color:{risk_color}'>{bt.get('Risk of Ruin %', 0):.2f}%</span>",
                        unsafe_allow_html=True,
                    )
                    st.write(f"**Sharpe Ratio:** {bt.get('Sharpe Ratio', 0):.2f}")
                    st.write(f"**Sortino Ratio:** {bt.get('Sortino Ratio', 0):.2f}")
                    st.write(f"**Profit Factor:** {bt.get('Profit Factor', 0):.2f}")

                # V3 & V5: Plotly line chart for Equity Curve and Interactive Trade Log
                eq_col, log_col = st.columns([2, 1])

                with eq_col:
                    equity_curve = bt.get("Equity Curve", [])
                    if equity_curve:
                        eq_df = pd.DataFrame(equity_curve)
                        eq_fig = px.line(eq_df, x='Date', y='Equity', title='Equity Curve')
                        eq_fig.update_layout(
                            height=350, margin=dict(l=20, r=20, t=40, b=20),
                            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,15,30,0.6)",
                            font=dict(color="#e0e0e0"),
                            xaxis=dict(showgrid=True, gridcolor="rgba(100,100,100,0.2)", zeroline=False),
                            yaxis=dict(showgrid=True, gridcolor="rgba(100,100,100,0.2)", zeroline=False)
                        )
                        eq_fig.update_traces(line=dict(color='#ff00d4', width=2))
                        st.plotly_chart(eq_fig, use_container_width=True)

                with log_col:
                    trade_log = bt.get("Trade Log", [])
                    if trade_log:
                        st.write("**Trade Log**")
                        tl_df = pd.DataFrame(trade_log)
                        tl_df['Return %'] = tl_df['Return %'].round(2)
                        st.dataframe(tl_df, height=350, use_container_width=True)
                    else:
                        st.write("No trades executed.")
"""

content = re.sub(
    r'            if run_backtest and "backtest" in r:.*?(?=\s+st.markdown\("---"\)|\Z)',
    bt_ui,
    content,
    flags=re.DOTALL,
)

with open("app.py", "w") as f:
    f.write(content)
