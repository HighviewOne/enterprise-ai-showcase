"""PriceWise - Agentic Pricing Strategy Assistant - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.pricing_engine import analyze_pricing

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 50%, #43a047 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: #fdd835; margin: 0; }
    .rec-card { background: #f1f8e9; border: 1px solid #aed581; border-radius: 8px;
        padding: 1rem; margin-bottom: 0.5rem; }
    .promo-card { background: #fff3e0; border: 1px solid #ffb74d; border-radius: 8px;
        padding: 1rem; margin-bottom: 0.5rem; }
    .risk-high { border-left: 4px solid #f44336; }
    .risk-medium { border-left: 4px solid #ff9800; }
    .risk-low { border-left: 4px solid #4caf50; }
    .metric-card { background: #e8f5e9; border-radius: 10px; padding: 1rem; text-align: center; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**PriceWise** analyzes your product catalog and market conditions to generate "
            "optimized pricing strategies with revenue forecasts.")

st.markdown("""<div class="hero"><h1>PriceWise</h1>
<p>AI-powered pricing strategy optimization for retail</p></div>""",
unsafe_allow_html=True)

with st.form("pricing_form"):
    product_catalog = st.text_area("Product Catalog (Name | Current Price | Cost | Inventory | Competitor Price)", height=200,
        value="Samsung 65\" 4K Smart TV | $799.99 | $520.00 | 145 units | Best Buy: $779.99, Amazon: $789.99\n"
              "Sony WH-1000XM5 Headphones | $349.99 | $185.00 | 320 units | Best Buy: $329.99, Amazon: $339.99\n"
              "Apple iPad Air 11\" | $599.99 | $440.00 | 85 units | Apple Store: $599.99, Amazon: $579.99\n"
              "LG 27\" 4K Monitor | $449.99 | $270.00 | 210 units | Best Buy: $429.99, Amazon: $439.99\n"
              "Bose SoundLink Max Speaker | $279.99 | $145.00 | 180 units | Best Buy: $279.99, Amazon: $269.99\n"
              "Logitech MX Master 3S Mouse | $99.99 | $42.00 | 410 units | Best Buy: $89.99, Amazon: $94.99")

    c1, c2 = st.columns(2)
    with c1:
        margin_target = st.text_input("Gross Margin Target", value="35% minimum, 40% target")
        revenue_growth = st.text_input("Revenue Growth Target", value="15% YoY increase this quarter")
    with c2:
        inventory_goals = st.text_input("Inventory Goals", value="Clear slow-moving stock within 60 days, maintain 4-week cover on fast movers")
        market_conditions = st.text_area("Market Conditions", height=100,
            value="Q4 holiday season approaching in 6 weeks. Consumer electronics spending flat YoY. "
                  "Aggressive competitor promotions expected from Amazon Prime Day fallout. "
                  "New product launches from Samsung and Apple expected next month. "
                  "Supply chain stable, inflation moderating to 3.2%.")

    submitted = st.form_submit_button("Generate Pricing Strategy", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(product_catalog=product_catalog, margin_target=margin_target,
                  revenue_growth=revenue_growth, inventory_goals=inventory_goals,
                  market_conditions=market_conditions)

    with st.spinner("Analyzing pricing data and generating strategy..."):
        try:
            result = analyze_pricing(config, api_key)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    # Market Assessment
    market = result.get("market_assessment", {})
    if market:
        st.subheader("Market Assessment")
        st.markdown(f"**Competitive Position:** {market.get('competitive_position', '')}")
        st.markdown(f"**Consumer Sentiment:** {market.get('consumer_sentiment', '')}")
        st.markdown(f"**Market Impact:** {market.get('market_conditions_impact', '')}")
        if market.get("demand_trends"):
            for t in market["demand_trends"]:
                st.markdown(f"- {t}")

    # Pricing Recommendations with Chart
    recs = result.get("pricing_recommendations", [])
    if recs:
        st.divider()
        st.subheader("Pricing Recommendations")

        # Plotly chart: current vs recommended prices
        products = [r.get("product", "") for r in recs]
        current_prices = [r.get("current_price", 0) for r in recs]
        recommended_prices = [r.get("recommended_price", 0) for r in recs]

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Current Price", x=products, y=current_prices,
                             marker_color="#90a4ae", text=[f"${p:,.2f}" for p in current_prices],
                             textposition="outside"))
        fig.add_trace(go.Bar(name="Recommended Price", x=products, y=recommended_prices,
                             marker_color="#2e7d32", text=[f"${p:,.2f}" for p in recommended_prices],
                             textposition="outside"))
        fig.update_layout(barmode="group", title="Current vs Recommended Prices",
                          yaxis_title="Price ($)", height=450)
        st.plotly_chart(fig, use_container_width=True)

        # Recommendation cards
        for r in recs:
            change = r.get("price_change_pct", 0)
            direction = "increase" if change > 0 else "decrease" if change < 0 else "no change"
            st.markdown(f'<div class="rec-card"><strong>{r.get("product", "")}</strong>: '
                       f'${r.get("current_price", 0):,.2f} -> ${r.get("recommended_price", 0):,.2f} '
                       f'({change:+.1f}% {direction})<br/>'
                       f'<em>{r.get("rationale", "")}</em><br/>'
                       f'Volume Impact: {r.get("expected_volume_impact", "")} | '
                       f'Revenue Impact: {r.get("expected_revenue_impact", "")} | '
                       f'Confidence: {r.get("confidence", "")}</div>', unsafe_allow_html=True)

    # Revenue Forecast & Margin Analysis side by side
    fc1, fc2 = st.columns(2)
    forecast = result.get("revenue_forecast", {})
    if forecast:
        with fc1:
            st.divider()
            st.subheader("Revenue Forecast")
            st.metric("Current Monthly Revenue", f"${forecast.get('current_monthly_revenue', 0):,.0f}")
            st.metric("Projected Monthly Revenue", f"${forecast.get('projected_monthly_revenue', 0):,.0f}",
                      delta=f"{forecast.get('revenue_change_pct', 0):+.1f}%")
            st.markdown(f"**Best Case:** ${forecast.get('best_case', 0):,.0f}")
            st.markdown(f"**Worst Case:** ${forecast.get('worst_case', 0):,.0f}")

    margin = result.get("margin_analysis", {})
    if margin:
        with fc2:
            st.divider()
            st.subheader("Margin Analysis")
            st.metric("Current Avg Margin", f"{margin.get('current_avg_margin_pct', 0):.1f}%")
            st.metric("Projected Avg Margin", f"{margin.get('projected_avg_margin_pct', 0):.1f}%",
                      delta=f"{margin.get('margin_change_pct', 0):+.1f}%")
            pm = margin.get("per_product_margins", [])
            if pm:
                mdf = pd.DataFrame(pm)
                st.dataframe(mdf, use_container_width=True, hide_index=True)

    # Promotion Strategy
    promos = result.get("promotion_strategy", [])
    if promos:
        st.divider()
        st.subheader("Promotion Strategy")
        for p in promos:
            st.markdown(f'<div class="promo-card"><strong>{p.get("product", "")}</strong> - '
                       f'{p.get("promotion_type", "")}<br/>'
                       f'Discount: {p.get("discount_depth", "")} | '
                       f'Timing: {p.get("timing", "")} | Duration: {p.get("duration", "")}<br/>'
                       f'Expected Lift: {p.get("expected_lift", "")}<br/>'
                       f'<em>{p.get("rationale", "")}</em></div>', unsafe_allow_html=True)

    # Elasticity Analysis
    elasticity = result.get("elasticity_analysis", [])
    if elasticity:
        st.divider()
        st.subheader("Price Elasticity Analysis")
        edf = pd.DataFrame([{
            "Product": e.get("product", ""),
            "Sensitivity": e.get("price_sensitivity", ""),
            "Elasticity": e.get("elasticity_estimate", 0),
            "Optimal Range": e.get("optimal_price_range", ""),
            "Floor": f"${e.get('floor_price', 0):,.2f}",
            "Ceiling": f"${e.get('ceiling_price', 0):,.2f}",
        } for e in elasticity])
        st.dataframe(edf, use_container_width=True, hide_index=True)

    # Inventory Optimization
    inv = result.get("inventory_optimization", {})
    if inv:
        st.divider()
        st.subheader("Inventory Optimization")
        ic1, ic2 = st.columns(2)
        with ic1:
            st.markdown("**Markdown Candidates**")
            for m in inv.get("markdown_candidates", []):
                st.warning(f"**{m.get('product', '')}**: {m.get('reason', '')} - {m.get('suggested_markdown', '')}")
        with ic2:
            st.markdown("**Stockout Risks**")
            for s in inv.get("stockout_risks", []):
                st.info(f"**{s.get('product', '')}** ({s.get('risk_level', '')}): {s.get('recommendation', '')}")

    # Competitive Response
    comp = result.get("competitive_response_simulation", [])
    if comp:
        st.divider()
        st.subheader("Competitive Response Simulation")
        for c in comp:
            st.markdown(f"**{c.get('scenario', '')}** (Probability: {c.get('probability', '')})")
            st.markdown(f"- Competitor Response: {c.get('competitor_likely_response', '')}")
            st.markdown(f"- Our Counter: {c.get('our_counter_strategy', '')}")

    # Implementation Timeline
    timeline = result.get("implementation_timeline", [])
    if timeline:
        st.divider()
        st.subheader("Implementation Timeline")
        for phase in timeline:
            st.markdown(f"**{phase.get('phase', '')}** ({phase.get('timeframe', '')})")
            for a in phase.get("actions", []):
                st.markdown(f"  - {a}")
            st.markdown(f"  *Expected: {phase.get('expected_outcome', '')}*")

    # KPI Dashboard
    kpis = result.get("kpi_dashboard", [])
    if kpis:
        st.divider()
        st.subheader("KPI Dashboard")
        kdf = pd.DataFrame([{
            "Metric": k.get("metric", ""),
            "Current": k.get("current_value", ""),
            "Target": k.get("target_value", ""),
            "Frequency": k.get("measurement_frequency", ""),
        } for k in kpis])
        st.dataframe(kdf, use_container_width=True, hide_index=True)

    st.divider()
    st.download_button("Download Pricing Strategy (JSON)", json.dumps(result, indent=2),
                       "pricing_strategy.json", "application/json")
