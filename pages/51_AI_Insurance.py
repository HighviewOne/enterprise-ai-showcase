"""AI-nsurance - AI-Powered Insurance Claims Processing - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.insurance_engine import process_claim

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #1b5e20 0%, #00838f 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: #ffcc02; margin: 0; }
    .track-fast { background: #e8f5e9; border: 2px solid #2e7d32; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .track-standard { background: #e3f2fd; border: 2px solid #1565c0; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .track-escalate { background: #ffebee; border: 2px solid #c62828; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .fraud-low { background: #e8f5e9; border-left: 4px solid #4caf50; border-radius: 8px;
        padding: 0.8rem; margin-bottom: 0.4rem; }
    .fraud-medium { background: #fff3e0; border-left: 4px solid #ff9800; border-radius: 8px;
        padding: 0.8rem; margin-bottom: 0.4rem; }
    .fraud-high { background: #ffebee; border-left: 4px solid #f44336; border-radius: 8px;
        padding: 0.8rem; margin-bottom: 0.4rem; }
    .risk-card { background: #f8f9fa; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**AI-nsurance** automates claims processing, document sorting, and coverage "
            "analysis to reduce approval delays.")

st.markdown("""<div class="hero"><h1>AI-nsurance</h1>
<p>AI-powered insurance claims processing and analysis</p></div>""",
unsafe_allow_html=True)

with st.form("insurance_form"):
    claim_description = st.text_area("Claim Description", height=200,
        value="On January 15, 2026, at approximately 3:45 PM, I was driving northbound on Highway 101 "
              "near Exit 42 in San Jose, CA when a vehicle ran a red light at the intersection and "
              "struck the driver side of my 2023 Toyota Camry. The impact caused significant damage "
              "to the front left quarter panel, driver door, and side mirror. The airbags deployed.\n\n"
              "I was transported to Regional Medical Center by ambulance where I was treated for:\n"
              "- Whiplash / cervical strain\n"
              "- Left shoulder contusion\n"
              "- Minor lacerations from glass\n\n"
              "Police report #2026-SJ-04821 was filed. The other driver was cited for running the red "
              "light. Witness statements from two bystanders confirm the other driver was at fault.\n\n"
              "My vehicle was towed to AutoBody Plus (invoice pending). I have been unable to work for "
              "5 days due to injury. I am requesting coverage for vehicle repairs, medical expenses, "
              "and lost wages.")

    c1, c2 = st.columns(2)
    with c1:
        coverage_type = st.selectbox("Coverage Type",
            ["Auto - Comprehensive", "Auto - Collision", "Auto - Liability",
             "Health - Individual", "Health - Group", "Property - Homeowners",
             "Property - Renters", "Life", "Workers Compensation", "General Liability"],
            index=1)
        policy_limits = st.text_input("Policy Limits", value="$100,000 per person / $300,000 per accident / $50,000 property damage")
    with c2:
        deductible = st.text_input("Deductible", value="$500")
        policy_period = st.text_input("Policy Period", value="July 1, 2025 - June 30, 2026")

    claimant_profile = st.text_area("Claimant Profile", height=120,
        value="Name: Sarah Chen\n"
              "Age: 34 | Policy Holder since: 2019\n"
              "Prior Claims: 1 (minor fender bender in 2022, $1,200 payout)\n"
              "Driving Record: Clean, no violations\n"
              "Policy Tier: Preferred\n"
              "Location: San Jose, CA 95128")

    submitted = st.form_submit_button("Process Claim", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(claim_description=claim_description, coverage_type=coverage_type,
                  policy_limits=policy_limits, deductible=deductible,
                  policy_period=policy_period, claimant_profile=claimant_profile)

    with st.spinner("Processing claim..."):
        try:
            result = process_claim(config, api_key)
        except Exception as e:
            st.error(f"Claim processing failed: {e}")
            st.stop()

    # Claim Classification
    cls = result.get("claim_classification", {})
    st.subheader("Claim Classification")
    cm1, cm2, cm3, cm4 = st.columns(4)
    cm1.metric("Type", cls.get("type", ""))
    cm2.metric("Sub-Type", cls.get("sub_type", ""))
    cm3.metric("Complexity", cls.get("complexity", ""))
    cm4.metric("Priority", cls.get("priority", ""))

    # Processing Recommendation
    proc = result.get("processing_recommendation", {})
    track = proc.get("track", "Standard")
    t_cls = ("track-fast" if "Fast" in track else "track-escalate" if "Escalate" in track
             else "track-standard")
    st.markdown(f'<div class="{t_cls}"><span style="font-size:1.5rem;font-weight:bold">'
               f'{track}</span><br/>{proc.get("reason", "")}</div>', unsafe_allow_html=True)

    # Settlement & Coverage side by side
    sc1, sc2 = st.columns(2)
    settlement = result.get("settlement_estimate", {})
    if settlement:
        with sc1:
            st.divider()
            st.subheader("Settlement Estimate")
            se1, se2, se3 = st.columns(3)
            se1.metric("Low Range", f"${settlement.get('low_range', 0):,.0f}")
            se2.metric("Recommended", f"${settlement.get('recommended_settlement', 0):,.0f}")
            se3.metric("High Range", f"${settlement.get('high_range', 0):,.0f}")
            st.markdown(f"**Rationale:** {settlement.get('rationale', '')}")

    coverage = result.get("coverage_analysis", {})
    if coverage:
        with sc2:
            st.divider()
            st.subheader("Coverage Analysis")
            st.markdown(f"**Policy Status:** {coverage.get('policy_status', '')}")
            st.markdown(f"**Limit:** {coverage.get('coverage_limit', '')}")
            st.markdown(f"**Deductible:** {coverage.get('deductible', '')}")
            if coverage.get("covered_items"):
                st.markdown("**Covered:**")
                for item in coverage["covered_items"]:
                    st.markdown(f"- {item}")
            if coverage.get("excluded_items"):
                st.markdown("**Excluded:**")
                for item in coverage["excluded_items"]:
                    st.warning(item)

    # Damage Estimate with Plotly chart
    damage = result.get("damage_estimate", {})
    if damage:
        st.divider()
        st.subheader("Damage Estimate")
        items = damage.get("itemized_costs", [])
        if items:
            df = pd.DataFrame([{
                "Item": i.get("item", ""),
                "Category": i.get("category", ""),
                "Cost": f"${i.get('estimated_cost', 0):,.2f}",
                "Notes": i.get("notes", ""),
            } for i in items])
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Plotly pie chart
            labels = [i.get("item", "")[:30] for i in items]
            values = [i.get("estimated_cost", 0) for i in items]
            if any(v > 0 for v in values):
                fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.4,
                    marker=dict(colors=["#1b5e20", "#00838f", "#ffcc02", "#e65100",
                                        "#6a1b9a", "#c62828", "#0d47a1", "#2e7d32"]))])
                fig.update_layout(title="Claim Cost Breakdown", height=400)
                st.plotly_chart(fig, use_container_width=True)

        dm1, dm2, dm3 = st.columns(3)
        dm1.metric("Total Estimate", f"${damage.get('total_estimate', 0):,.2f}")
        dm2.metric("Depreciation", f"${damage.get('depreciation', 0):,.2f}")
        dm3.metric("Net Claim Value", f"${damage.get('net_claim_value', 0):,.2f}")

    # Liability Assessment
    liability = result.get("liability_assessment", {})
    if liability:
        st.divider()
        st.subheader("Liability Assessment")
        st.markdown(f"**Determination:** {liability.get('liability_determination', '')}")
        st.markdown(f"**Fault %:** {liability.get('fault_percentage', '')}")
        st.markdown(f"**Subrogation Potential:** {liability.get('subrogation_potential', '')}")
        if liability.get("third_party_involvement"):
            st.markdown(f"**Third Party:** {liability['third_party_involvement']}")

    # Fraud Indicators
    fraud = result.get("fraud_indicators", {})
    if fraud:
        st.divider()
        st.subheader("Fraud Assessment")
        risk = fraud.get("risk_level", "Low").lower()
        f_cls = f"fraud-{risk}"
        st.markdown(f'<div class="{f_cls}"><strong>Risk Level: {fraud.get("risk_level", "")}</strong> '
                   f'| Recommendation: {fraud.get("recommendation", "")}<br/>'
                   f'{fraud.get("notes", "")}</div>', unsafe_allow_html=True)
        if fraud.get("flags"):
            for flag in fraud["flags"]:
                st.markdown(f"- {flag}")

    # Document Checklist
    docs = result.get("document_checklist", [])
    if docs:
        st.divider()
        st.subheader("Document Checklist")
        doc_df = pd.DataFrame([{
            "Document": d.get("document", ""),
            "Required": "Yes" if d.get("required") else "No",
            "Status": d.get("status", ""),
            "Notes": d.get("notes", ""),
        } for d in docs])
        st.dataframe(doc_df, use_container_width=True, hide_index=True)

    # Next Steps
    steps = result.get("next_steps_for_claimant", [])
    if steps:
        st.divider()
        st.subheader("Next Steps for Claimant")
        for s in steps:
            st.markdown(f"- {s}")

    # Compliance Check
    compliance = result.get("compliance_check", {})
    if compliance:
        st.divider()
        st.subheader("Compliance Check")
        st.markdown(f"**Regulatory Met:** {'Yes' if compliance.get('regulatory_requirements_met') else 'No'}")
        st.markdown(f"**Documentation:** {compliance.get('documentation_compliance', '')}")
        st.markdown(f"**Filing Deadlines:** {compliance.get('filing_deadlines', '')}")
        if compliance.get("state_specific_requirements"):
            for req in compliance["state_specific_requirements"]:
                st.markdown(f"- {req}")

    # Timeline
    timeline = result.get("timeline_to_resolution", {})
    if timeline:
        st.divider()
        st.subheader(f"Timeline to Resolution: ~{timeline.get('estimated_days', 'N/A')} days")
        phases = timeline.get("phases", [])
        if phases:
            phase_df = pd.DataFrame([{
                "Phase": p.get("phase", ""),
                "Duration (days)": p.get("duration_days", 0),
                "Status": p.get("status", ""),
            } for p in phases])
            st.dataframe(phase_df, use_container_width=True, hide_index=True)
        if timeline.get("bottlenecks"):
            st.markdown("**Potential Delays:**")
            for b in timeline["bottlenecks"]:
                st.warning(b)

    st.divider()
    st.download_button("Download Claims Report (JSON)", json.dumps(result, indent=2),
                       "claims_report.json", "application/json")
