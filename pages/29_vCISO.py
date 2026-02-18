"""vCISO - Virtual Chief Information Security Officer - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.security_engine import assess_security

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #004d40 0%, #00695c 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .risk-card { background: #f8f9fa; border-radius: 10px; padding: 1.2rem; margin-bottom: 0.8rem; }
    .risk-low { border-left: 4px solid #4caf50; }
    .risk-medium { border-left: 4px solid #ff9800; }
    .risk-high { border-left: 4px solid #f44336; }
    .risk-critical { border-left: 4px solid #b71c1c; background: #ffebee; }
    .qw-card { background: #e8f5e9; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
        border-left: 4px solid #2e7d32; }
    .road-card { background: #e3f2fd; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
        border-left: 4px solid #1565c0; }
    .phase-tag { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 20px;
        font-size: 0.8rem; font-weight: bold; color: white; margin-right: 0.5rem; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.warning("**Advisory Notice:** This tool provides general cybersecurity guidance. "
               "It does not replace a professional security audit or penetration test.")

st.markdown("""<div class="hero"><h1>vCISO - Virtual CISO</h1>
<p>AI-powered cybersecurity assessment for small & medium businesses — risk analysis, compliance gaps, and actionable roadmap</p></div>""",
unsafe_allow_html=True)

with st.form("security_form"):
    c1, c2 = st.columns(2)
    with c1:
        company_name = st.text_input("Company Name", value="Greenleaf Medical Clinic")
        industry = st.selectbox("Industry",
            ["Healthcare", "Financial Services", "Retail/E-commerce", "Technology/SaaS",
             "Manufacturing", "Professional Services", "Education", "Non-profit"])
        employee_count = st.selectbox("Employee Count",
            ["1-10", "11-50", "51-200", "201-500"], index=1)
        revenue = st.selectbox("Annual Revenue Range",
            ["Under $1M", "$1M-$5M", "$5M-$25M", "$25M-$100M"], index=1)
    with c2:
        budget = st.selectbox("Security Budget",
            ["Under $5K/year", "$5K-$25K/year", "$25K-$100K/year", "Over $100K/year"], index=1)
        data_types = st.multiselect("Data Types Handled",
            ["Customer PII", "Financial/Payment Data", "Health Records (PHI)",
             "Intellectual Property", "Employee Data", "Student Records"],
            default=["Customer PII", "Health Records (PHI)", "Financial/Payment Data"])
        compliance_reqs = st.multiselect("Compliance Requirements",
            ["HIPAA", "PCI-DSS", "SOC 2", "GDPR", "CCPA", "NIST", "ISO 27001", "None/Unknown"],
            default=["HIPAA"])

    current_security = st.text_area("Current Security Measures",
        value="Windows Defender on all workstations (15 PCs, 5 laptops)\n"
              "Basic firewall (ISP-provided router)\n"
              "Cloud-based EHR system (DrChrono) with SSO\n"
              "No formal security policy or incident response plan\n"
              "Staff use personal phones for work email\n"
              "Wi-Fi password shared among all staff, not segmented\n"
              "No MFA except on EHR system\n"
              "Weekly manual backup to external hard drive", height=150)

    infrastructure = st.text_area("IT Infrastructure",
        value="15 Windows 10 workstations, 5 laptops (mix of Windows/Mac)\n"
              "1 on-prem file server (Windows Server 2016, aging)\n"
              "Cloud: Microsoft 365 Business Basic, DrChrono EHR (cloud)\n"
              "Square POS terminal for patient co-pays\n"
              "Standard office network, single VLAN\n"
              "No VPN for remote access — staff use personal ISPs", height=130)

    s1, s2 = st.columns(2)
    with s1:
        incidents = st.text_area("Previous Security Incidents",
            value="No confirmed breaches.\nIncreasing phishing attempts targeting staff (3 reported in last month).\n"
                  "One staff member clicked a phishing link in October — no data loss confirmed but concerning.",
            height=100)
    with s2:
        concerns = st.text_input("Additional Concerns",
            value="New HIPAA audit expected next quarter. Need to demonstrate compliance improvements.")

    submitted = st.form_submit_button("Run Security Assessment", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        company_name=company_name, industry=industry, employee_count=employee_count,
        revenue=revenue, current_security=current_security, infrastructure=infrastructure,
        data_types=", ".join(data_types), incidents=incidents,
        compliance_reqs=", ".join(compliance_reqs), budget=budget, concerns=concerns,
    )

    with st.spinner("Running security assessment..."):
        try:
            result = assess_security(config, api_key)
        except Exception as e:
            st.error(f"Assessment failed: {e}")
            st.stop()

    # Executive Summary
    exec_sum = result.get("executive_summary", {})
    score = exec_sum.get("overall_risk_score", 50)
    risk_level = exec_sum.get("risk_level", "Medium")

    st.subheader("Executive Summary")
    ec1, ec2 = st.columns([1, 2])
    with ec1:
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": "Risk Score"},
            gauge={"axis": {"range": [0, 100]},
                   "bar": {"color": "#f44336" if score >= 70 else "#ff9800" if score >= 40 else "#4caf50"},
                   "steps": [{"range": [0, 30], "color": "#e8f5e9"},
                             {"range": [30, 60], "color": "#fff3e0"},
                             {"range": [60, 100], "color": "#ffebee"}]},
        ))
        fig_gauge.update_layout(height=250, margin=dict(t=40, b=0, l=30, r=30))
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.metric("Risk Level", risk_level)

    with ec2:
        st.info(f"**{exec_sum.get('headline', '')}**")
        for finding in exec_sum.get("key_findings", []):
            st.markdown(f"- {finding}")

    # Security Posture
    posture = result.get("security_posture", [])
    if posture:
        st.divider()
        st.subheader("Security Posture Assessment")

        # Radar chart
        cats = [p.get("category", "")[:20] for p in posture]
        scores = [p.get("score", 5) for p in posture]
        fig_radar = go.Figure(go.Scatterpolar(
            r=scores + [scores[0]],
            theta=cats + [cats[0]],
            fill="toself",
            fillcolor="rgba(76, 175, 80, 0.2)",
            line_color="#4caf50",
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(range=[0, 10])),
            title="Security Category Scores", height=350,
        )
        st.plotly_chart(fig_radar, use_container_width=True)

        for p in posture:
            s = p.get("score", 5)
            status = p.get("status", "Needs Improvement")
            cls = ("risk-low" if s >= 7 else "risk-high" if s <= 3 else "risk-medium")
            st.markdown(f'<div class="risk-card {cls}"><strong>{p.get("category", "")}</strong> '
                       f'— Score: {s}/10 | Status: {status}</div>', unsafe_allow_html=True)
            with st.expander(f"Details: {p.get('category', '')}"):
                st.markdown(p.get("findings", ""))
                for rec in p.get("recommendations", []):
                    st.markdown(f"- {rec}")

    # Compliance Assessment
    compliance = result.get("compliance_assessment", {})
    if compliance:
        st.divider()
        st.subheader("Compliance Assessment")
        st.markdown(f"**Applicable Frameworks:** {', '.join(compliance.get('applicable_frameworks', []))}")

        gaps = compliance.get("compliance_gaps", [])
        if gaps:
            gap_df = pd.DataFrame([{
                "Framework": g.get("framework", ""),
                "Gap": g.get("gap", ""),
                "Severity": g.get("severity", ""),
                "Remediation": g.get("remediation", ""),
            } for g in gaps])
            st.dataframe(gap_df, use_container_width=True, hide_index=True)

        for pa in compliance.get("priority_actions", []):
            st.warning(f"Priority: {pa}")

    # Threat Landscape
    threats = result.get("threat_landscape", {})
    if threats:
        st.divider()
        st.subheader("Threat Landscape")
        top = threats.get("top_threats", [])
        if top:
            threat_df = pd.DataFrame([{
                "Threat": t.get("threat", ""),
                "Likelihood": t.get("likelihood", ""),
                "Impact": t.get("impact", ""),
                "Mitigation": t.get("mitigation", ""),
            } for t in top])
            st.dataframe(threat_df, use_container_width=True, hide_index=True)

        for r in threats.get("industry_specific_risks", []):
            st.error(f"Industry Risk: {r}")

    # Quick Wins
    qw = result.get("quick_wins", [])
    if qw:
        st.divider()
        st.subheader("Quick Wins")
        for i, w in enumerate(qw, 1):
            st.markdown(f'<div class="qw-card"><strong>#{i} {w.get("action", "")}</strong><br/>'
                       f'Cost: {w.get("cost", "Low")} | Impact: {w.get("impact", "High")} | '
                       f'Timeframe: {w.get("timeframe", "This week")}</div>',
                       unsafe_allow_html=True)

    # Incident Response Plan
    irp = result.get("incident_response_plan", [])
    if irp:
        st.divider()
        st.subheader("Incident Response Plan")
        phase_colors = {"Preparation": "#1565c0", "Detection": "#6a1b9a",
                       "Containment": "#e65100", "Eradication": "#c62828",
                       "Recovery": "#2e7d32", "Lessons Learned": "#37474f"}
        for phase in irp:
            pname = phase.get("phase", "")
            color = phase_colors.get(pname, "#455a64")
            with st.expander(f"{pname}"):
                for action in phase.get("actions", []):
                    st.markdown(f"- {action}")
                if phase.get("tools_needed"):
                    st.caption(f"Tools: {', '.join(phase['tools_needed'])}")
                st.caption(f"Responsible: {phase.get('responsible_party', 'TBD')}")

    # Roadmap
    roadmap = result.get("roadmap", [])
    if roadmap:
        st.divider()
        st.subheader("Security Roadmap")
        for r in roadmap:
            st.markdown(f'<div class="road-card"><strong>{r.get("phase", "")}</strong> '
                       f'(Est. {r.get("estimated_cost", "TBD")})</div>', unsafe_allow_html=True)
            for item in r.get("items", []):
                st.markdown(f"  - {item}")

    # Budget
    budget_rec = result.get("budget_recommendation", {})
    if budget_rec:
        st.divider()
        st.subheader("Budget Recommendation")
        st.metric("Recommended Annual Security Budget", budget_rec.get("total_annual_budget", ""))

        breakdown = budget_rec.get("breakdown", [])
        if breakdown:
            labels = [b.get("category", "") for b in breakdown]
            values = []
            for b in breakdown:
                amt = b.get("amount", "$0").replace("$", "").replace(",", "")
                try:
                    values.append(float(amt))
                except ValueError:
                    values.append(0)
            fig_budget = go.Figure(go.Pie(labels=labels, values=values, hole=0.4))
            fig_budget.update_layout(title="Budget Allocation", height=300)
            st.plotly_chart(fig_budget, use_container_width=True)

    st.divider()
    st.download_button("Download Security Report (JSON)", json.dumps(result, indent=2),
                       "security_assessment.json", "application/json")
