"""AI-Powered ROI Calculator - Streamlit Application."""

import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from dotenv import load_dotenv

from engines.roi_engine import ProjectInputs, run_all_scenarios
from engines.ai_advisor import get_ai_assessment

load_dotenv()


# --- Custom CSS ---
st.markdown("""
<style>
    .verdict-card {
        padding: 1.2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
        color: white;
    }
    .verdict-strong-go { background: linear-gradient(135deg, #28a745, #20c997); }
    .verdict-go { background: linear-gradient(135deg, #17a2b8, #28a745); }
    .verdict-cautious-go { background: linear-gradient(135deg, #ffc107, #fd7e14); color: #333; }
    .verdict-no-go { background: linear-gradient(135deg, #dc3545, #c82333); }
    .metric-box {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        border-left: 4px solid #667eea;
    }
    .risk-high { border-left: 4px solid #dc3545; }
    .risk-medium { border-left: 4px solid #ffc107; }
    .risk-low { border-left: 4px solid #28a745; }
</style>
""", unsafe_allow_html=True)


def format_currency(val: float) -> str:
    if abs(val) >= 1_000_000:
        return f"${val / 1_000_000:,.1f}M"
    if abs(val) >= 1_000:
        return f"${val / 1_000:,.0f}K"
    return f"${val:,.0f}"


def build_projection_chart(scenarios: dict, years: int) -> go.Figure:
    """Build a multi-scenario revenue/cost/profit chart."""
    year_labels = [f"Year {i+1}" for i in range(years)]
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("Revenue vs Costs (Most Likely)", "Cumulative Profit by Scenario"),
    )

    ml = scenarios["most_likely"]
    fig.add_trace(go.Bar(name="Revenue", x=year_labels, y=ml.yearly_revenue,
                         marker_color="#28a745"), row=1, col=1)
    fig.add_trace(go.Bar(name="Costs", x=year_labels, y=ml.yearly_costs,
                         marker_color="#dc3545"), row=1, col=1)

    colors = {"optimistic": "#28a745", "most_likely": "#17a2b8", "pessimistic": "#dc3545"}
    for key, sc in scenarios.items():
        fig.add_trace(go.Scatter(
            name=sc.label, x=year_labels, y=sc.cumulative_profit,
            mode="lines+markers", line=dict(color=colors[key], width=3),
        ), row=1, col=2)

    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5, row=1, col=2)
    fig.update_layout(height=400, showlegend=True, legend=dict(orientation="h", y=-0.15))
    fig.update_yaxes(tickprefix="$", row=1, col=1)
    fig.update_yaxes(tickprefix="$", row=1, col=2)
    return fig


def build_scenario_comparison_chart(scenarios: dict) -> go.Figure:
    """Build a grouped bar chart comparing key metrics across scenarios."""
    labels = [s.label for s in scenarios.values()]
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Total Revenue", x=labels,
                         y=[s.total_revenue for s in scenarios.values()], marker_color="#28a745"))
    fig.add_trace(go.Bar(name="Total Costs", x=labels,
                         y=[s.total_costs for s in scenarios.values()], marker_color="#dc3545"))
    fig.add_trace(go.Bar(name="Net Profit", x=labels,
                         y=[s.total_profit for s in scenarios.values()], marker_color="#17a2b8"))
    fig.update_layout(barmode="group", height=350, yaxis_tickprefix="$",
                      legend=dict(orientation="h", y=-0.15))
    return fig


def render_scenario_table(scenarios: dict, years: int):
    """Render a financial summary table."""
    rows = []
    for sc in scenarios.values():
        row = {"Scenario": sc.label, "Customers": sc.customer_count}
        for i in range(years):
            row[f"Y{i+1} Revenue"] = f"${sc.yearly_revenue[i]:,.0f}"
            row[f"Y{i+1} Costs"] = f"${sc.yearly_costs[i]:,.0f}"
            row[f"Y{i+1} Profit"] = f"${sc.yearly_profit[i]:,.0f}"
        row["Total Profit"] = f"${sc.total_profit:,.0f}"
        row["ROI %"] = f"{sc.roi_pct}%"
        row["NPV"] = f"${sc.npv:,.0f}"
        payback = f"{sc.payback_month} mo" if sc.payback_month else "N/A"
        row["Payback"] = payback
        rows.append(row)
    return pd.DataFrame(rows)


