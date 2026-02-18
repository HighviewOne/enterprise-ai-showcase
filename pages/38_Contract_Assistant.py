"""Government Contract Assistant - Federal Procurement Guidance - Streamlit Application."""

import os
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from engines.contract_engine import analyze_contract

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: #ffd54f; margin: 0; }
    .hero p { color: #e0e0e0; }
    .go-card { background: #e8f5e9; border-radius: 10px; padding: 1.2rem; border-left: 4px solid #2e7d32; }
    .nogo-card { background: #ffebee; border-radius: 10px; padding: 1.2rem; border-left: 4px solid #c62828; }
    .cond-card { background: #fff3e0; border-radius: 10px; padding: 1.2rem; border-left: 4px solid #e65100; }
    .section-card { background: #f8f9fa; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
        border-left: 4px solid #1565c0; }
    .theme-card { background: #e8eaf6; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
        border-left: 4px solid #3f51b5; }
    .timeline-card { background: #e3f2fd; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem;
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
    st.info("**Athena** helps small businesses navigate government contracting — from "
            "opportunity analysis to proposal strategy.")

st.markdown("""<div class="hero"><h1>Athena - Government Contract Assistant</h1>
<p>AI-powered federal procurement guidance — opportunity analysis, compliance checks, and proposal strategy</p></div>""",
unsafe_allow_html=True)

with st.form("contract_form"):
    solicitation = st.text_area("Solicitation Details", height=200,
        value="RFP: GSA-IT-2025-0042\n"
              "Agency: General Services Administration (GSA)\n"
              "Title: Cloud Migration and Modernisation Services\n"
              "NAICS: 541512 - Computer Systems Design Services\n"
              "Set-Aside: Small Business Set-Aside (Total)\n"
              "Contract Type: Time & Materials (T&M) with NTE\n"
              "Period: 1 Base Year + 4 Option Years\n"
              "Estimated Value: $5M-$10M\n"
              "Due Date: March 15, 2025\n"
              "Requirements:\n"
              "- Migrate 15 legacy applications to AWS GovCloud\n"
              "- FedRAMP High compliance required\n"
              "- Agile development methodology\n"
              "- Must demonstrate 3 similar cloud migration projects\n"
              "- Key personnel: Project Manager (PMP), Cloud Architect (AWS Certified)\n"
              "- Evaluation: Technical (50%), Past Performance (30%), Price (20%)\n"
              "- Oral presentations required for shortlisted firms")

    company_profile = st.text_area("Company Profile", height=180,
        value="Company: CloudPath Solutions LLC\n"
              "Founded: 2019 | DUNS: 123456789\n"
              "Employees: 45 | Revenue: $6.5M (2024)\n"
              "Location: Reston, VA\n"
              "Capabilities: Cloud migration (AWS/Azure), DevSecOps, application modernisation\n"
              "Past Performance: 3 federal contracts (DOD, VA, DHS), 5 commercial cloud migrations\n"
              "Certifications: AWS Advanced Consulting Partner, ISO 27001\n"
              "Key Staff: 2 PMP-certified PMs, 3 AWS Solutions Architects, 1 CISSP\n"
              "Current Vehicles: GSA MAS IT, CIO-SP3 (sub)")

    c1, c2 = st.columns(2)
    with c1:
        naics = st.text_input("Primary NAICS", value="541512")
        certifications = st.multiselect("Business Certifications",
            ["Small Business", "8(a)", "WOSB/EDWOSB", "SDVOSB", "HUBZone",
             "Minority-Owned", "None"],
            default=["Small Business"])
    with c2:
        award_date = st.text_input("Target Award Date", value="June 2025")
        context = st.text_input("Additional Context",
            value="We've worked with GSA before on a smaller task order. Know the COR informally.")

    submitted = st.form_submit_button("Analyse Opportunity", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        solicitation=solicitation, company_profile=company_profile,
        naics=naics, certifications=", ".join(certifications),
        award_date=award_date, context=context,
    )

    with st.spinner("Analysing opportunity..."):
        try:
            result = analyze_contract(config, api_key)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    # Opportunity Analysis
    opp = result.get("opportunity_analysis", {})
    st.subheader("Opportunity Analysis")

    om1, om2, om3, om4 = st.columns(4)
    om1.metric("Fit Score", f"{opp.get('fit_score', 0)}/100")
    om2.metric("Contract Type", opp.get("contract_type", ""))
    om3.metric("Est. Value", opp.get("estimated_value", ""))
    om4.metric("Competition", opp.get("competition_level", ""))

    rec = opp.get("go_no_go_recommendation", "Conditional Go")
    cls = "go-card" if rec == "Go" else "nogo-card" if rec == "No-Go" else "cond-card"
    st.markdown(f'<div class="{cls}"><strong>Recommendation: {rec}</strong><br/>'
               f'{opp.get("rationale", "")}</div>', unsafe_allow_html=True)

    # Compliance Checklist
    compliance = result.get("compliance_checklist", [])
    if compliance:
        st.divider()
        st.subheader("Compliance Checklist")
        comp_df = pd.DataFrame([{
            "Requirement": c.get("requirement", ""),
            "Status": c.get("status", ""),
            "Evidence": c.get("evidence", ""),
            "Action Needed": c.get("action_needed", ""),
        } for c in compliance])
        st.dataframe(comp_df, use_container_width=True, hide_index=True)

    # Win Themes
    themes = result.get("win_themes", [])
    if themes:
        st.divider()
        st.subheader("Win Themes")
        for t in themes:
            st.markdown(f'<div class="theme-card"><strong>{t.get("theme", "")}</strong><br/>'
                       f'Evidence: {t.get("evidence", "")}<br/>'
                       f'<em>vs. Competitors: {t.get("ghost_competitor", "")}</em></div>',
                       unsafe_allow_html=True)

    # Proposal Outline
    outline = result.get("proposal_outline", [])
    if outline:
        st.divider()
        st.subheader("Proposal Outline")
        for s in outline:
            with st.expander(f"📄 {s.get('section', '')} {('— ' + s['page_limit']) if s.get('page_limit') else ''}"):
                st.markdown("**Key Points:**")
                for k in s.get("key_points", []):
                    st.markdown(f"- {k}")
                if s.get("discriminators"):
                    st.markdown("**Discriminators:**")
                    for d in s["discriminators"]:
                        st.success(d)
                if s.get("warnings"):
                    for w in s["warnings"]:
                        st.warning(w)

    # Pricing & Teaming side by side
    pc1, pc2 = st.columns(2)
    pricing = result.get("pricing_guidance", {})
    if pricing:
        with pc1:
            st.divider()
            st.subheader("Pricing Guidance")
            st.markdown(f"**Strategy:** {pricing.get('strategy', '')}")
            if pricing.get("competitive_range"):
                st.markdown(f"**Competitive Range:** {pricing['competitive_range']}")
            for c in pricing.get("considerations", []):
                st.markdown(f"- {c}")
            for w in pricing.get("warnings", []):
                st.warning(w)

    teaming = result.get("teaming_recommendations", {})
    if teaming:
        with pc2:
            st.divider()
            st.subheader("Teaming Strategy")
            needs = "Yes" if teaming.get("needs_teaming") else "No"
            st.markdown(f"**Teaming Needed:** {needs}")
            if teaming.get("teaming_structure"):
                st.markdown(f"**Structure:** {teaming['teaming_structure']}")
            for r in teaming.get("recommendations", []):
                st.markdown(f"- {r}")

    # Timeline
    timeline = result.get("timeline", [])
    if timeline:
        st.divider()
        st.subheader("Proposal Timeline")
        for t in timeline:
            st.markdown(f'<div class="timeline-card"><strong>{t.get("milestone", "")}</strong> — '
                       f'{t.get("deadline", "")} | Owner: {t.get("owner", "")}</div>',
                       unsafe_allow_html=True)

    # Risk Factors
    risks = result.get("risk_factors", [])
    if risks:
        st.divider()
        st.subheader("Risk Factors")
        for r in risks:
            icon = "🔴" if r.get("impact") == "High" else "🟡" if r.get("impact") == "Medium" else "🟢"
            st.markdown(f"{icon} **{r.get('risk', '')}** — {r.get('mitigation', '')}")

    st.divider()
    st.download_button("Download Analysis (JSON)", json.dumps(result, indent=2),
                       "contract_analysis.json", "application/json")
