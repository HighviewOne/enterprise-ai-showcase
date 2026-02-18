"""Customer Insights Engine (CUE) - Unified Customer Intelligence - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.insights_engine import analyze_insights

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #006064 0%, #00838f 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .theme-card { background: #f8f9fa; border-radius: 10px; padding: 1.2rem; margin-bottom: 0.8rem; }
    .theme-pos { border-left: 4px solid #4caf50; }
    .theme-neg { border-left: 4px solid #f44336; }
    .theme-mix { border-left: 4px solid #ff9800; }
    .theme-neu { border-left: 4px solid #9e9e9e; }
    .seg-card { background: #e8eaf6; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
        border-left: 4px solid #3f51b5; }
    .churn-card { background: #ffebee; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
        border-left: 4px solid #c62828; }
    .rec-card { background: #e3f2fd; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
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
    st.info("**CUE** synthesises fragmented customer data into unified, actionable insights "
            "for product, marketing, and leadership teams.")

st.markdown("""<div class="hero"><h1>CUE - Customer Understanding Engine</h1>
<p>Unify CRM, support tickets, surveys, and call transcripts into actionable customer intelligence</p></div>""",
unsafe_allow_html=True)

with st.form("insights_form"):
    customer_data = st.text_area("Customer Data (paste from any sources)", height=300,
        value="=== CRM NOTES (Last 90 Days) ===\n"
              "Account: TechPro Corp ($120K ARR) - Champion left company, new stakeholder skeptical\n"
              "Account: MedStar Health ($85K ARR) - Requested enterprise SSO integration, timeline concerns\n"
              "Account: RetailMax ($200K ARR) - Expanded to 3 new regions, very satisfied\n"
              "Account: FinanceHub ($95K ARR) - Exploring competitor DataVault, pricing concerns\n\n"
              "=== SUPPORT TICKETS (Top Issues) ===\n"
              "TICKET-4521: Dashboard loading takes 30+ seconds with large datasets (5 reports)\n"
              "TICKET-4498: API rate limits too restrictive for enterprise workflows (3 reports)\n"
              "TICKET-4512: 'Export to PDF' formatting broken in latest release (8 reports)\n"
              "TICKET-4530: SSO/SAML integration documentation incomplete\n"
              "TICKET-4545: Data refresh stuck at 99% - needs manual restart (4 reports)\n\n"
              "=== NPS SURVEY RESPONSES (Q4) ===\n"
              "NPS Score: 42 (down from 51 in Q3)\n"
              "\"Love the product but the performance has gotten worse\" - Score 7\n"
              "\"Best analytics tool we've used, wish pricing was more transparent\" - Score 8\n"
              "\"Support response time used to be great, now takes 2 days\" - Score 5\n"
              "\"Missing features our team needs, considering alternatives\" - Score 4\n"
              "\"Onboarding was excellent, team adopted it quickly\" - Score 9\n\n"
              "=== CALL TRANSCRIPT EXCERPTS ===\n"
              "FinanceHub QBR: \"We like the product but DataVault is offering 30% less. We need \n"
              "to see the value to justify the renewal.\"\n"
              "MedStar Escalation: \"HIPAA compliance documentation is lacking. We need SOC2 \n"
              "report and BAA before we can expand usage.\"\n"
              "RetailMax Success: \"Your real-time dashboards saved us $2M in inventory costs. \n"
              "We want to roll this out to all 12 locations.\"")

    c1, c2 = st.columns(2)
    with c1:
        company = st.text_input("Your Company", value="InsightFlow Analytics")
        product = st.text_input("Product/Service", value="InsightFlow - Real-Time Business Analytics Platform")
    with c2:
        period = st.text_input("Analysis Period", value="Q4 2024 (October - December)")
        focus = st.text_input("Analysis Focus",
            value="Churn risk, NPS decline root cause, product priorities, competitive positioning")

    submitted = st.form_submit_button("Generate Insights", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(customer_data=customer_data, company=company,
                  product=product, period=period, focus=focus)

    with st.spinner("Synthesising customer intelligence..."):
        try:
            result = analyze_insights(config, api_key)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    # Overview
    overview = result.get("customer_overview", {})
    st.subheader("Customer Intelligence Overview")
    om1, om2, om3, om4 = st.columns(4)
    om1.metric("Data Points", overview.get("total_data_points", 0))
    om2.metric("Time Span", overview.get("time_span", ""))
    om3.metric("Sentiment Trend", overview.get("sentiment_trend", ""))
    sent = result.get("sentiment_analysis", {})
    om4.metric("Sentiment Score", f"{sent.get('overall_score', 0)}/10")
    st.info(f"**Key Insight:** {overview.get('key_insight', '')}")

    # Executive Brief
    brief = result.get("executive_brief", "")
    if brief:
        st.success(f"**Executive Brief:** {brief}")

    # Themes
    themes = result.get("themes", [])
    if themes:
        st.divider()
        st.subheader(f"Key Themes ({len(themes)})")
        for t in themes:
            s = t.get("sentiment", "Neutral")
            cls = ("theme-pos" if s == "Positive" else "theme-neg" if s == "Negative"
                   else "theme-mix" if s == "Mixed" else "theme-neu")
            st.markdown(f'<div class="theme-card {cls}"><strong>{t.get("theme", "")}</strong> '
                       f'({s}) — Frequency: {t.get("frequency", "")}<br/>'
                       f'Impact: {t.get("business_impact", "")}</div>', unsafe_allow_html=True)
            with st.expander(f"Details: {t.get('theme', '')}"):
                if t.get("evidence"):
                    for e in t["evidence"]:
                        st.caption(f'"{e}"')
                st.markdown(f"**Action:** {t.get('recommended_action', '')}")

    # Sentiment Analysis
    if sent:
        st.divider()
        st.subheader("Sentiment Analysis")
        sc1, sc2 = st.columns(2)
        with sc1:
            if sent.get("positive_drivers"):
                st.markdown("**What Customers Love:**")
                for p in sent["positive_drivers"]:
                    st.markdown(f"- {p}")
        with sc2:
            if sent.get("negative_drivers"):
                st.markdown("**What Customers Dislike:**")
                for n in sent["negative_drivers"]:
                    st.markdown(f"- {n}")

    # Customer Segments
    segments = result.get("customer_segments", [])
    if segments:
        st.divider()
        st.subheader("Customer Segments")
        for s in segments:
            risk = s.get("retention_risk", "Medium")
            risk_color = "#f44336" if risk == "High" else "#ff9800" if risk == "Medium" else "#4caf50"
            st.markdown(f'<div class="seg-card"><strong>{s.get("segment", "")}</strong> '
                       f'({s.get("size", "")}) — Retention Risk: '
                       f'<span style="color:{risk_color};font-weight:bold">{risk}</span></div>',
                       unsafe_allow_html=True)
            with st.expander(f"Segment: {s.get('segment', '')}"):
                sc1, sc2 = st.columns(2)
                with sc1:
                    st.markdown("**Needs:**")
                    for n in s.get("needs", []):
                        st.markdown(f"- {n}")
                with sc2:
                    st.markdown("**Pain Points:**")
                    for p in s.get("pain_points", []):
                        st.markdown(f"- {p}")
                st.markdown(f"**Opportunity:** {s.get('opportunity', '')}")

    # Product Feedback
    feedback = result.get("product_feedback", [])
    if feedback:
        st.divider()
        st.subheader("Product Feedback")
        fb_df = pd.DataFrame([{
            "Area": f.get("feature_area", ""),
            "Type": f.get("feedback_type", ""),
            "Frequency": f.get("frequency", 0),
            "Summary": f.get("summary", ""),
            "Priority": f.get("priority", ""),
        } for f in feedback])
        st.dataframe(fb_df, use_container_width=True, hide_index=True)

    # Churn Signals
    churn = result.get("churn_signals", [])
    if churn:
        st.divider()
        st.subheader("Churn Risk Signals")
        for c in churn:
            urg = c.get("urgency", "Watch")
            icon = "🔴" if urg == "Immediate" else "🟡" if urg == "Near-term" else "🟢"
            st.markdown(f'<div class="churn-card">{icon} <strong>{c.get("signal", "")}</strong><br/>'
                       f'Segment: {c.get("affected_segment", "")} | Urgency: {urg}<br/>'
                       f'Intervention: {c.get("intervention", "")}</div>', unsafe_allow_html=True)

    # Competitive Intelligence
    comp = result.get("competitive_intelligence", {})
    if comp:
        st.divider()
        st.subheader("Competitive Intelligence")
        cc1, cc2 = st.columns(2)
        with cc1:
            if comp.get("loyalty_drivers"):
                st.markdown("**Why Customers Stay:**")
                for l in comp["loyalty_drivers"]:
                    st.markdown(f"- {l}")
        with cc2:
            if comp.get("switching_risk_factors"):
                st.markdown("**Switching Risk Factors:**")
                for s in comp["switching_risk_factors"]:
                    st.warning(s)
        mentions = comp.get("competitor_mentions", [])
        if mentions:
            for m in mentions:
                st.caption(f"**{m.get('competitor', '')}:** {m.get('context', '')} ({m.get('sentiment', '')})")

    # Strategic Recommendations
    recs = result.get("strategic_recommendations", [])
    if recs:
        st.divider()
        st.subheader("Strategic Recommendations")
        for i, r in enumerate(recs, 1):
            effort = r.get("effort", "Medium")
            eff_color = "#4caf50" if effort == "Low" else "#f44336" if effort == "High" else "#ff9800"
            st.markdown(f'<div class="rec-card"><strong>#{i} {r.get("recommendation", "")}</strong><br/>'
                       f'Impact: {r.get("expected_impact", "")} | '
                       f'Effort: <span style="color:{eff_color};font-weight:bold">{effort}</span> | '
                       f'Timeline: {r.get("timeline", "")}<br/>'
                       f'<em>Evidence: {r.get("supporting_data", "")}</em></div>',
                       unsafe_allow_html=True)

    st.divider()
    st.download_button("Download Insights Report (JSON)", json.dumps(result, indent=2),
                       "customer_insights.json", "application/json")
