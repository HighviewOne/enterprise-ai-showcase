"""GridFlow - Power Grid Interconnection Analysis - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.grid_engine import analyze_interconnection

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #e65100 0%, #f9a825 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: #fff; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
    .viability-strong { background: #e8f5e9; border: 2px solid #2e7d32; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .viability-viable { background: #e3f2fd; border: 2px solid #1565c0; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .viability-marginal { background: #fff3e0; border: 2px solid #e65100; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .viability-challenging { background: #ffebee; border: 2px solid #c62828; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .risk-card { background: #f8f9fa; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem; }
    .risk-high { border-left: 4px solid #f44336; }
    .risk-medium { border-left: 4px solid #ff9800; }
    .risk-low { border-left: 4px solid #4caf50; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**GridFlow** evaluates whether a new asset can safely connect to the power grid, "
            "analyzing interconnection queue, capacity, and costs.")

st.markdown("""<div class="hero"><h1>GridFlow</h1>
<p>AI-powered grid interconnection analysis and feasibility assessment</p></div>""",
unsafe_allow_html=True)

with st.form("grid_form"):
    c1, c2 = st.columns(2)
    with c1:
        asset_type = st.selectbox("Asset Type",
            ["Solar Farm", "Wind Farm", "Battery Storage", "Data Center",
             "Solar + Battery Hybrid", "Wind + Battery Hybrid",
             "Natural Gas Peaker", "Hydrogen Electrolyzer"], index=0)
        capacity_mw = st.number_input("Capacity (MW)", min_value=1, max_value=5000, value=150)
        location = st.text_input("Location / Region", value="West Texas, near Midland-Odessa (ERCOT West zone)")
    with c2:
        grid_operator = st.selectbox("Grid Operator (ISO/RTO)",
            ["ERCOT", "CAISO", "PJM", "MISO", "SPP", "NYISO", "ISO-NE", "AESO", "Other"], index=0)
        voltage = st.selectbox("Interconnection Voltage (kV)",
            ["69", "115", "138", "230", "345", "500", "765"], index=2)
        online_date = st.text_input("Target Online Date", value="Q3 2027")

    additional_context = st.text_area("Additional Context (optional)", height=100,
        value="This is a 150MW single-axis tracking solar farm on 1,200 acres of leased ranch land. "
              "The site is approximately 3 miles from an existing 138kV transmission line. "
              "We have an executed land lease and preliminary environmental surveys complete. "
              "Looking for the most cost-effective and fastest path to interconnection. "
              "The project has a 20-year PPA with a major tech company for $28/MWh.")

    submitted = st.form_submit_button("Analyze Interconnection", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(asset_type=asset_type, capacity_mw=capacity_mw, location=location,
                  grid_operator=grid_operator, voltage=voltage, online_date=online_date,
                  additional_context=additional_context)

    with st.spinner("Analyzing grid interconnection..."):
        try:
            result = analyze_interconnection(config, api_key)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    # Financial Viability Banner
    fin = result.get("financial_impact", {})
    viability = fin.get("project_viability", "Viable")
    v_cls = f"viability-{viability.lower()}" if viability.lower() in ["strong", "viable", "marginal", "challenging"] else "viability-viable"
    st.markdown(f'<div class="{v_cls}"><span style="font-size:1.5rem;font-weight:bold">'
               f'Project Viability: {viability}</span><br/>'
               f'Estimated Interconnection Cost: ${result.get("cost_estimate", {}).get("total_estimated_cost_usd", 0):,.0f} '
               f'| Payback: {fin.get("payback_period_years", "N/A")} years</div>', unsafe_allow_html=True)

    # Queue & Capacity side by side
    qc1, qc2 = st.columns(2)
    queue = result.get("queue_position_analysis", {})
    if queue:
        with qc1:
            st.divider()
            st.subheader("Queue Position")
            st.markdown(f"**Queue Depth:** {queue.get('estimated_queue_depth', '')}")
            st.markdown(f"**Avg Wait:** {queue.get('average_wait_time_months', '')} months")
            st.markdown(f"**Queue Trend:** {queue.get('queue_trend', '')}")
            st.markdown(f"**Withdrawal Rate:** {queue.get('withdrawal_rate', '')}")
            st.markdown(f"**Assessment:** {queue.get('position_assessment', '')}")
            if queue.get("notes"):
                st.info(queue["notes"])

    capacity = result.get("grid_capacity_assessment", {})
    if capacity:
        with qc2:
            st.divider()
            st.subheader("Grid Capacity")
            gc1, gc2_ = st.columns(2)
            gc1.metric("Available Capacity", f"{capacity.get('available_capacity_mw', 0)} MW")
            gc2_.metric("Congestion", capacity.get("congestion_level", ""))
            st.markdown(f"**Thermal Limit:** {capacity.get('thermal_limit_mw', '')} MW")
            st.markdown(f"**Headroom:** {capacity.get('headroom_percentage', '')}%")
            st.markdown(f"**Assessment:** {capacity.get('assessment', '')}")

    # Timeline Gantt Chart
    timeline = result.get("timeline_projection", {})
    if timeline:
        st.divider()
        st.subheader(f"Timeline Projection (~{timeline.get('total_months', 'N/A')} months)")
        st.markdown(f"**Earliest Possible:** {timeline.get('earliest_possible_date', '')} | "
                   f"**Most Likely:** {timeline.get('most_likely_date', '')} | "
                   f"**Target Achievable:** {'Yes' if timeline.get('target_achievable') else 'No'}")

        phases = timeline.get("phases", [])
        if phases:
            # Plotly Gantt chart
            fig = go.Figure()
            colors = ["#1b5e20", "#0d47a1", "#e65100", "#6a1b9a", "#c62828",
                      "#00838f", "#f9a825", "#2e7d32", "#d84315", "#1565c0"]
            for i, phase in enumerate(phases):
                start = phase.get("start_month", 0)
                dur = phase.get("duration_months", 0)
                fig.add_trace(go.Bar(
                    name=phase.get("phase", f"Phase {i+1}"),
                    y=[phase.get("phase", f"Phase {i+1}")],
                    x=[dur],
                    base=[start],
                    orientation="h",
                    marker=dict(color=colors[i % len(colors)]),
                    text=f"{dur} mo",
                    textposition="inside",
                ))
            fig.update_layout(
                title="Interconnection Timeline (months)",
                xaxis_title="Months from Start",
                barmode="stack",
                height=max(300, len(phases) * 50),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

    # Cost Breakdown
    costs = result.get("cost_estimate", {})
    if costs:
        st.divider()
        st.subheader("Cost Estimate")
        co1, co2, co3 = st.columns(3)
        co1.metric("Total Cost", f"${costs.get('total_estimated_cost_usd', 0):,.0f}")
        co2.metric("Cost per MW", f"${costs.get('cost_per_mw', 0):,.0f}")
        co3.metric("Network Upgrades", f"${costs.get('network_upgrade_costs', 0):,.0f}")
        if costs.get("cost_breakdown_notes"):
            st.info(costs["cost_breakdown_notes"])

    # Upgrade Requirements
    upgrades = result.get("upgrade_requirements", [])
    if upgrades:
        st.divider()
        st.subheader("Upgrade Requirements")
        up_df = pd.DataFrame([{
            "Upgrade": u.get("upgrade", ""),
            "Category": u.get("category", ""),
            "Cost": f"${u.get('estimated_cost_usd', 0):,.0f}",
            "Timeline": f"{u.get('timeline_months', 0)} mo",
            "Responsible": u.get("responsible_party", ""),
            "Criticality": u.get("criticality", ""),
        } for u in upgrades])
        st.dataframe(up_df, use_container_width=True, hide_index=True)

    # Risk Factors
    risks = result.get("risk_factors", [])
    if risks:
        st.divider()
        st.subheader("Risk Factors")
        for r in risks:
            sev = r.get("severity", "Medium").lower()
            st.markdown(f'<div class="risk-card risk-{sev}"><strong>{r.get("risk", "")}</strong> '
                       f'(Severity: {r.get("severity", "")} | Probability: {r.get("probability", "")})<br/>'
                       f'Impact: {r.get("impact", "")}<br/>'
                       f'Mitigation: {r.get("mitigation", "")}</div>', unsafe_allow_html=True)

    # Comparable Projects
    comps = result.get("comparable_projects", [])
    if comps:
        st.divider()
        st.subheader("Comparable Projects")
        comp_df = pd.DataFrame([{
            "Project": c.get("project", ""),
            "Capacity": f"{c.get('capacity_mw', 0)} MW",
            "Region": c.get("region", ""),
            "IC Cost": f"${c.get('interconnection_cost_usd', 0):,.0f}",
            "Timeline": f"{c.get('timeline_months', 0)} mo",
            "Outcome": c.get("outcome", ""),
        } for c in comps])
        st.dataframe(comp_df, use_container_width=True, hide_index=True)

    # Optimization Recommendations
    opts = result.get("optimization_recommendations", [])
    if opts:
        st.divider()
        st.subheader("Optimization Recommendations")
        for o in opts:
            st.markdown(f"**{o.get('recommendation', '')}**")
            st.markdown(f"Impact: {o.get('impact', '')} | Savings: {o.get('estimated_savings', '')} "
                       f"| Effort: {o.get('implementation_effort', '')}")

    # Regulatory
    regs = result.get("regulatory_requirements", [])
    if regs:
        st.divider()
        st.subheader("Regulatory Requirements")
        reg_df = pd.DataFrame([{
            "Requirement": r.get("requirement", ""),
            "Authority": r.get("authority", ""),
            "Timeline": f"{r.get('timeline_months', 0)} mo",
            "Complexity": r.get("complexity", ""),
        } for r in regs])
        st.dataframe(reg_df, use_container_width=True, hide_index=True)

    # Financial Impact
    if fin:
        st.divider()
        st.subheader("Financial Impact")
        fi1, fi2, fi3 = st.columns(3)
        fi1.metric("Est. Annual Revenue", f"${fin.get('estimated_annual_revenue_usd', 0):,.0f}")
        fi2.metric("IC Cost as % of CapEx", f"{fin.get('interconnection_cost_as_pct_of_capex', 0)}%")
        fi3.metric("LCOE Impact", fin.get("lcoe_impact", ""))
        if fin.get("revenue_risk_factors"):
            st.markdown("**Revenue Risk Factors:**")
            for rf in fin["revenue_risk_factors"]:
                st.markdown(f"- {rf}")

    st.divider()
    st.download_button("Download Interconnection Report (JSON)", json.dumps(result, indent=2),
                       "interconnection_report.json", "application/json")
