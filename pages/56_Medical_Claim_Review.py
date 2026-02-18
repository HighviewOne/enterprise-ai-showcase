"""ClaimLens - AI Medical Claim Review Assistant - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.claim_engine import review_claim

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #4a148c 0%, #6a1b9a 50%, #8e24aa 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: #ce93d8; margin: 0; }
    .decision-approve { background: #e8f5e9; border: 2px solid #2e7d32; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .decision-deny { background: #ffebee; border: 2px solid #c62828; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .decision-pend { background: #fff3e0; border: 2px solid #e65100; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .decision-escalate { background: #fce4ec; border: 2px solid #ad1457; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .flag-card { background: #f8f9fa; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem; }
    .flag-high { border-left: 4px solid #f44336; }
    .flag-medium { border-left: 4px solid #ff9800; }
    .flag-low { border-left: 4px solid #4caf50; }
    .missing-card { background: #fff8e1; border-left: 4px solid #ffc107; padding: 0.6rem;
        border-radius: 4px; margin-bottom: 0.3rem; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**ClaimLens** evaluates medical claims for completeness, coding accuracy, "
            "medical necessity, and generates preliminary adjudication recommendations.")

st.markdown("""<div class="hero"><h1>ClaimLens</h1>
<p>AI-powered medical claim review and adjudication support</p></div>""",
unsafe_allow_html=True)

with st.form("claim_form"):
    st.markdown("**Claim Details**")
    claim_details = st.text_area("Claim Narrative", height=150,
        value="Patient: Robert Martinez, DOB: 03/15/1968, Member ID: HBC-2847561\n"
              "Date of Service: 01/22/2026\n"
              "Provider: Dr. Sarah Chen, MD - Orthopedic Surgery\n"
              "Facility: Memorial Regional Medical Center (In-Network)\n"
              "Claim ID: CLM-2026-00847\n\n"
              "Patient presents with persistent right knee pain for 6 months. Conservative "
              "treatment attempted: 8 weeks physical therapy, NSAIDs, corticosteroid injection "
              "(10/2025). MRI shows possible meniscal tear but report not attached to claim. "
              "Requesting knee arthroscopy with possible meniscectomy.")

    c1, c2 = st.columns(2)
    with c1:
        procedure_codes = st.text_area("Procedure Codes (CPT)", height=100,
            value="29881 - Arthroscopy, knee, surgical; with meniscectomy\n"
                  "29877 - Arthroscopy, knee, surgical; debridement/shaving of articular cartilage\n"
                  "27447 - Arthroplasty, knee, condyle and plateau (NOTE: appears inconsistent with arthroscopy)")
        diagnosis_codes = st.text_area("Diagnosis Codes (ICD-10)", height=80,
            value="M23.21 - Derangement of meniscus, right knee\n"
                  "M17.11 - Primary osteoarthritis, right knee\n"
                  "M25.561 - Pain in right knee")
    with c2:
        provider_info = st.text_area("Provider Information", height=80,
            value="Dr. Sarah Chen, MD - Board Certified Orthopedic Surgeon\n"
                  "NPI: 1234567890 | Tax ID: 12-3456789\n"
                  "Memorial Regional Medical Center - In-Network facility\n"
                  "Provider is in good standing, no sanctions")
        billed_amounts = st.text_area("Billed Amounts", height=80,
            value="CPT 29881: $4,200.00\n"
                  "CPT 29877: $2,800.00\n"
                  "CPT 27447: $18,500.00\n"
                  "Facility fee: $8,200.00\n"
                  "Anesthesia: $2,100.00\n"
                  "Total Billed: $35,800.00")

    patient_history = st.text_area("Patient History Summary", height=100,
        value="56-year-old male, BMI 29.8. History of right knee osteoarthritis (3 years). "
              "Physical therapy completed Oct-Dec 2025 (12 sessions). Cortisone injection "
              "10/15/2025 with temporary relief (4 weeks). No prior knee surgeries. "
              "Comorbidities: controlled hypertension, pre-diabetes. "
              "Note: MRI report referenced but not included in submission.")
    policy_details = st.text_area("Policy Details", height=100,
        value="Plan: BlueCross PPO Premium | Effective: 01/01/2025\n"
              "Deductible: $1,500 (met: $1,200 - $300 remaining)\n"
              "Coinsurance: 80/20 after deductible | OOP Max: $6,000\n"
              "Prior Authorization: REQUIRED for all surgical procedures >$2,500\n"
              "Prior Auth Status: NOT ON FILE for this claim\n"
              "Knee arthroscopy: Covered under surgical benefits\n"
              "Total knee replacement: Requires step therapy documentation")

    submitted = st.form_submit_button("Review Claim", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(claim_details=claim_details, procedure_codes=procedure_codes,
                  diagnosis_codes=diagnosis_codes, provider_info=provider_info,
                  billed_amounts=billed_amounts, patient_history=patient_history,
                  policy_details=policy_details)

    with st.spinner("Reviewing claim details and applying clinical guidelines..."):
        try:
            result = review_claim(config, api_key)
        except Exception as e:
            st.error(f"Review failed: {e}")
            st.stop()

    # Claim Summary
    summary = result.get("claim_summary", {})
    if summary:
        st.subheader("Claim Summary")
        sm1, sm2, sm3, sm4 = st.columns(4)
        sm1.metric("Claim ID", summary.get("claim_id", ""))
        sm2.metric("Patient", summary.get("patient_name", ""))
        sm3.metric("Provider", summary.get("provider", "")[:30])
        sm4.metric("Total Billed", f"${summary.get('total_billed', 0):,.2f}")

    # Decision
    rec = result.get("recommendation", {})
    decision = rec.get("decision", "Pend for Review")
    d_cls = ("decision-approve" if "Approve" in decision else "decision-deny" if "Deny" in decision
             else "decision-escalate" if "Escalate" in decision else "decision-pend")
    st.markdown(f'<div class="{d_cls}"><span style="font-size:1.5rem;font-weight:bold">'
               f'{decision}</span> (Confidence: {rec.get("confidence", "")})<br/>'
               f'{rec.get("rationale", "")}</div>', unsafe_allow_html=True)

    # Billed vs Allowed Chart
    payment = result.get("payment_calculation", {})
    comparable = result.get("comparable_claims", {})
    if payment:
        st.divider()
        st.subheader("Payment Analysis")

        fig = go.Figure()
        categories = ["Billed Amount", "Allowed Amount", "Plan Payment", "Member Responsibility"]
        values = [
            payment.get("billed_amount", 0),
            payment.get("allowed_amount", 0),
            payment.get("plan_payment", 0),
            payment.get("member_responsibility", 0),
        ]
        colors = ["#ef5350", "#42a5f5", "#66bb6a", "#ffa726"]
        fig.add_trace(go.Bar(x=categories, y=values, marker_color=colors,
                             text=[f"${v:,.2f}" for v in values], textposition="outside"))
        fig.update_layout(title="Billed vs Allowed vs Payment Breakdown",
                          yaxis_title="Amount ($)", height=400)
        st.plotly_chart(fig, use_container_width=True)

        pc1, pc2 = st.columns(2)
        with pc1:
            st.markdown("**Payment Breakdown:**")
            st.markdown(f"- Billed: ${payment.get('billed_amount', 0):,.2f}")
            st.markdown(f"- Allowed: ${payment.get('allowed_amount', 0):,.2f}")
            st.markdown(f"- Plan Pays: ${payment.get('plan_payment', 0):,.2f}")
            st.markdown(f"- Copay: ${payment.get('copay', 0):,.2f}")
            st.markdown(f"- Coinsurance: ${payment.get('coinsurance', 0):,.2f}")
            st.markdown(f"- Deductible Applied: ${payment.get('deductible_applied', 0):,.2f}")
        with pc2:
            if comparable:
                st.markdown("**Comparable Claims:**")
                st.markdown(f"- Typical Allowed: ${comparable.get('typical_allowed_amount', 0):,.2f}")
                st.markdown(f"- Range: ${comparable.get('typical_range_low', 0):,.2f} - "
                           f"${comparable.get('typical_range_high', 0):,.2f}")
                st.markdown(f"- Geographic Factor: {comparable.get('geographic_adjustment', '')}")
                st.markdown(f"- Percentile: {comparable.get('percentile_of_billed', '')}")

    # Medical Necessity & Coding side by side
    nc1, nc2 = st.columns(2)
    necessity = result.get("medical_necessity_assessment", {})
    if necessity:
        with nc1:
            st.divider()
            st.subheader(f"Medical Necessity (Score: {necessity.get('necessity_score', 0)}/10)")
            is_necessary = necessity.get("is_medically_necessary", False)
            if is_necessary:
                st.success("Medically Necessary")
            else:
                st.error("Medical Necessity Not Established")
            st.markdown(necessity.get("justification", ""))
            if necessity.get("clinical_guidelines_referenced"):
                st.markdown("**Guidelines Referenced:**")
                for g in necessity["clinical_guidelines_referenced"]:
                    st.markdown(f"- {g}")

    coding = result.get("coding_accuracy", {})
    if coding:
        with nc2:
            st.divider()
            st.subheader("Coding Accuracy")
            cc1, cc2 = st.columns(2)
            cc1.metric("CPT Valid", "Yes" if coding.get("cpt_codes_valid") else "No")
            cc2.metric("ICD-10 Valid", "Yes" if coding.get("icd10_codes_valid") else "No")
            st.metric("Upcoding Risk", coding.get("upcoding_risk", ""))
            st.metric("Unbundling Risk", coding.get("unbundling_risk", ""))
            if coding.get("coding_notes"):
                for n in coding["coding_notes"]:
                    st.markdown(f"- {n}")

    # Documentation & Policy Compliance
    dc1, dc2 = st.columns(2)
    docs = result.get("documentation_completeness", {})
    if docs:
        with dc1:
            st.divider()
            st.subheader(f"Documentation (Score: {docs.get('completeness_score', 0)}/10)")
            missing = docs.get("missing_items", [])
            if missing:
                for m in missing:
                    st.markdown(f'<div class="missing-card"><strong>{m.get("item", "")}</strong> '
                               f'({m.get("severity", "")})<br/>{m.get("impact", "")}</div>',
                               unsafe_allow_html=True)
            else:
                st.success("All documentation complete")

    policy = result.get("policy_compliance", {})
    if policy:
        with dc2:
            st.divider()
            st.subheader("Policy Compliance")
            st.markdown(f"**Network Status:** {policy.get('network_status', '')}")
            st.markdown(f"**Pre-Auth Required:** {'Yes' if policy.get('pre_authorization_required') else 'No'}")
            st.markdown(f"**Pre-Auth Obtained:** {'Yes' if policy.get('pre_authorization_obtained') else 'No'}")
            if policy.get("compliance_notes"):
                for n in policy["compliance_notes"]:
                    st.markdown(f"- {n}")

    # Fraud Risk & Duplicate Check
    fraud = result.get("fraud_risk_indicators", {})
    if fraud:
        st.divider()
        st.subheader(f"Fraud Risk Assessment (Score: {fraud.get('fraud_score', 0)}/10)")
        st.metric("Overall Risk", fraud.get("overall_risk", ""))
        flags = fraud.get("red_flags", [])
        if flags:
            for f in flags:
                sev = f.get("severity", "Medium").lower()
                cls = f"flag-{sev}"
                st.markdown(f'<div class="flag-card {cls}"><strong>{f.get("indicator", "")}</strong> '
                           f'({f.get("severity", "")})<br/>{f.get("explanation", "")}</div>',
                           unsafe_allow_html=True)
        else:
            st.success("No significant fraud indicators detected")

    dup = result.get("duplicate_check_indicators", {})
    if dup and dup.get("duplicate_signals"):
        st.warning(f"**Duplicate Check:** {dup.get('recommendation', '')}")
        for s in dup["duplicate_signals"]:
            st.markdown(f"- {s}")

    # Pend Reasons
    pends = result.get("pend_reasons", [])
    if pends:
        st.divider()
        st.subheader("Pend Reasons / Information Needed")
        pdf_data = pd.DataFrame([{
            "Reason": p.get("reason", ""),
            "Information Needed": p.get("information_needed", ""),
            "Source": p.get("source", ""),
            "Deadline (Days)": p.get("deadline_days", 0),
        } for p in pends])
        st.dataframe(pdf_data, use_container_width=True, hide_index=True)

    # Appeal Likelihood
    appeal = result.get("appeal_likelihood", {})
    if appeal:
        st.divider()
        st.subheader("Appeal Likelihood")
        st.metric("Likelihood if Denied", appeal.get("likelihood", ""))
        if appeal.get("common_appeal_grounds"):
            st.markdown("**Common Appeal Grounds:**")
            for g in appeal["common_appeal_grounds"]:
                st.markdown(f"- {g}")
        if appeal.get("recommended_preparation"):
            st.markdown("**Preparation:**")
            for p in appeal["recommended_preparation"]:
                st.markdown(f"- {p}")

    st.divider()
    st.download_button("Download Claim Review (JSON)", json.dumps(result, indent=2),
                       "claim_review.json", "application/json")
