"""RegWatch - Compliance Intelligence System - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.regtech_engine import analyze_regulation

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #1b5e20 0%, #004d40 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: #a5d6a7; margin: 0; }
    .score-high { background: #e8f5e9; border: 2px solid #2e7d32; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .score-medium { background: #fff3e0; border: 2px solid #e65100; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .score-low { background: #ffebee; border: 2px solid #c62828; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .gap-card { background: #f8f9fa; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem; }
    .gap-critical { border-left: 4px solid #d32f2f; }
    .gap-high { border-left: 4px solid #f57c00; }
    .gap-medium { border-left: 4px solid #fbc02d; }
    .gap-low { border-left: 4px solid #4caf50; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**RegWatch** analyzes regulations against your organization's profile "
            "and generates comprehensive compliance intelligence reports.")

st.markdown("""<div class="hero"><h1>RegWatch</h1>
<p>AI-powered compliance intelligence and regulation impact analysis</p></div>""",
unsafe_allow_html=True)

with st.form("regtech_form"):
    org_profile = st.text_area("Organization Profile", height=150,
        value="Organization: Meridian Financial Services Group\n"
              "Type: Mid-size financial services firm (bank holding company)\n"
              "Employees: 2,500 across EU operations\n"
              "HQ: Frankfurt, Germany | Branches: London, Paris, Amsterdam, Dublin\n"
              "Assets Under Management: EUR 18 billion\n"
              "Services: Retail banking, corporate lending, investment management,\n"
              "digital payments platform, mobile banking app\n"
              "IT Infrastructure: Hybrid cloud (Azure + on-premises), 45 critical\n"
              "ICT systems, 12 third-party ICT providers including cloud, core banking\n"
              "vendor, and payment processing partners")

    regulation_text = st.text_area("Regulation to Analyze", height=200,
        value="Digital Operational Resilience Act (DORA) - EU Regulation 2022/2554\n\n"
              "DORA establishes a comprehensive framework for digital operational resilience\n"
              "in the EU financial sector. Key requirements include:\n\n"
              "1. ICT Risk Management (Articles 5-16): Financial entities must establish and\n"
              "   maintain resilient ICT systems with comprehensive risk management frameworks,\n"
              "   identification of critical functions, and protection/prevention measures.\n\n"
              "2. ICT Incident Reporting (Articles 17-23): Mandatory classification and reporting\n"
              "   of major ICT-related incidents to competent authorities within strict timelines.\n\n"
              "3. Digital Operational Resilience Testing (Articles 24-27): Regular testing including\n"
              "   threat-led penetration testing (TLPT) for significant entities every 3 years.\n\n"
              "4. ICT Third-Party Risk (Articles 28-44): Due diligence, contractual requirements,\n"
              "   and ongoing monitoring for all ICT third-party providers. Critical providers\n"
              "   subject to EU oversight framework.\n\n"
              "5. Information Sharing (Article 45): Voluntary sharing of cyber threat intelligence\n"
              "   among financial entities.\n\n"
              "Effective: January 17, 2025\n"
              "Applies to: Banks, insurance companies, investment firms, payment institutions,\n"
              "crypto-asset providers, and their critical ICT third-party providers.")

    compliance_posture = st.text_area("Current Compliance Posture", height=150,
        value="Current frameworks in place:\n"
              "- ISO 27001 certified (last audit: 2024)\n"
              "- SOC 2 Type II compliant\n"
              "- GDPR compliant with DPO appointed\n"
              "- EBA Guidelines on ICT Risk partially implemented\n"
              "- BaFin MaRisk/BAIT requirements met\n"
              "- Basic incident response plan exists but not DORA-aligned\n"
              "- Third-party vendor management program in place but limited ICT focus\n"
              "- Annual penetration testing conducted (not threat-led)\n"
              "- No formal digital operational resilience testing program\n"
              "- Business continuity plans exist but ICT-specific continuity gaps identified\n"
              "- Board receives quarterly IT risk reports but no DORA-specific reporting")

    c1, c2 = st.columns(2)
    with c1:
        industry = st.selectbox("Industry",
            ["Financial Services", "Insurance", "Investment Management", "Payment Services",
             "Crypto/Digital Assets", "Healthcare", "Technology", "Energy", "Telecommunications"],
            index=0)
        jurisdiction = st.selectbox("Primary Jurisdiction",
            ["European Union", "United States", "United Kingdom", "Singapore",
             "Hong Kong", "Australia", "Canada", "Switzerland", "Global"],
            index=0)
    with c2:
        current_frameworks = st.multiselect("Current Compliance Frameworks",
            ["ISO 27001", "SOC 2", "GDPR", "PCI DSS", "NIST CSF", "CIS Controls",
             "COBIT", "ITIL", "Basel III", "MiFID II", "PSD2", "NIS2", "HIPAA",
             "EBA Guidelines", "BaFin MaRisk/BAIT"],
            default=["ISO 27001", "SOC 2", "GDPR", "EBA Guidelines", "BaFin MaRisk/BAIT"])

    submitted = st.form_submit_button("Analyze Regulation", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(org_profile=org_profile, regulation_text=regulation_text,
                  compliance_posture=compliance_posture, industry=industry,
                  jurisdiction=jurisdiction,
                  current_frameworks=", ".join(current_frameworks))

    with st.spinner("Analyzing regulation and assessing compliance gaps..."):
        try:
            result = analyze_regulation(config, api_key)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    # Board Reporting / Executive Summary
    board = result.get("board_reporting", {})
    st.subheader("Executive Summary")
    bm1, bm2, bm3, bm4 = st.columns(4)
    bm1.metric("Compliance Score", f"{board.get('compliance_score', 0)}/100")
    bm2.metric("Risk Rating", board.get("risk_rating", "N/A"))
    bm3.metric("Timeline", board.get("timeline_to_compliance", "N/A"))
    bm4.metric("Budget Request", board.get("budget_request", "N/A"))

    score = board.get("compliance_score", 0)
    score_cls = "score-high" if score >= 70 else "score-medium" if score >= 40 else "score-low"
    st.markdown(f'<div class="{score_cls}"><span style="font-size:1.2rem;font-weight:bold">'
                f'{board.get("executive_summary", "")}</span></div>', unsafe_allow_html=True)

    # Regulation Summary
    reg = result.get("regulation_summary", {})
    if reg:
        st.divider()
        st.subheader("Regulation Summary")
        st.markdown(f"**{reg.get('regulation_name', '')}** - {reg.get('issuing_body', '')}")
        st.markdown(f"**Effective Date:** {reg.get('effective_date', '')}")
        st.markdown(f"**Scope:** {reg.get('scope', '')}")
        st.info(reg.get("plain_language_summary", ""))
        if reg.get("key_objectives"):
            st.markdown("**Key Objectives:**")
            for obj in reg["key_objectives"]:
                st.markdown(f"- {obj}")

    # Applicability Assessment
    applic = result.get("applicability_assessment", {})
    if applic:
        st.divider()
        st.subheader("Applicability Assessment")
        ac1, ac2 = st.columns(2)
        with ac1:
            st.markdown(f"**Applies:** {'Yes' if applic.get('applies') else 'No'}")
            st.markdown(f"**Level:** {applic.get('applicability_level', '')}")
            st.markdown(f"**Classification:** {applic.get('entity_classification', '')}")
        with ac2:
            st.markdown(f"**Rationale:** {applic.get('rationale', '')}")
            st.markdown(f"**Proportionality:** {applic.get('proportionality', '')}")

    # Gap Analysis with Plotly Chart
    gaps = result.get("gap_analysis", [])
    if gaps:
        st.divider()
        st.subheader("Gap Analysis")

        # Plotly bar chart: compliant vs gaps per section
        sections = [g.get("section", "")[:40] for g in gaps]
        status_map = {"Compliant": 3, "Partial": 2, "Non-Compliant": 1, "Not Assessed": 0}
        statuses = [g.get("gap_status", "Not Assessed") for g in gaps]
        scores = [status_map.get(s, 0) for s in statuses]
        colors = ["#4caf50" if s == "Compliant" else "#fbc02d" if s == "Partial"
                  else "#f44336" if s == "Non-Compliant" else "#9e9e9e" for s in statuses]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=sections, y=scores, text=statuses, textposition="auto",
            marker_color=colors, name="Compliance Status"
        ))
        fig.update_layout(
            title="Gap Analysis: Compliance Status by Section",
            yaxis_title="Compliance Level",
            yaxis=dict(tickvals=[0, 1, 2, 3],
                       ticktext=["Not Assessed", "Non-Compliant", "Partial", "Compliant"]),
            height=400, showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

        # Gap detail cards
        for g in gaps:
            priority = g.get("priority", "Medium").lower()
            cls = f"gap-{priority}"
            st.markdown(f'<div class="gap-card {cls}">'
                       f'<strong>{g.get("section", "")}</strong> '
                       f'({g.get("gap_status", "")}) - Priority: {g.get("priority", "")}<br/>'
                       f'<em>Requirement:</em> {g.get("requirement", "")}<br/>'
                       f'<em>Current State:</em> {g.get("current_state", "")}<br/>'
                       f'<em>Gap:</em> {g.get("gap_description", "")}</div>',
                       unsafe_allow_html=True)

    # Compliance Roadmap
    roadmap = result.get("compliance_roadmap", [])
    if roadmap:
        st.divider()
        st.subheader("Compliance Roadmap")
        roadmap_df = pd.DataFrame([{
            "Phase": r.get("phase", ""),
            "Timeline": r.get("timeline", ""),
            "Milestone": r.get("milestone", ""),
            "Owner": r.get("responsible_party", ""),
        } for r in roadmap])
        st.dataframe(roadmap_df, use_container_width=True, hide_index=True)
        for r in roadmap:
            with st.expander(f"{r.get('phase', '')} - {r.get('timeline', '')}"):
                st.markdown("**Actions:**")
                for a in r.get("actions", []):
                    st.markdown(f"- {a}")
                if r.get("dependencies"):
                    st.markdown("**Dependencies:**")
                    for d in r["dependencies"]:
                        st.markdown(f"- {d}")

    # Impact Assessment & Cross-Regulation Mapping side by side
    ic1, ic2 = st.columns(2)
    impact = result.get("impact_assessment", {})
    if impact:
        with ic1:
            st.divider()
            st.subheader("Impact Assessment")
            st.markdown(f"**Operational:** {impact.get('operational_impact', '')}")
            st.markdown(f"**Technical:** {impact.get('technical_impact', '')}")
            st.markdown(f"**Staffing:** {impact.get('staffing_impact', '')}")
            st.markdown(f"**Timeline:** {impact.get('timeline_impact', '')}")
            fin = impact.get("financial_impact", {})
            if fin:
                st.markdown(f"**Compliance Cost:** {fin.get('estimated_compliance_cost', '')}")
                st.markdown(f"**Ongoing Annual Cost:** {fin.get('ongoing_annual_cost', '')}")

    cross = result.get("cross_regulation_mapping", [])
    if cross:
        with ic2:
            st.divider()
            st.subheader("Cross-Regulation Mapping")
            for c in cross:
                with st.expander(f"{c.get('framework', '')} - {c.get('overlap_percentage', '')} overlap"):
                    st.markdown(f"**Leverage Opportunity:** {c.get('leverage_opportunity', '')}")
                    if c.get("overlapping_areas"):
                        st.markdown("**Overlapping Areas:**")
                        for o in c["overlapping_areas"]:
                            st.markdown(f"- {o}")
                    if c.get("unique_requirements"):
                        st.markdown("**Unique Requirements:**")
                        for u in c["unique_requirements"]:
                            st.markdown(f"- {u}")

    # Risk of Non-Compliance
    risk = result.get("risk_of_non_compliance", {})
    if risk:
        st.divider()
        st.subheader("Risk of Non-Compliance")
        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown(f"**Maximum Penalty:** {risk.get('maximum_penalty', '')}")
            st.markdown(f"**Penalty Calculation:** {risk.get('penalty_calculation', '')}")
            st.markdown(f"**Enforcement Body:** {risk.get('enforcement_body', '')}")
        with rc2:
            st.markdown(f"**Enforcement Trends:** {risk.get('enforcement_trends', '')}")
            st.markdown(f"**Reputational Risk:** {risk.get('reputational_risk', '')}")
            st.markdown(f"**Liability Exposure:** {risk.get('liability_exposure', '')}")

    # Implementation Requirements
    impl = result.get("implementation_requirements", {})
    if impl:
        st.divider()
        st.subheader("Implementation Requirements")
        imp1, imp2, imp3 = st.columns(3)
        with imp1:
            st.markdown("**People:**")
            for p in impl.get("people", []):
                st.markdown(f"- {p}")
        with imp2:
            st.markdown("**Process:**")
            for p in impl.get("process", []):
                st.markdown(f"- {p}")
        with imp3:
            st.markdown("**Technology:**")
            for t in impl.get("technology", []):
                st.markdown(f"- {t}")

    # Monitoring Plan
    monitor = result.get("monitoring_plan", {})
    if monitor:
        st.divider()
        st.subheader("Monitoring Plan")
        kpis = monitor.get("kpis", [])
        if kpis:
            kpi_df = pd.DataFrame([{
                "KPI": k.get("metric", ""),
                "Target": k.get("target", ""),
                "Frequency": k.get("frequency", ""),
            } for k in kpis])
            st.dataframe(kpi_df, use_container_width=True, hide_index=True)
        st.markdown(f"**Audit Schedule:** {monitor.get('audit_schedule', '')}")
        st.markdown(f"**Review Cycle:** {monitor.get('review_cycle', '')}")

    # Board Decisions
    if board.get("key_decisions_needed"):
        st.divider()
        st.subheader("Key Decisions for Leadership")
        for d in board["key_decisions_needed"]:
            st.markdown(f"- {d}")
        if board.get("recommended_actions"):
            st.markdown("**Recommended Actions:**")
            for a in board["recommended_actions"]:
                st.markdown(f"- {a}")

    st.divider()
    st.download_button("Download Compliance Report (JSON)", json.dumps(result, indent=2),
                       "compliance_report.json", "application/json")
