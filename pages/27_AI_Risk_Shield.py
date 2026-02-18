"""AI Risk Shield - Financial KYC/AML Screening - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.risk_engine import assess_risk

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #263238 0%, #455a64 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .risk-card { background: #f8f9fa; border-radius: 10px; padding: 1.2rem; margin-bottom: 0.8rem; }
    .risk-low { border-left: 4px solid #4caf50; }
    .risk-medium { border-left: 4px solid #ff9800; }
    .risk-high { border-left: 4px solid #f44336; }
    .risk-blocked { border-left: 4px solid #b71c1c; background: #ffebee; }
    .check-pass { color: #4caf50; font-weight: bold; }
    .check-fail { color: #f44336; font-weight: bold; }
    .check-warn { color: #ff9800; font-weight: bold; }
    .factor-tag { display: inline-block; padding: 0.2rem 0.5rem; border-radius: 20px;
        margin: 0.1rem; font-size: 0.8rem; }
    .factor-high { background: #ffcdd2; color: #c62828; }
    .factor-med { background: #fff3e0; color: #e65100; }
    .factor-low { background: #e8f5e9; color: #2e7d32; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**Note:** This is a demonstration tool. Real KYC/AML screening requires "
            "integration with official sanctions lists and regulatory databases.")

st.markdown("""<div class="hero"><h1>AI Risk Shield</h1>
<p>AI-powered KYC/AML risk classification — PEP screening, sanctions checks, and transaction risk analysis</p></div>""",
unsafe_allow_html=True)

sample_customers = ""
try:
    with open("examples/sample_customers.txt") as f:
        sample_customers = f.read()
except FileNotFoundError:
    pass

with st.form("risk_form"):
    customers = st.text_area("Customer Profiles to Screen",
                              value=sample_customers, height=300,
                              placeholder="Paste customer details: name, nationality, occupation, "
                                          "source of funds, PEP status, transaction patterns...")
    c1, c2 = st.columns(2)
    with c1:
        risk_appetite = st.selectbox("Institutional Risk Appetite",
            ["Conservative", "Moderate", "Aggressive"])
        industry = st.selectbox("Industry",
            ["Banking / Wealth Management", "Insurance", "Payments / Fintech",
             "Cryptocurrency Exchange", "Real Estate", "Securities / Brokerage"])
    with c2:
        jurisdiction = st.selectbox("Primary Jurisdiction",
            ["United States (FinCEN)", "United Kingdom (FCA)", "European Union",
             "Singapore (MAS)", "Hong Kong (HKMA)", "Multi-jurisdictional"])
        context = st.text_input("Additional Context",
            value="Quarterly batch screening. Focus on high-risk jurisdictions and PEP exposure.")

    submitted = st.form_submit_button("Screen Customers", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        customers=customers, risk_appetite=risk_appetite,
        industry=industry, jurisdiction=jurisdiction, context=context,
    )

    with st.spinner("Running risk assessment..."):
        try:
            result = assess_risk(config, api_key)
        except Exception as e:
            st.error(f"Assessment failed: {e}")
            st.stop()

    # Batch Summary
    batch = result.get("batch_summary", {})
    st.subheader("Screening Summary")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Total Screened", batch.get("total_customers", 0))
    m2.metric("Low Risk", batch.get("low_risk", 0))
    m3.metric("Medium Risk", batch.get("medium_risk", 0))
    m4.metric("High Risk", batch.get("high_risk", 0))
    m5.metric("Blocked", batch.get("blocked", 0))

    # Risk distribution chart
    fig_risk = go.Figure(go.Pie(
        labels=["Low", "Medium", "High", "Blocked"],
        values=[batch.get("low_risk", 0), batch.get("medium_risk", 0),
                batch.get("high_risk", 0), batch.get("blocked", 0)],
        hole=0.4,
        marker_colors=["#4caf50", "#ff9800", "#f44336", "#b71c1c"],
    ))
    fig_risk.update_layout(title="Risk Distribution", height=300)
    st.plotly_chart(fig_risk, use_container_width=True)
    st.info(batch.get("key_findings", ""))

    # Customer Assessments
    assessments = result.get("customer_assessments", [])
    if assessments:
        st.divider()
        st.subheader(f"Customer Risk Assessments ({len(assessments)})")

        # Summary table
        sum_df = pd.DataFrame([{
            "Customer": a.get("customer_id", ""),
            "Type": a.get("entity_type", ""),
            "Risk": a.get("risk_classification", ""),
            "Score": f"{a.get('risk_score', 0)}/100",
            "Recommendation": a.get("recommendation", ""),
            "PEP": "Yes" if a.get("pep_screening", {}).get("is_pep") else "No",
            "Sanctions": a.get("sanctions_screening", {}).get("status", ""),
        } for a in assessments])
        st.dataframe(sum_df, use_container_width=True, hide_index=True)

        # Risk score chart
        fig_scores = go.Figure(go.Bar(
            x=[a.get("customer_id", "")[:20] for a in assessments],
            y=[a.get("risk_score", 0) for a in assessments],
            marker_color=["#4caf50" if a.get("risk_score", 0) < 30
                          else "#ff9800" if a.get("risk_score", 0) < 60
                          else "#f44336" for a in assessments],
            text=[a.get("risk_classification", "") for a in assessments],
            textposition="outside",
        ))
        fig_scores.update_layout(title="Risk Scores", height=300, yaxis_range=[0, 100])
        st.plotly_chart(fig_scores, use_container_width=True)

        # Detailed cards
        for a in sorted(assessments, key=lambda x: x.get("risk_score", 0), reverse=True):
            risk = a.get("risk_classification", "Medium")
            cls = ("risk-blocked" if "Block" in risk or "Reject" in risk
                   else "risk-high" if "High" in risk
                   else "risk-medium" if "Medium" in risk
                   else "risk-low")
            rec = a.get("recommendation", "")
            rec_color = ("#4caf50" if "Approve" in rec and "EDD" not in rec
                        else "#f44336" if "Reject" in rec
                        else "#ff9800")

            st.markdown(f"""<div class="risk-card {cls}">
                <strong>{a.get('customer_id', '')}</strong> ({a.get('entity_type', '')})
                <span style="float:right; color:{rec_color}; font-weight:bold;">{rec}</span><br/>
                Risk: <strong>{risk}</strong> ({a.get('risk_score', 0)}/100) |
                Confidence: {a.get('confidence', 'N/A')}
            </div>""", unsafe_allow_html=True)

            with st.expander(f"Full Assessment — {a.get('customer_id', '')}"):
                dc1, dc2 = st.columns(2)
                with dc1:
                    # KYC Checks
                    kyc = a.get("kyc_checks", {})
                    st.markdown("**KYC Checks:**")
                    for field, label in [("identity_verification", "Identity"),
                                         ("address_verification", "Address"),
                                         ("source_of_funds", "Source of Funds"),
                                         ("beneficial_ownership", "Beneficial Ownership")]:
                        val = kyc.get(field, "N/A")
                        cls = ("check-pass" if val in ("Pass", "Verified", "Clear")
                               else "check-fail" if val in ("Fail", "Suspicious", "Opaque")
                               else "check-warn")
                        st.markdown(f'- {label}: <span class="{cls}">{val}</span>', unsafe_allow_html=True)

                    # PEP
                    pep = a.get("pep_screening", {})
                    st.markdown(f"**PEP Status:** {'Yes - ' + pep.get('pep_type', '') if pep.get('is_pep') else 'Not a PEP'}")
                    if pep.get("details"):
                        st.caption(pep["details"])

                with dc2:
                    # Sanctions
                    sanc = a.get("sanctions_screening", {})
                    sanc_status = sanc.get("status", "Clear")
                    sanc_cls = "check-pass" if sanc_status == "Clear" else "check-fail"
                    st.markdown(f'**Sanctions:** <span class="{sanc_cls}">{sanc_status}</span>', unsafe_allow_html=True)
                    if sanc.get("matches_found"):
                        for m in sanc["matches_found"]:
                            st.error(f"Match: {m}")

                    # Adverse Media
                    am = a.get("adverse_media", {})
                    st.markdown(f"**Adverse Media:** {am.get('severity', 'None')}")
                    if am.get("findings"):
                        st.caption(am["findings"])

                    # Transaction Risk
                    tr = a.get("transaction_risk", {})
                    st.markdown(f"**Transaction Pattern:** {tr.get('pattern_assessment', 'N/A')}")
                    for rf in tr.get("red_flags", []):
                        st.warning(rf)

                # Risk Factors
                factors = a.get("risk_factors", [])
                if factors:
                    st.markdown("**Risk Factors:**")
                    for f in factors:
                        w = f.get("weight", "Medium")
                        f_cls = "factor-high" if w == "High" else "factor-low" if w == "Low" else "factor-med"
                        st.markdown(f'<span class="factor-tag {f_cls}">[{w}] {f.get("factor", "")}</span> '
                                   f'— {f.get("evidence", "")}', unsafe_allow_html=True)

                # EDD
                edd = a.get("edd_requirements", [])
                if edd:
                    st.markdown("**Enhanced Due Diligence Required:**")
                    for e in edd:
                        st.markdown(f"- {e}")

                st.info(f"**Analyst Notes:** {a.get('analyst_notes', '')}")
                st.caption(f"Monitoring: {a.get('monitoring_recommendations', '')}")

    # Regulatory Considerations
    reg = result.get("regulatory_considerations", {})
    if reg:
        st.divider()
        st.subheader("Regulatory Considerations")
        rc1, rc2 = st.columns(2)
        with rc1:
            for j in reg.get("jurisdictional_risks", []):
                st.error(f"Jurisdiction Risk: {j}")
            for r in reg.get("regulatory_requirements", []):
                st.markdown(f"- {r}")
        with rc2:
            for o in reg.get("reporting_obligations", []):
                st.warning(f"Reporting: {o}")

    st.divider()
    st.download_button("Download Risk Report (JSON)", json.dumps(result, indent=2),
                       "risk_assessment.json", "application/json")