def render_ai_assessment(assessment: dict):
    """Render the AI strategic assessment."""
    # Go / No-Go Verdict
    verdict = assessment["go_no_go"]
    v = verdict["verdict"].lower().replace(" ", "-")
    css_class = f"verdict-{v}" if v in ("strong-go", "go", "cautious-go", "no-go") else "verdict-cautious-go"
    st.markdown(f"""
    <div class="verdict-card {css_class}">
        <h2 style="margin:0;">{verdict['verdict'].upper()}</h2>
        <p style="margin:0.3rem 0 0 0;">Confidence: {verdict['confidence']} | {verdict['reasoning']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Market Assessment
    ma = assessment["market_assessment"]
    col1, col2, col3 = st.columns(3)
    for col, label, val in [
        (col1, "Market Attractiveness", ma["market_attractiveness"]),
        (col2, "Competitive Intensity", ma["competitive_intensity"]),
        (col3, "Entry Barriers", ma["entry_barriers"]),
    ]:
        with col:
            st.markdown(f"""<div class="metric-box"><strong>{label}</strong><br/><span style="font-size:1.3rem;">{val}</span></div>""",
                        unsafe_allow_html=True)

    st.markdown(f"**Market Summary:** {ma['market_summary']}")

    # Risk Factors
    st.subheader("Risk Factors")
    for rf in assessment.get("risk_factors", []):
        sev = rf["severity"].lower()
        st.markdown(f"""
        <div class="metric-box risk-{sev}" style="margin-bottom:0.5rem;">
            <div style="text-align:left;">
                <strong>[{rf['severity']}]</strong> {rf['risk']}<br/>
                <em>Mitigation:</em> {rf['mitigation']}
            </div>
        </div>""", unsafe_allow_html=True)

    # Recommendations
    st.subheader("Strategic Recommendations")
    for i, rec in enumerate(assessment.get("recommendations", []), 1):
        st.markdown(f"**{i}.** {rec}")

    # Sensitivity
    if assessment.get("sensitivity_notes"):
        st.subheader("Sensitivity Notes")
        st.info(assessment["sensitivity_notes"])


# ===================== MAIN APP =====================

st.title("💰 AI-Powered ROI Calculator")
st.markdown("Estimate the ROI of expanding a product into a new market with AI-driven market assessment and multi-scenario financial projections.")

# Sidebar - API Key
api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.markdown("**Model:** Claude Sonnet 4.5")
    st.markdown("**Scenarios:** Optimistic, Most Likely, Pessimistic")

# --- Input Form ---
with st.form("roi_form"):
    st.subheader("Project Details")
    c1, c2 = st.columns(2)
    with c1:
        product_name = st.text_input("Product Name", value="Software Zed", placeholder="e.g. Software Zed")
        target_market = st.text_input("Target Market", value="ERCOT (North America Energy)", placeholder="e.g. ERCOT energy market")
    with c2:
        product_description = st.text_area("Product Description", height=100,
            value="Enterprise energy management SaaS platform for utility companies and grid operators.",
            placeholder="Brief description of the product...")

    st.divider()
    st.subheader("Cost Parameters")
    cc1, cc2, cc3 = st.columns(3)
    with cc1:
        initial_investment = st.number_input("Initial Investment ($)", min_value=0, value=500_000, step=50_000,
                                              help="One-time R&D / development cost")
    with cc2:
        annual_operating_cost = st.number_input("Annual Operating Cost ($)", min_value=0, value=200_000, step=25_000,
                                                 help="Ongoing annual costs (salaries, infra, support)")
    with cc3:
        annual_cost_growth = st.number_input("Annual Cost Growth (%)", min_value=0.0, value=5.0, step=1.0)

    st.divider()
    st.subheader("Revenue Parameters")
    rc1, rc2, rc3, rc4 = st.columns(4)
    with rc1:
        tam = st.number_input("Total Addressable Market", min_value=1, value=1100, step=100,
                               help="Total market participants")
    with rc2:
        qualifying_pct = st.number_input("Qualifying Ratio (%)", min_value=0.1, max_value=100.0, value=22.7, step=1.0,
                                          help="% of market that qualifies")
    with rc3:
        hit_rate = st.number_input("Expected Hit Rate (%)", min_value=0.1, max_value=100.0, value=10.0, step=1.0,
                                    help="Conversion rate of qualified leads")
    with rc4:
        avg_license = st.number_input("Avg Annual License ($)", min_value=0, value=165_000, step=5_000)

    rc5, rc6, rc7 = st.columns(3)
    with rc5:
        rev_start = st.number_input("Revenue Start Month", min_value=1, max_value=60, value=13, step=1,
                                     help="Month when first revenue begins")
    with rc6:
        rev_growth = st.number_input("Annual Revenue Growth (%)", min_value=0.0, value=10.0, step=1.0)
    with rc7:
        projection_years = st.selectbox("Projection Period (Years)", [1, 2, 3, 4, 5], index=2)

    st.divider()
    discount_rate = st.slider("Discount Rate for NPV (%)", min_value=0.0, max_value=25.0, value=10.0, step=0.5)

    submitted = st.form_submit_button("Calculate ROI", type="primary", use_container_width=True)

# --- Results ---
if submitted:
    inputs = ProjectInputs(
        product_name=product_name,
        target_market=target_market,
        product_description=product_description,
        initial_investment=initial_investment,
        annual_operating_cost=annual_operating_cost,
        annual_cost_growth_pct=annual_cost_growth,
        total_addressable_market=tam,
        qualifying_ratio_pct=qualifying_pct,
        hit_rate_pct=hit_rate,
        avg_annual_license=avg_license,
        revenue_start_month=rev_start,
        annual_revenue_growth_pct=rev_growth,
        projection_years=projection_years,
        discount_rate_pct=discount_rate,
    )

    # Calculate scenarios
    scenarios = run_all_scenarios(inputs)
    ml = scenarios["most_likely"]

    st.divider()
    st.header("Financial Projections")

    # Key metrics row
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Revenue", format_currency(ml.total_revenue))
    m2.metric("Total Costs", format_currency(ml.total_costs))
    m3.metric("Net Profit", format_currency(ml.total_profit))
    m4.metric("ROI", f"{ml.roi_pct}%")
    m5.metric("NPV", format_currency(ml.npv))

    # Charts
    st.plotly_chart(build_projection_chart(scenarios, projection_years), use_container_width=True)
    st.plotly_chart(build_scenario_comparison_chart(scenarios), use_container_width=True)

    # Scenario table
    st.subheader("Scenario Comparison")
    df = render_scenario_table(scenarios, projection_years)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # AI Assessment
    if not api_key:
        st.warning("Add an Anthropic API key in the sidebar to get AI-powered market assessment and recommendations.")
    else:
        st.divider()
        st.header("AI Strategic Assessment")
        with st.spinner("Claude is analyzing your market and financials..."):
            try:
                assessment = get_ai_assessment(inputs, scenarios, api_key)
                render_ai_assessment(assessment)
            except Exception as e:
                st.error(f"AI assessment failed: {e}")
                st.info("Financial projections above are still valid — they don't require the AI.")

    # Export
    st.divider()
    st.subheader("Export")
    csv = df.to_csv(index=False)
    st.download_button("Download Scenario Table (CSV)", csv, "roi_scenarios.csv", "text/csv")
