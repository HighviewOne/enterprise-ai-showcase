"""AI Stock Market Analysis Agent - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.analyst import analyze_stocks

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #0d6efd 0%, #6610f2 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .stock-card { background: #f8f9fa; border-radius: 10px; padding: 1.2rem;
        border-top: 4px solid #0d6efd; margin-bottom: 0.8rem; }
    .rec-badge { display: inline-block; padding: 0.3rem 0.8rem; border-radius: 20px;
        color: white; font-weight: bold; font-size: 0.9rem; }
    .risk-tag { display: inline-block; padding: 0.2rem 0.5rem; border-radius: 20px;
        margin: 0.1rem; font-size: 0.8rem; }
    .risk-low { background: #d4edda; color: #155724; }
    .risk-med { background: #fff3cd; color: #856404; }
    .risk-high { background: #f8d7da; color: #721c24; }
    .catalyst-pos { background: #d4edda; color: #155724; display: inline-block;
        padding: 0.2rem 0.5rem; border-radius: 20px; margin: 0.1rem; font-size: 0.8rem; }
    .catalyst-neg { background: #f8d7da; color: #721c24; display: inline-block;
        padding: 0.2rem 0.5rem; border-radius: 20px; margin: 0.1rem; font-size: 0.8rem; }
    .context-card { background: #e8f4fd; border-radius: 8px; padding: 1rem;
        border-left: 4px solid #0d6efd; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.markdown("**Disclaimer:** This tool is for educational purposes only. "
                "It does not constitute financial advice. Always consult a licensed "
                "financial advisor before making investment decisions.")

st.markdown("""<div class="hero"><h1>AI Stock Market Analyst</h1>
<p>Get comprehensive AI-powered stock analysis with fundamentals, technicals, risk assessment, and recommendations</p></div>""",
unsafe_allow_html=True)

with st.form("analysis_form"):
    c1, c2 = st.columns(2)
    with c1:
        tickers = st.text_input("Stock Ticker(s)", value="AAPL, MSFT, GOOGL",
                                placeholder="e.g., AAPL, TSLA, NVDA")
        thesis = st.text_area("Investment Thesis / Goals",
                              value="Looking for strong tech companies with solid fundamentals "
                                    "and long-term growth potential for a buy-and-hold strategy.",
                              height=80)
        context = st.text_area("Additional Context",
                               value="Interested in AI/cloud computing exposure. "
                                     "Already hold some index funds.",
                               height=60)
    with c2:
        risk_tolerance = st.selectbox("Risk Tolerance",
            ["Conservative", "Moderate", "Aggressive", "Very Aggressive"], index=1)
        horizon = st.selectbox("Investment Horizon",
            ["Short-term (1-3 months)", "Medium-term (3-12 months)",
             "Long-term (1-5 years)", "Very Long-term (5+ years)"], index=2)
        portfolio_size = st.selectbox("Portfolio Size",
            ["Under $10K", "$10K - $50K", "$50K - $100K",
             "$100K - $500K", "$500K+"], index=1)

    submitted = st.form_submit_button("Analyze Stocks", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        tickers=tickers, thesis=thesis, risk_tolerance=risk_tolerance,
        horizon=horizon, portfolio_size=portfolio_size, context=context,
    )

    with st.spinner("Analyzing stocks... This may take a moment."):
        try:
            result = analyze_stocks(config, api_key)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    # Disclaimer
    st.warning(result.get("disclaimer", "For educational purposes only."))

    # Market Context
    mkt = result.get("market_context", {})
    if mkt:
        st.subheader("Market Context")
        mc1, mc2 = st.columns([1, 2])
        with mc1:
            sentiment = mkt.get("market_sentiment", "N/A")
            sent_color = "#28a745" if "Bull" in sentiment else "#dc3545" if "Bear" in sentiment else "#ffc107"
            st.markdown(f'<span class="rec-badge" style="background:{sent_color};">'
                        f'{sentiment}</span>', unsafe_allow_html=True)
        with mc2:
            for factor in mkt.get("key_macro_factors", []):
                st.markdown(f"- {factor}")
        if mkt.get("upcoming_events"):
            st.info("**Upcoming Events:** " + " | ".join(mkt.get("upcoming_events", [])))

    # Individual Stock Analysis
    stocks = result.get("stocks", [])
    if stocks:
        st.divider()
        st.subheader(f"Stock Analysis ({len(stocks)} stocks)")

        for stock in stocks:
            rec = stock.get("recommendation", {})
            action = rec.get("action", "Hold")
            action_colors = {
                "Strong Buy": "#155724", "Buy": "#28a745", "Hold": "#ffc107",
                "Sell": "#fd7e14", "Strong Sell": "#dc3545",
            }
            badge_color = action_colors.get(action, "#6c757d")

            st.markdown(f"""<div class="stock-card">
                <span class="rec-badge" style="background:{badge_color};">{action}</span>
                <span style="margin-left:0.5rem; color:#666;">Confidence: {rec.get('confidence', 'N/A')}%</span>
                <h2 style="margin:0.5rem 0 0.2rem 0;">{stock.get('ticker', '')} — {stock.get('company_name', '')}</h2>
                <p style="margin:0; color:#666;">{stock.get('sector', '')} | Market Cap: {stock.get('market_cap', 'N/A')}</p>
                <h3 style="margin:0.3rem 0; color:#0d6efd;">~${stock.get('current_price_est', 0):,.2f}</h3>
                <p>Target: ${rec.get('target_price', 0):,.2f} | Stop Loss: ${rec.get('stop_loss', 0):,.2f} | {rec.get('time_horizon', '')}</p>
                <p><em>{rec.get('reasoning', '')}</em></p>
            </div>""", unsafe_allow_html=True)

            # Detailed tabs per stock
            t1, t2, t3, t4 = st.tabs(["Fundamentals", "Technicals", "Risk", "Comparables"])

            with t1:
                fa = stock.get("fundamental_analysis", {})
                f1, f2, f3, f4 = st.columns(4)
                f1.metric("P/E Ratio", fa.get("pe_ratio", "N/A"))
                f2.metric("Profit Margin", fa.get("profit_margin", "N/A"))
                f3.metric("Revenue Trend", fa.get("revenue_trend", "N/A"))
                f4.metric("Dividend Yield", fa.get("dividend_yield", "N/A"))
                f5, f6, f7, f8 = st.columns(4)
                f5.metric("D/E Ratio", fa.get("debt_to_equity", "N/A"))
                f6.metric("Free Cash Flow", fa.get("free_cash_flow", "N/A"))
                f7.metric("5yr Earnings Growth", fa.get("earnings_growth_5yr", "N/A"))
                f8.metric("P/E vs Industry", fa.get("pe_vs_industry", "N/A"))
                st.info(f"**Moat:** {fa.get('moat', 'N/A')}")
                st.markdown(fa.get("summary", ""))

            with t2:
                ta = stock.get("technical_analysis", {})
                t_1, t_2, t_3 = st.columns(3)
                t_1.metric("Trend", ta.get("trend", "N/A"))
                t_2.metric("RSI", ta.get("rsi_indication", "N/A"))
                t_3.metric("Volume", ta.get("volume_trend", "N/A"))

                # Support/Resistance chart
                fig_sr = go.Figure()
                price = stock.get("current_price_est", 0)
                support = ta.get("support_level", 0)
                resistance = ta.get("resistance_level", 0)
                if price and support and resistance:
                    fig_sr.add_trace(go.Bar(
                        x=["Support", "Current Price", "Resistance"],
                        y=[support, price, resistance],
                        marker_color=["#28a745", "#0d6efd", "#dc3545"],
                        text=[f"${support:,.0f}", f"${price:,.0f}", f"${resistance:,.0f}"],
                        textposition="outside",
                    ))
                    fig_sr.update_layout(title=f"{stock.get('ticker', '')} Price Levels",
                                         height=300, yaxis_tickprefix="$")
                    st.plotly_chart(fig_sr, use_container_width=True)

                st.markdown(f"**Moving Avg:** {ta.get('moving_avg_signal', 'N/A')}")
                st.markdown(ta.get("summary", ""))

            with t3:
                risk = stock.get("risk_assessment", {})
                overall = risk.get("overall_risk", "Medium")
                risk_cls = "risk-low" if overall == "Low" else "risk-high" if overall in ("High", "Very High") else "risk-med"
                st.markdown(f'Overall Risk: <span class="risk-tag {risk_cls}">{overall}</span> '
                            f'| Volatility: {risk.get("volatility", "N/A")} '
                            f'| Beta: {risk.get("beta", "N/A")}', unsafe_allow_html=True)

                rc1, rc2 = st.columns(2)
                with rc1:
                    st.markdown("**Key Risks**")
                    for r in risk.get("key_risks", []):
                        st.markdown(f'<span class="catalyst-neg">{r}</span>', unsafe_allow_html=True)
                    st.markdown("**Negative Catalysts**")
                    for c in risk.get("catalysts_negative", []):
                        st.markdown(f'<span class="catalyst-neg">{c}</span>', unsafe_allow_html=True)
                with rc2:
                    st.markdown("**Positive Catalysts**")
                    for c in risk.get("catalysts_positive", []):
                        st.markdown(f'<span class="catalyst-pos">{c}</span>', unsafe_allow_html=True)

            with t4:
                comps = stock.get("comparable_companies", [])
                if comps:
                    comp_df = pd.DataFrame(comps)
                    st.dataframe(comp_df, use_container_width=True, hide_index=True)

        # Comparison chart across all stocks
        if len(stocks) > 1:
            st.divider()
            st.subheader("Stock Comparison")

            # Price & target comparison
            fig_comp = go.Figure()
            tickers_list = [s.get("ticker", "") for s in stocks]
            prices = [s.get("current_price_est", 0) for s in stocks]
            targets = [s.get("recommendation", {}).get("target_price", 0) for s in stocks]
            fig_comp.add_trace(go.Bar(name="Current Price", x=tickers_list, y=prices,
                                       marker_color="#0d6efd"))
            fig_comp.add_trace(go.Bar(name="Target Price", x=tickers_list, y=targets,
                                       marker_color="#28a745"))
            fig_comp.update_layout(title="Current vs Target Price", barmode="group",
                                    height=350, yaxis_tickprefix="$")
            st.plotly_chart(fig_comp, use_container_width=True)

            # Comparison table
            comp_table = pd.DataFrame([{
                "Ticker": s.get("ticker", ""),
                "Company": s.get("company_name", ""),
                "Price": f"${s.get('current_price_est', 0):,.2f}",
                "Target": f"${s.get('recommendation', {}).get('target_price', 0):,.2f}",
                "P/E": s.get("fundamental_analysis", {}).get("pe_ratio", "N/A"),
                "Risk": s.get("risk_assessment", {}).get("overall_risk", "N/A"),
                "Action": s.get("recommendation", {}).get("action", "N/A"),
                "Confidence": f"{s.get('recommendation', {}).get('confidence', 0)}%",
            } for s in stocks])
            st.dataframe(comp_table, use_container_width=True, hide_index=True)

    # Portfolio suggestion
    portfolio = result.get("portfolio_suggestion", {})
    if portfolio:
        st.divider()
        st.subheader("Portfolio Strategy")
        st.markdown(f"**Allocation:** {portfolio.get('allocation_strategy', '')}")
        st.markdown(f"**Diversification:** {portfolio.get('diversification_notes', '')}")
        st.markdown(f"**Rebalancing:** {portfolio.get('rebalancing_suggestion', '')}")

    # Export
    st.divider()
    st.download_button("Download Analysis (JSON)", json.dumps(result, indent=2),
                       "stock_analysis.json", "application/json")
