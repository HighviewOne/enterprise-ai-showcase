"""Due Diligence Generator - M&A Technology Due Diligence - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.dd_engine import generate_diligence

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #0d47a1 0%, #1565c0 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .risk-card { background: #f8f9fa; border-radius: 10px; padding: 1.2rem; margin-bottom: 0.8rem; }
    .risk-low { border-left: 4px solid #4caf50; }
    .risk-medium { border-left: 4px solid #ff9800; }
    .risk-high { border-left: 4px solid #f44336; }
    .risk-critical { border-left: 4px solid #b71c1c; background: #ffebee; }
    .flag-green { background: #e8f5e9; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem;
        border-left: 4px solid #2e7d32; }
    .flag-red { background: #ffebee; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem;
        border-left: 4px solid #c62828; }
    .phase-card { background: #e3f2fd; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
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
    st.info("**DiligenceSphere** automates technology due diligence questionnaire generation, "
            "scoring, and reporting for M&A and investment deals.")

st.markdown("""<div class="hero"><h1>DiligenceSphere</h1>
<p>AI-powered technology due diligence for M&A — automated scoring, risk assessment, and deal recommendations</p></div>""",
unsafe_allow_html=True)

with st.form("dd_form"):
    company_profile = st.text_area("Target Company Profile", height=250,
        value="Company: DataFlow Analytics Inc.\n"
              "Founded: 2019 | Headquarters: Austin, TX\n"
              "Employees: 85 (40 engineering, 10 data science, 35 business)\n"
              "Product: Real-time data pipeline platform for enterprise ETL/ELT\n"
              "Tech Stack: Python/Go microservices, Kubernetes on AWS, Apache Kafka, PostgreSQL, React\n"
              "Revenue: $12M ARR, growing 80% YoY\n"
              "Customers: 45 enterprise clients (Fortune 500 includes 8)\n"
              "Architecture: Multi-tenant SaaS, SOC 2 Type II certified\n"
              "Code: ~350K lines, monorepo on GitHub Enterprise, 78% test coverage\n"
              "Team: CTO has 15yr experience, 3 PhDs on data science team\n"
              "Tech Debt: Legacy ingestion module (v1) needs rewrite, est. 3 months\n"
              "IP: 2 pending patents on streaming data transformation algorithms\n"
              "Security: Annual pentest, bug bounty program, no major incidents\n"
              "Concerns: Key-person dependency on CTO for architecture decisions\n"
              "DevOps: CI/CD via GitHub Actions, 15-min deploy cycle, 99.95% uptime SLA")

    c1, c2 = st.columns(2)
    with c1:
        deal_type = st.selectbox("Deal Type",
            ["Full Acquisition", "Majority Stake", "Minority Investment",
             "Merger", "Acqui-hire", "Strategic Partnership"])
        acquirer_industry = st.selectbox("Acquirer Industry",
            ["Technology/SaaS", "Financial Services", "Healthcare", "Manufacturing",
             "Consulting", "Private Equity", "Venture Capital"])
    with c2:
        deal_size = st.selectbox("Deal Size Range",
            ["$1M-$10M", "$10M-$50M", "$50M-$100M", "$100M-$500M", "$500M+"], index=2)
        rationale = st.text_input("Strategic Rationale",
            value="Acquire best-in-class data pipeline technology to enhance our enterprise data platform offering.")
    focus = st.text_input("Due Diligence Focus",
        value="Technology architecture, scalability, team retention risk, IP portfolio, integration feasibility.")

    submitted = st.form_submit_button("Generate Due Diligence Report", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        company_profile=company_profile, deal_type=deal_type,
        acquirer_industry=acquirer_industry, deal_size=deal_size,
        rationale=rationale, focus=focus,
    )

    with st.spinner("Generating due diligence report..."):
        try:
            result = generate_diligence(config, api_key)
        except Exception as e:
            st.error(f"Report generation failed: {e}")
            st.stop()

    # Executive Summary
    exec_sum = result.get("executive_summary", {})
    score = exec_sum.get("overall_score", 50)

    st.subheader("Executive Summary")
    ec1, ec2 = st.columns([1, 2])
    with ec1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": "Overall Score"},
            gauge={"axis": {"range": [0, 100]},
                   "bar": {"color": "#4caf50" if score >= 70 else "#ff9800" if score >= 40 else "#f44336"},
                   "steps": [{"range": [0, 40], "color": "#ffebee"},
                             {"range": [40, 70], "color": "#fff3e0"},
                             {"range": [70, 100], "color": "#e8f5e9"}]},
        ))
        fig.update_layout(height=250, margin=dict(t=40, b=0, l=30, r=30))
        st.plotly_chart(fig, use_container_width=True)

    with ec2:
        em1, em2 = st.columns(2)
        em1.metric("Rating", exec_sum.get("rating", ""))
        rec = exec_sum.get("deal_recommendation", "")
        rec_color = "#4caf50" if "Proceed" in rec and "Condition" not in rec else "#f44336" if "Not" in rec else "#ff9800"
        em2.metric("Recommendation", rec)
        st.info(f"**{exec_sum.get('headline', '')}**")
        for f in exec_sum.get("key_findings", []):
            st.markdown(f"- {f}")

    # Technology Assessment
    tech = result.get("technology_assessment", [])
    if tech:
        st.divider()
        st.subheader("Technology Assessment")

        cats = [t.get("area", "")[:15] for t in tech]
        scores = [t.get("score", 5) for t in tech]
        fig_radar = go.Figure(go.Scatterpolar(
            r=scores + [scores[0]], theta=cats + [cats[0]],
            fill="toself", fillcolor="rgba(21, 101, 192, 0.2)", line_color="#1565c0",
        ))
        fig_radar.update_layout(polar=dict(radialaxis=dict(range=[0, 10])),
                                title="Technology Scores", height=350)
        st.plotly_chart(fig_radar, use_container_width=True)

        for t in tech:
            s = t.get("score", 5)
            cls = "risk-low" if s >= 7 else "risk-high" if s <= 3 else "risk-medium"
            st.markdown(f'<div class="risk-card {cls}"><strong>{t.get("area", "")}</strong> — '
                       f'Score: {s}/10 | {t.get("rating", "")}</div>', unsafe_allow_html=True)
            with st.expander(f"Details: {t.get('area', '')}"):
                st.markdown(t.get("findings", ""))
                if t.get("risks"):
                    st.markdown("**Risks:**")
                    for r in t["risks"]:
                        st.warning(r)
                for rec in t.get("recommendations", []):
                    st.markdown(f"- {rec}")

    # DD Questionnaire
    quest = result.get("questionnaire", [])
    if quest:
        st.divider()
        st.subheader("Due Diligence Questionnaire")
        for cat in quest:
            with st.expander(f"📋 {cat.get('category', '')} ({len(cat.get('questions', []))} questions)"):
                for q in cat.get("questions", []):
                    pri = q.get("priority", "Important")
                    pri_color = "#f44336" if pri == "Critical" else "#ff9800" if pri == "Important" else "#4caf50"
                    st.markdown(f'<span style="color:{pri_color};font-weight:bold">[{pri}]</span> '
                               f'{q.get("question", "")}', unsafe_allow_html=True)
                    st.caption(f"Evidence: {q.get('expected_evidence', '')}")

    # Risk Register
    risks = result.get("risk_register", [])
    if risks:
        st.divider()
        st.subheader("Risk Register")
        risk_df = pd.DataFrame([{
            "Risk": r.get("risk", ""),
            "Category": r.get("category", ""),
            "Likelihood": r.get("likelihood", ""),
            "Impact": r.get("impact", ""),
            "Deal Impact": r.get("deal_impact", ""),
        } for r in risks])
        st.dataframe(risk_df, use_container_width=True, hide_index=True)

    # Valuation Impact
    val = result.get("valuation_impact", {})
    if val:
        st.divider()
        st.subheader("Valuation Impact")
        vc1, vc2 = st.columns(2)
        with vc1:
            st.markdown("**Premium Factors:**")
            for p in val.get("tech_premium_factors", []):
                st.markdown(f'<div class="flag-green">{p}</div>', unsafe_allow_html=True)
        with vc2:
            st.markdown("**Discount Factors:**")
            for d in val.get("tech_discount_factors", []):
                st.markdown(f'<div class="flag-red">{d}</div>', unsafe_allow_html=True)
        vm1, vm2, vm3 = st.columns(3)
        vm1.metric("Est. Tech Debt Cost", val.get("estimated_tech_debt_cost", "N/A"))
        vm2.metric("Integration Complexity", val.get("integration_complexity", "N/A"))
        vm3.metric("Est. Integration Cost", val.get("estimated_integration_cost", "N/A"))

    # Red / Green Flags
    rf = result.get("red_flags", [])
    gf = result.get("green_flags", [])
    if rf or gf:
        st.divider()
        st.subheader("Deal Signals")
        fg1, fg2 = st.columns(2)
        with fg1:
            st.markdown("**Green Flags:**")
            for g in gf:
                st.markdown(f'<div class="flag-green">{g}</div>', unsafe_allow_html=True)
        with fg2:
            st.markdown("**Red Flags:**")
            for r in rf:
                st.markdown(f'<div class="flag-red">{r}</div>', unsafe_allow_html=True)

    # Post-Acquisition Roadmap
    roadmap = result.get("post_acquisition_roadmap", [])
    if roadmap:
        st.divider()
        st.subheader("Post-Acquisition Roadmap")
        for r in roadmap:
            st.markdown(f'<div class="phase-card"><strong>{r.get("phase", "")}</strong> '
                       f'(Est. {r.get("estimated_cost", "TBD")}) — {r.get("priority", "")}</div>',
                       unsafe_allow_html=True)
            for a in r.get("actions", []):
                st.markdown(f"  - {a}")

    st.divider()
    st.download_button("Download DD Report (JSON)", json.dumps(result, indent=2),
                       "due_diligence_report.json", "application/json")
