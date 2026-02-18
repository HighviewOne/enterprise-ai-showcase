"""PriceWise AI - Retail Pricing & Promotion Planner - Streamlit Application."""

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
    .hero { background: linear-gradient(135deg, #e91e63 0%, #f06292 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .price-card { background: #f8f9fa; border-radius: 10px; padding: 1rem;
        border-top: 4px solid #e91e63; margin-bottom: 0.6rem; }
    .promo-card { background: #fce4ec; border-radius: 10px; padding: 1rem;
        border-left: 4px solid #e91e63; margin-bottom: 0.6rem; }
    .alert-high { background: #ffebee; border-left: 4px solid #f44336;
        padding: 0.8rem; border-radius: 6px; margin: 0.3rem 0; }
    .alert-med { background: #fff3e0; border-left: 4px solid #ff9800;
        padding: 0.8rem; border-radius: 6px; margin: 0.3rem 0; }
    .alert-low { background: #e8f5e9; border-left: 4px solid #4caf50;
        padding: 0.8rem; border-radius: 6px; margin: 0.3rem 0; }
    .phase-card { background: #f3e5f5; border-radius: 8px; padding: 0.8rem;
        border-left: 4px solid #9c27b0; margin-bottom: 0.4rem; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input

st.markdown("""<div class="hero"><h1>PriceWise AI</h1>
<p>Intelligent pricing optimization and promotion planning for retail businesses</p></div>""",
unsafe_allow_html=True)

SAMPLE_CATALOG = """Product | Current Price | Cost | Monthly Units | Category
Organic Cold Brew Coffee (12oz) | $4.99 | $1.80 | 2,400 | Beverages
Artisan Sourdough Bread | $6.49 | $2.20 | 1,800 | Bakery
Greek Yogurt Parfait | $5.99 | $2.10 | 1,500 | Dairy/Snacks
Quinoa Power Bowl | $11.99 | $4.50 | 900 | Prepared Meals
Fresh-Pressed Green Juice (16oz) | $7.99 | $3.00 | 1,200 | Beverages
Grass-Fed Beef Burger Kit | $14.99 | $6.50 | 600 | Meat/Prepared
Vegan Protein Bar (box of 6) | $8.99 | $3.20 | 1,100 | Snacks
Seasonal Fruit Bowl | $6.99 | $2.80 | 1,400 | Produce"""

SAMPLE_COMPETITORS = """Competitor | Cold Brew | Sourdough | Yogurt Parfait | Power Bowl | Green Juice
Whole Foods | $5.49 | $5.99 | $6.49 | $12.99 | $8.49
Trader Joe's | $3.99 | $4.49 | $4.99 | $9.99 | $6.99
Local Co-op | $5.29 | $6.99 | $5.49 | $10.99 | $7.49
Sprouts | $4.49 | $5.49 | $5.79 | $11.49 | $7.99"""

with st.form("pricing_form"):
    st.subheader("Business Profile")
    b1, b2, b3 = st.columns(3)
    with b1:
        business_name = st.text_input("Business Name", value="Green Harvest Market")
        segment = st.selectbox("Industry Segment",
            ["Grocery / Specialty Food", "Fashion / Apparel", "Electronics",
             "Home & Garden", "Health & Beauty", "Sports & Outdoors", "Other"])
    with b2:
        store_type = st.selectbox("Store Type",
            ["Single Location", "Small Chain (2-10)", "Regional Chain (10-50)",
             "National Chain", "E-Commerce Only", "Omnichannel"])
        monthly_revenue = st.text_input("Monthly Revenue", value="$285,000")
    with b3:
        target_margin = st.text_input("Target Gross Margin", value="35-40%")
        objective = st.selectbox("Pricing Objective",
            ["Maximize Revenue", "Maximize Margin", "Gain Market Share",
             "Match Competitors", "Premium Positioning", "Clear Inventory"])

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        product_catalog = st.text_area("Product Catalog (name, price, cost, units, category)",
                                        value=SAMPLE_CATALOG, height=200)
    with c2:
        competitor_data = st.text_area("Competitor Pricing Data",
                                        value=SAMPLE_COMPETITORS, height=200)

    market_conditions = st.text_input("Market Conditions",
        value="Summer season approaching. Inflation at 3.2%. Health-conscious trend growing. "
              "New Whole Foods opening 2 miles away next month.")
    context = st.text_input("Additional Context",
        value="Want to prepare a summer promotion strategy. Loyalty program has 5,000 active members.")

    submitted = st.form_submit_button("Analyze Pricing & Generate Strategy",
                                       type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        business_name=business_name, segment=segment, store_type=store_type,
        monthly_revenue=monthly_revenue, target_margin=target_margin,
        product_catalog=product_catalog, competitor_data=competitor_data,
        market_conditions=market_conditions, objective=objective, context=context,
    )

    with st.spinner("Analyzing pricing and generating strategy..."):
        try:
            result = analyze_pricing(config, api_key)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    # Market Overview
    mkt = result.get("market_overview", {})
    if mkt:
        st.subheader("Market Overview")
        mo1, mo2, mo3 = st.columns(3)
        mo1.metric("Market Condition", mkt.get("market_condition", "N/A"))
        mo2.metric("Price Sensitivity", mkt.get("price_sensitivity", "N/A"))
        mo3.metric("Competitive Intensity", mkt.get("competitive_intensity", "N/A"))
        st.info(f"**Insight:** {mkt.get('key_insight', '')} | Seasonal: {mkt.get('seasonal_factors', '')}")

    # Alerts
    alerts = result.get("alerts", [])
    if alerts:
        st.divider()
        st.subheader("Pricing Alerts")
        for a in alerts:
            sev = a.get("severity", "Medium")
            cls = "alert-high" if sev == "High" else "alert-low" if sev == "Low" else "alert-med"
            icon = "🔴" if sev == "High" else "🟡" if sev == "Medium" else "🟢"
            st.markdown(f"""<div class="{cls}">
                {icon} <strong>[{a.get('type', '')}]</strong> {a.get('message', '')}<br/>
                <em>Action: {a.get('recommended_action', '')}</em>
            </div>""", unsafe_allow_html=True)

    # Product Pricing Recommendations
    products = result.get("product_analysis", [])
    if products:
        st.divider()
        st.subheader("Pricing Recommendations")

        # Price comparison chart
        fig = go.Figure()
        names = [p.get("product", "")[:25] for p in products]
        current = [p.get("current_price", 0) for p in products]
        recommended = [p.get("recommended_price", 0) for p in products]
        fig.add_trace(go.Bar(name="Current Price", x=names, y=current, marker_color="#90a4ae"))
        fig.add_trace(go.Bar(name="Recommended", x=names, y=recommended, marker_color="#e91e63"))
        fig.update_layout(title="Current vs Recommended Pricing", barmode="group",
                          height=350, yaxis_tickprefix="$")
        st.plotly_chart(fig, use_container_width=True)

        # Product cards
        for p in products:
            change = p.get("price_change_pct", 0)
            arrow = "↑" if change > 0 else "↓" if change < 0 else "→"
            color = "#4caf50" if change > 0 else "#f44336" if change < 0 else "#757575"
            st.markdown(f"""<div class="price-card">
                <strong>{p.get('product', '')}</strong>
                <span style="float:right; color:{color}; font-weight:bold;">
                    ${p.get('current_price', 0):.2f} {arrow} ${p.get('recommended_price', 0):.2f}
                    ({change:+.1f}%)
                </span><br/>
                Elasticity: {p.get('elasticity_estimate', 'N/A')} |
                vs Competitors: {p.get('competitor_position', 'N/A')} |
                Margin Impact: {p.get('margin_impact', 'N/A')} |
                Risk: {p.get('risk_level', 'N/A')}<br/>
                <em>{p.get('reasoning', '')}</em>
            </div>""", unsafe_allow_html=True)

        # Summary table
        price_df = pd.DataFrame([{
            "Product": p.get("product", "")[:30],
            "Current": f"${p.get('current_price', 0):.2f}",
            "Recommended": f"${p.get('recommended_price', 0):.2f}",
            "Change": f"{p.get('price_change_pct', 0):+.1f}%",
            "Confidence": p.get("confidence", "N/A"),
            "Risk": p.get("risk_level", "N/A"),
        } for p in products])
        st.dataframe(price_df, use_container_width=True, hide_index=True)

    # Promotion Plan
    promos = result.get("promotion_plan", [])
    if promos:
        st.divider()
        st.subheader(f"Promotion Strategy ({len(promos)} promotions)")
        for promo in promos:
            products_str = ", ".join(promo.get("target_products", []))
            st.markdown(f"""<div class="promo-card">
                <strong>{promo.get('promotion_name', '')}</strong> — {promo.get('discount_type', '')}<br/>
                <strong>Offer:</strong> {promo.get('discount_value', '')} |
                <strong>Duration:</strong> {promo.get('duration', '')} |
                <strong>Channel:</strong> {promo.get('channel', '')}<br/>
                <strong>Products:</strong> {products_str}<br/>
                <strong>Target:</strong> {promo.get('target_segment', '')} |
                <strong>Expected Lift:</strong> {promo.get('expected_lift_pct', 0)}% |
                <strong>Revenue Impact:</strong> {promo.get('expected_revenue_impact', 'N/A')}<br/>
                <strong>Timing:</strong> {promo.get('timing', '')}
            </div>""", unsafe_allow_html=True)

    # Revenue Simulation + Competitor Response
    rc1, rc2 = st.columns(2)

    rev = result.get("revenue_simulation", {})
    if rev:
        with rc1:
            st.divider()
            st.subheader("Revenue Projection")
            st.metric("Current Monthly", f"${rev.get('current_monthly_revenue', 0):,.0f}")
            st.metric("Projected Monthly", f"${rev.get('projected_monthly_revenue', 0):,.0f}",
                      delta=f"{rev.get('revenue_change_pct', 0):+.1f}%")
            fig_rev = go.Figure(go.Bar(
                x=["Worst Case", "Current", "Projected", "Best Case"],
                y=[rev.get("worst_case", 0), rev.get("current_monthly_revenue", 0),
                   rev.get("projected_monthly_revenue", 0), rev.get("best_case", 0)],
                marker_color=["#f44336", "#90a4ae", "#e91e63", "#4caf50"],
                text=[f"${v:,.0f}" for v in [rev.get("worst_case", 0),
                      rev.get("current_monthly_revenue", 0),
                      rev.get("projected_monthly_revenue", 0),
                      rev.get("best_case", 0)]],
                textposition="outside",
            ))
            fig_rev.update_layout(height=300, yaxis_tickprefix="$", title="Revenue Scenarios")
            st.plotly_chart(fig_rev, use_container_width=True)
            st.caption(f"Break-even: {rev.get('break_even_timeline', 'N/A')}")

    comp = result.get("competitor_response", {})
    if comp:
        with rc2:
            st.divider()
            st.subheader("Competitor Intelligence")
            st.metric("Price War Risk", comp.get("price_war_risk", "N/A"))
            st.markdown("**Likely Reactions:**")
            for r in comp.get("likely_reactions", []):
                st.markdown(f"- {r}")
            st.markdown("**Defensive Moves:**")
            for d in comp.get("defensive_moves", []):
                st.markdown(f"- {d}")
            st.markdown("**Differentiation Opportunities:**")
            for o in comp.get("differentiation_opportunities", []):
                st.success(o)

    # Implementation Roadmap
    roadmap = result.get("implementation_roadmap", [])
    if roadmap:
        st.divider()
        st.subheader("Implementation Roadmap")
        for phase in roadmap:
            actions = " | ".join(phase.get("actions", []))
            kpis = ", ".join(phase.get("kpis_to_track", []))
            st.markdown(f"""<div class="phase-card">
                <strong>{phase.get('phase', '')}</strong> — {phase.get('timeline', '')}<br/>
                Actions: {actions}<br/>
                <small>KPIs: {kpis}</small>
            </div>""", unsafe_allow_html=True)

    # Export
    st.divider()
    st.download_button("Download Pricing Strategy (JSON)", json.dumps(result, indent=2),
                       "pricing_strategy.json", "application/json")
