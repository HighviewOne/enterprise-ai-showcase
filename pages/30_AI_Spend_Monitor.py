"""AI Spend Monitor - FinOps Anomaly Detection - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.spend_engine import analyze_spend

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #1a237e 0%, #4a148c 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: #ffd54f; margin: 0; }
    .hero p { color: #e0e0e0; }
    .anomaly-card { background: #f8f9fa; border-radius: 10px; padding: 1.2rem; margin-bottom: 0.8rem; }
    .sev-critical { border-left: 4px solid #b71c1c; background: #ffebee; }
    .sev-high { border-left: 4px solid #f44336; }
    .sev-medium { border-left: 4px solid #ff9800; }
    .sev-low { border-left: 4px solid #2196f3; }
    .savings-tag { background: #e8f5e9; color: #2e7d32; padding: 0.2rem 0.5rem;
        border-radius: 20px; font-weight: bold; font-size: 0.85rem; }
    .action-card { background: #fff3e0; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
        border-left: 4px solid #e65100; }
    .opt-card { background: #e3f2fd; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
        border-left: 4px solid #1565c0; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**Heimdall FinOps** — AI-powered spend intelligence that detects billing "
            "anomalies, identifies savings, and coordinates resolution.")

st.markdown("""<div class="hero"><h1>AI Spend Monitor</h1>
<p>Detect billing anomalies, flag unexpected charges, and optimise cloud/SaaS spend</p></div>""",
unsafe_allow_html=True)

sample_data = ""
try:
    with open("examples/sample_spend_data.txt") as f:
        sample_data = f.read()
except FileNotFoundError:
    pass

with st.form("spend_form"):
    spend_data = st.text_area("Spend Data", value=sample_data, height=350,
                               placeholder="Paste vendor spend logs, invoices, or billing summaries...")
    c1, c2 = st.columns(2)
    with c1:
        period = st.text_input("Analysis Period", value="January 2025")
        budget = st.number_input("Monthly Budget ($)", value=185000, step=5000)
        department = st.selectbox("Department",
            ["All Departments", "Engineering", "Marketing", "Sales",
             "Operations", "Finance", "Product"])
    with c2:
        threshold = st.slider("Alert Threshold (%)", 10, 50, 20)
        focus_areas = st.multiselect("Focus Areas",
            ["Cloud Infrastructure", "SaaS Subscriptions", "Consulting/Services",
             "Hardware", "Travel", "Marketing Spend"],
            default=["Cloud Infrastructure", "SaaS Subscriptions", "Consulting/Services"])
        context = st.text_input("Additional Context",
            value="Q1 cost review. New vendor onboarding policy requires PO for >$10K.")

    submitted = st.form_submit_button("Analyse Spend", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        spend_data=spend_data, period=period, budget=budget,
        department=department, threshold=threshold,
        focus_areas=", ".join(focus_areas), context=context,
    )

    with st.spinner("Analysing spend data..."):
        try:
            result = analyze_spend(config, api_key)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    # Spend Summary
    summary = result.get("spend_summary", {})
    st.subheader("Spend Overview")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Spend", summary.get("total_spend", "$0"))
    m2.metric("Budget", summary.get("baseline_budget", "$0"))
    var = summary.get("variance_pct", 0)
    m3.metric("Variance", f"{var:+.1f}%" if isinstance(var, (int, float)) else str(var))
    m4.metric("Anomalies", summary.get("anomaly_count", 0))
    exec_sum = result.get("executive_summary", {})
    m5.metric("Potential Savings", exec_sum.get("total_potential_savings", "$0"))

    # Category Breakdown charts
    cats = result.get("category_breakdown", [])
    if cats:
        ch1, ch2 = st.columns(2)
        with ch1:
            fig_cat = go.Figure(go.Pie(
                labels=[c.get("category", "") for c in cats],
                values=[float(str(c.get("spend", "0")).replace("$", "").replace(",", ""))
                        for c in cats],
                hole=0.4,
            ))
            fig_cat.update_layout(title="Spend by Category", height=300)
            st.plotly_chart(fig_cat, use_container_width=True)

        with ch2:
            cat_names = [c.get("category", "")[:20] for c in cats]
            spends = []
            budgets = []
            for c in cats:
                s = str(c.get("spend", "0")).replace("$", "").replace(",", "")
                b = str(c.get("budget", "0")).replace("$", "").replace(",", "")
                try:
                    spends.append(float(s))
                except ValueError:
                    spends.append(0)
                try:
                    budgets.append(float(b))
                except ValueError:
                    budgets.append(0)
            fig_bar = go.Figure()
            fig_bar.add_trace(go.Bar(name="Actual", x=cat_names, y=spends, marker_color="#f44336"))
            fig_bar.add_trace(go.Bar(name="Budget", x=cat_names, y=budgets, marker_color="#4caf50"))
            fig_bar.update_layout(title="Spend vs Budget", barmode="group", height=300)
            st.plotly_chart(fig_bar, use_container_width=True)

    st.info(f"**Key Finding:** {summary.get('key_finding', '')}")

    # Anomalies
    anomalies = result.get("anomalies", [])
    if anomalies:
        st.divider()
        st.subheader(f"Anomalies Detected ({len(anomalies)})")

        sev_counts = {}
        for a in anomalies:
            s = a.get("severity", "Medium")
            sev_counts[s] = sev_counts.get(s, 0) + 1
        sc1, sc2, sc3, sc4 = st.columns(4)
        sc1.metric("Critical", sev_counts.get("Critical", 0))
        sc2.metric("High", sev_counts.get("High", 0))
        sc3.metric("Medium", sev_counts.get("Medium", 0))
        sc4.metric("Low", sev_counts.get("Low", 0))

        for a in sorted(anomalies, key=lambda x: {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}.get(x.get("severity", "Medium"), 2)):
            sev = a.get("severity", "Medium")
            cls = f"sev-{sev.lower()}"
            savings = a.get("estimated_savings", "$0")
            st.markdown(f"""<div class="anomaly-card {cls}">
                <strong>{a.get('vendor', '')}</strong> — {a.get('anomaly_type', '')}
                <span style="float:right"><span class="savings-tag">Save {savings}</span></span><br/>
                Amount: <strong>{a.get('amount', '')}</strong> (expected {a.get('expected_amount', '')})
                | Variance: {a.get('variance_pct', 0)}% | Priority: {a.get('priority', 'P1')}
            </div>""", unsafe_allow_html=True)

            with st.expander(f"Details: {a.get('vendor', '')}"):
                st.markdown(f"**Root Cause:** {a.get('root_cause_hypothesis', '')}")
                st.markdown(f"**Recommended Action:** {a.get('recommended_action', '')}")
                st.markdown(f"**Category:** {a.get('category', '')}")

    # Vendor Analysis
    vendors = result.get("vendor_analysis", [])
    if vendors:
        st.divider()
        st.subheader("Vendor Analysis")
        v_df = pd.DataFrame([{
            "Vendor": v.get("vendor", ""),
            "Spend": v.get("total_spend", ""),
            "Trend": v.get("trend", ""),
            "Contract": v.get("contract_status", ""),
            "Risk": v.get("risk_level", ""),
            "Notes": v.get("notes", ""),
        } for v in vendors])
        st.dataframe(v_df, use_container_width=True, hide_index=True)

    # Cost Optimization
    opts = result.get("cost_optimization", [])
    if opts:
        st.divider()
        st.subheader("Cost Optimisation Opportunities")
        for i, o in enumerate(opts, 1):
            effort = o.get("effort", "Medium")
            effort_color = "#4caf50" if effort == "Low" else "#f44336" if effort == "High" else "#ff9800"
            st.markdown(f'<div class="opt-card"><strong>#{i} {o.get("opportunity", "")}</strong><br/>'
                       f'<span class="savings-tag">Save {o.get("estimated_savings", "")}</span> '
                       f'| Effort: <span style="color:{effort_color};font-weight:bold">{effort}</span><br/>'
                       f'{o.get("recommendation", "")}</div>', unsafe_allow_html=True)

    # Resolution Actions
    actions = result.get("resolution_actions", [])
    if actions:
        st.divider()
        st.subheader("Resolution Actions")
        act_df = pd.DataFrame([{
            "Action": a.get("action", ""),
            "Owner": a.get("owner", ""),
            "Priority": a.get("priority", ""),
            "Status": a.get("status", "Open"),
            "Deadline": a.get("deadline", ""),
        } for a in actions])
        st.dataframe(act_df, use_container_width=True, hide_index=True)

    # Trend Analysis
    trend = result.get("trend_analysis", {})
    if trend:
        monthly = trend.get("monthly_trend", [])
        if monthly:
            st.divider()
            st.subheader("Spend Trend")
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=[m.get("month", "") for m in monthly],
                y=[m.get("spend", 0) for m in monthly],
                mode="lines+markers",
                line_color="#1565c0",
                name="Monthly Spend",
            ))
            fig_trend.update_layout(title="Monthly Spend Trend", height=300)
            st.plotly_chart(fig_trend, use_container_width=True)
            st.caption(f"Forecast: {trend.get('forecast_next_month', 'N/A')} | "
                      f"{trend.get('yoy_comparison', '')}")

    # Executive Summary
    if exec_sum:
        st.divider()
        st.subheader("Executive Summary")
        risk_rating = exec_sum.get("risk_rating", "Medium")
        risk_color = "#f44336" if risk_rating in ("Critical", "High") else "#ff9800" if risk_rating == "Medium" else "#4caf50"
        st.markdown(f'Risk Rating: <span style="color:{risk_color};font-weight:bold;font-size:1.2rem">'
                   f'{risk_rating}</span>', unsafe_allow_html=True)
        st.info(exec_sum.get("one_liner", ""))
        st.markdown("**Top Actions:**")
        for a in exec_sum.get("top_actions", []):
            st.markdown(f"1. {a}")

    st.divider()
    st.download_button("Download Spend Report (JSON)", json.dumps(result, indent=2),
                       "spend_analysis.json", "application/json")
