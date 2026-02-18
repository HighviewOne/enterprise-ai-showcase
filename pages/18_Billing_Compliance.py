"""Billing Compliance Assistant (LuminaClaims) - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.billing_engine import review_billing

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #37474f 0%, #546e7a 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .flag-card { background: #f8f9fa; border-radius: 10px; padding: 1rem; margin-bottom: 0.6rem; }
    .sev-high { border-left: 4px solid #f44336; }
    .sev-med { border-left: 4px solid #ff9800; }
    .sev-low { border-left: 4px solid #4caf50; }
    .rewrite-box { background: #e8f5e9; border-radius: 6px; padding: 0.5rem;
        margin-top: 0.3rem; font-style: italic; }
    .score-good { color: #4caf50; font-weight: bold; }
    .score-warn { color: #ff9800; font-weight: bold; }
    .score-bad { color: #f44336; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input

st.markdown("""<div class="hero"><h1>LuminaClaims</h1>
<p>AI-powered billing compliance review — flag violations, rewrite vague entries, and reduce client pushback</p></div>""",
unsafe_allow_html=True)

# Load sample files
sample_log = ""
sample_guidelines = ""
try:
    with open("examples/sample_billing_log.txt") as f:
        sample_log = f.read()
    with open("examples/sample_billing_guidelines.txt") as f:
        sample_guidelines = f.read()
except FileNotFoundError:
    pass

with st.form("billing_form"):
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Billing Guidelines")
        guidelines = st.text_area("Paste billing guidelines / outside counsel guidelines",
                                   value=sample_guidelines, height=250)
    with c2:
        st.subheader("Billing Log")
        billing_log = st.text_area("Paste billing entries (date, attorney, hours, description)",
                                    value=sample_log, height=250)

    context = st.text_input("Review Context",
        value="Monthly pre-bill review for January 2025. Focus on vague descriptions and excessive hours.")

    submitted = st.form_submit_button("Review Billing Entries", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()
    if not guidelines.strip() or not billing_log.strip():
        st.error("Both guidelines and billing log are required.")
        st.stop()

    config = dict(guidelines=guidelines, billing_log=billing_log, context=context)

    with st.spinner("Reviewing billing entries for compliance..."):
        try:
            result = review_billing(config, api_key)
        except Exception as e:
            st.error(f"Review failed: {e}")
            st.stop()

    # Summary metrics
    summary = result.get("summary", {})
    st.subheader("Review Summary")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Entries", summary.get("total_entries", 0))
    m2.metric("Total Hours", f"{summary.get('total_hours', 0):.1f}")
    m3.metric("Total Billed", f"${summary.get('total_amount', 0):,.0f}")
    m4.metric("Flagged", f"{summary.get('flagged_entries', 0)} ({summary.get('violation_rate_pct', 0):.0f}%)",
              delta=f"-${summary.get('estimated_write_off', 0):,.0f} at risk",
              delta_color="inverse")

    # Violation breakdown chart
    flagged = result.get("flagged_items", [])
    if flagged:
        violation_types = {}
        severities = {"High": 0, "Medium": 0, "Low": 0}
        for f in flagged:
            vt = f.get("violation_type", "Other")
            violation_types[vt] = violation_types.get(vt, 0) + 1
            sev = f.get("severity", "Medium")
            severities[sev] = severities.get(sev, 0) + 1

        fig_col1, fig_col2 = st.columns(2)
        with fig_col1:
            fig_vt = go.Figure(go.Pie(
                labels=list(violation_types.keys()),
                values=list(violation_types.values()),
                hole=0.4,
            ))
            fig_vt.update_layout(title="Violations by Type", height=300)
            st.plotly_chart(fig_vt, use_container_width=True)

        with fig_col2:
            fig_sev = go.Figure(go.Bar(
                x=list(severities.keys()),
                y=list(severities.values()),
                marker_color=["#f44336", "#ff9800", "#4caf50"],
            ))
            fig_sev.update_layout(title="Violations by Severity", height=300)
            st.plotly_chart(fig_sev, use_container_width=True)

    # Flagged Items
    if flagged:
        st.divider()
        st.subheader(f"Flagged Entries ({len(flagged)})")
        for item in flagged:
            sev = item.get("severity", "Medium")
            sev_cls = "sev-high" if sev == "High" else "sev-low" if sev == "Low" else "sev-med"
            sev_emoji = "🔴" if sev == "High" else "🟡" if sev == "Medium" else "🟢"

            st.markdown(f"""<div class="flag-card {sev_cls}">
                {sev_emoji} <strong>{item.get('entry_ref', '')}</strong>
                — <em>{item.get('violation_type', '')}</em>
                — Action: <strong>{item.get('recommended_action', '')}</strong>
                — At risk: <strong>${item.get('amount_at_risk', 0):,.0f}</strong><br/>
                <strong>Original:</strong> "{item.get('original_description', '')}"<br/>
                <strong>Issue:</strong> {item.get('issue', '')}
                <div class="rewrite-box">
                    <strong>Suggested rewrite:</strong> {item.get('suggested_rewrite', '')}
                </div>
            </div>""", unsafe_allow_html=True)

    # Attorney Summary
    attorneys = result.get("attorney_summary", [])
    if attorneys:
        st.divider()
        st.subheader("Attorney Compliance Scores")
        att_df = pd.DataFrame([{
            "Attorney": a.get("attorney", ""),
            "Hours": f"{a.get('total_hours', 0):.1f}",
            "Billed": f"${a.get('total_billed', 0):,.0f}",
            "Violations": a.get("violations", 0),
            "Score": f"{a.get('compliance_score', 0)}%",
            "Primary Issue": a.get("primary_issue", "N/A"),
        } for a in attorneys])
        st.dataframe(att_df, use_container_width=True, hide_index=True)

        # Score bar chart
        fig_att = go.Figure(go.Bar(
            x=[a.get("attorney", "") for a in attorneys],
            y=[a.get("compliance_score", 0) for a in attorneys],
            marker_color=["#4caf50" if a.get("compliance_score", 0) >= 80
                          else "#ff9800" if a.get("compliance_score", 0) >= 60
                          else "#f44336" for a in attorneys],
            text=[f"{a.get('compliance_score', 0)}%" for a in attorneys],
            textposition="outside",
        ))
        fig_att.update_layout(title="Compliance Score by Attorney", height=300,
                               yaxis_range=[0, 100])
        st.plotly_chart(fig_att, use_container_width=True)

    # Client Summary
    clients = result.get("client_summary", [])
    if clients:
        st.divider()
        st.subheader("Client Risk Summary")
        cl_df = pd.DataFrame([{
            "Client": c.get("client", ""),
            "Hours": f"{c.get('total_hours', 0):.1f}",
            "Billed": f"${c.get('total_billed', 0):,.0f}",
            "At Risk": f"${c.get('flagged_amount', 0):,.0f}",
            "Risk Level": c.get("risk_level", "N/A"),
        } for c in clients])
        st.dataframe(cl_df, use_container_width=True, hide_index=True)

    # Trends & Recommendations
    trends = result.get("compliance_trends", {})
    recs = result.get("top_recommendations", [])
    if trends or recs:
        st.divider()
        tr1, tr2 = st.columns(2)
        with tr1:
            st.subheader("Compliance Trends")
            if trends.get("most_common_violation"):
                st.warning(f"**Most common violation:** {trends['most_common_violation']}")
            if trends.get("highest_risk_matter"):
                st.error(f"**Highest risk matter:** {trends['highest_risk_matter']}")
            for t in trends.get("training_needs", []):
                st.info(f"Training needed: {t}")
        with tr2:
            st.subheader("Top Recommendations")
            for r in recs:
                st.markdown(f"- {r}")

    # Export
    st.divider()
    st.download_button("Download Compliance Report (JSON)", json.dumps(result, indent=2),
                       "billing_compliance_report.json", "application/json")
