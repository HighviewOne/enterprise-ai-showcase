"""PatientEdge - AI Health Advocate - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.advocate_engine import analyze_patient

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #0d47a1 0%, #1565c0 50%, #1e88e5 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: #b3e5fc; margin: 0; }
    .med-card { background: #e3f2fd; border: 1px solid #90caf9; border-radius: 8px;
        padding: 1rem; margin-bottom: 0.5rem; }
    .savings-card { background: #e8f5e9; border: 2px solid #4caf50; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .warning-card { background: #fff3e0; border-left: 4px solid #ff9800; padding: 0.8rem;
        border-radius: 4px; margin-bottom: 0.4rem; }
    .question-card { background: #f3e5f5; border: 1px solid #ce93d8; border-radius: 8px;
        padding: 0.8rem; margin-bottom: 0.4rem; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**PatientEdge** helps patients understand medications, find cost savings, "
            "coordinate care, and prepare for doctor visits.")
    st.warning("This tool provides educational information only. Always consult your "
               "healthcare provider before making changes to your treatment.")

st.markdown("""<div class="hero"><h1>PatientEdge</h1>
<p>Your AI health advocate - reduce costs, understand care, ask better questions</p></div>""",
unsafe_allow_html=True)

with st.form("patient_form"):
    st.markdown("**Patient Scenario**")
    c1, c2 = st.columns(2)
    with c1:
        patient_scenario = st.text_area("Patient Background", height=120,
            value="62-year-old male, retired teacher. Diagnosed with Type 2 Diabetes (8 years) "
                  "and Hypertension (12 years). BMI 31.2. Non-smoker. Moderate activity level. "
                  "Lives alone, fixed income from pension. Concerned about rising medication costs "
                  "and managing multiple conditions.")
        medications = st.text_area("Current Medications", height=150,
            value="1. Metformin 1000mg twice daily (diabetes)\n"
                  "2. Jardiance (empagliflozin) 25mg once daily (diabetes)\n"
                  "3. Lisinopril 20mg once daily (hypertension)\n"
                  "4. Amlodipine 10mg once daily (hypertension)")
    with c2:
        diagnoses = st.text_area("Diagnoses", height=80,
            value="Type 2 Diabetes Mellitus (E11.9)\nEssential Hypertension (I10)")
        insurance_type = st.selectbox("Insurance Type",
            ["Medicare Part D", "Medicare Advantage", "Employer PPO", "Employer HMO",
             "ACA Marketplace Silver", "ACA Marketplace Gold", "Medicaid", "Uninsured"],
            index=0)
        current_costs = st.text_area("Current Monthly Costs", height=80,
            value="Metformin: $15/month (generic)\n"
                  "Jardiance: $520/month (brand, after Medicare coverage gap)\n"
                  "Lisinopril: $8/month (generic)\n"
                  "Amlodipine: $12/month (generic)\n"
                  "Total out-of-pocket: ~$555/month")

    concerns = st.text_area("Specific Concerns or Questions", height=80,
        value="Monthly medication costs are eating into my pension. Is there a cheaper alternative "
              "to Jardiance? Am I on the right medications? What screenings should I be getting? "
              "I sometimes feel dizzy when standing up - could it be my meds?")

    submitted = st.form_submit_button("Analyze & Advocate", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(patient_scenario=patient_scenario, medications=medications,
                  diagnoses=diagnoses, insurance_type=insurance_type,
                  current_costs=current_costs, concerns=concerns)

    with st.spinner("Analyzing medications, costs, and care options..."):
        try:
            result = analyze_patient(config, api_key)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    # Savings Summary at top
    savings = result.get("savings_opportunities", {})
    if savings:
        total_monthly = savings.get("total_potential_monthly_savings", 0)
        total_annual = savings.get("total_potential_annual_savings", 0)
        st.markdown(f'<div class="savings-card"><h2>Potential Savings</h2>'
                   f'<span style="font-size:2rem;font-weight:bold;color:#2e7d32">'
                   f'${total_monthly:,.0f}/month</span> | '
                   f'<span style="font-size:1.5rem;color:#388e3c">'
                   f'${total_annual:,.0f}/year</span></div>', unsafe_allow_html=True)

    # Cost Comparison Chart
    cost_data = result.get("cost_analysis", [])
    if cost_data:
        st.divider()
        st.subheader("Cost Analysis")

        med_names = [c.get("medication", "") for c in cost_data]
        current_costs_vals = [c.get("current_monthly_cost", 0) for c in cost_data]
        generic_costs = [c.get("generic_monthly_cost", 0) or 0 for c in cost_data]
        potential_savings = [c.get("potential_monthly_savings", 0) for c in cost_data]

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Current Cost", x=med_names, y=current_costs_vals,
                             marker_color="#ef5350",
                             text=[f"${v:,.0f}" for v in current_costs_vals],
                             textposition="outside"))
        optimized = [max(cur - sav, 0) for cur, sav in zip(current_costs_vals, potential_savings)]
        fig.add_trace(go.Bar(name="Optimized Cost", x=med_names, y=optimized,
                             marker_color="#66bb6a",
                             text=[f"${v:,.0f}" for v in optimized],
                             textposition="outside"))
        fig.update_layout(barmode="group", title="Monthly Medication Costs: Current vs Optimized",
                          yaxis_title="Cost ($)", height=400)
        st.plotly_chart(fig, use_container_width=True)

        # Cost detail table
        for c in cost_data:
            st.markdown(f'<div class="med-card"><strong>{c.get("medication", "")}</strong> - '
                       f'${c.get("current_monthly_cost", 0):,.0f}/month<br/>'
                       f'Generic: {c.get("generic_alternative", "N/A")} '
                       f'(${c.get("generic_monthly_cost", 0) or 0:,.0f}/month)<br/>'
                       f'Potential Savings: <strong>${c.get("potential_monthly_savings", 0):,.0f}/month</strong>'
                       f'</div>', unsafe_allow_html=True)
            if c.get("patient_assistance_programs"):
                for p in c["patient_assistance_programs"]:
                    st.markdown(f"  - {p}")

    # Medication Review
    meds = result.get("medication_review", [])
    if meds:
        st.divider()
        st.subheader("Medication Review")
        for m in meds:
            with st.expander(f"{m.get('medication', '')} ({m.get('dosage', '')}) - {m.get('importance', '')}"):
                st.markdown(f"**Purpose:** {m.get('purpose', '')}")
                st.markdown(f"**How it Works:** {m.get('how_it_works', '')}")
                if m.get("common_side_effects"):
                    st.markdown("**Side Effects:** " + ", ".join(m["common_side_effects"]))
                if m.get("interactions"):
                    st.markdown("**Interactions:** " + ", ".join(m["interactions"]))

    # Insurance Optimization & Care Coordination
    ic1, ic2 = st.columns(2)
    ins = result.get("insurance_optimization", {})
    if ins:
        with ic1:
            st.divider()
            st.subheader("Insurance Optimization")
            if ins.get("formulary_tips"):
                st.markdown("**Formulary Tips:**")
                for t in ins["formulary_tips"]:
                    st.markdown(f"- {t}")
            if ins.get("tier_optimization"):
                st.markdown("**Tier Optimization:**")
                for t in ins["tier_optimization"]:
                    st.markdown(f"- {t}")
            if ins.get("prior_auth_guidance"):
                st.markdown("**Prior Auth Guidance:**")
                for p in ins["prior_auth_guidance"]:
                    st.markdown(f"- {p}")

    care = result.get("care_coordination", {})
    if care:
        with ic2:
            st.divider()
            st.subheader("Care Coordination")
            specs = care.get("specialist_recommendations", [])
            if specs:
                st.markdown("**Recommended Specialists:**")
                for s in specs:
                    st.markdown(f"- **{s.get('specialist', '')}**: {s.get('reason', '')} ({s.get('frequency', '')})")
            screens = care.get("screening_schedule", [])
            if screens:
                st.markdown("**Screening Schedule:**")
                sdf = pd.DataFrame([{
                    "Screening": s.get("screening", ""),
                    "Frequency": s.get("frequency", ""),
                    "Next Due": s.get("next_due", ""),
                    "Purpose": s.get("purpose", ""),
                } for s in screens])
                st.dataframe(sdf, use_container_width=True, hide_index=True)

    # Disease Education
    edu = result.get("disease_education", [])
    if edu:
        st.divider()
        st.subheader("Understanding Your Conditions")
        for e in edu:
            with st.expander(e.get("condition", "")):
                st.markdown(e.get("plain_explanation", ""))
                if e.get("lifestyle_modifications"):
                    st.markdown("**Lifestyle Changes:**")
                    for lm in e["lifestyle_modifications"]:
                        st.markdown(f"- {lm}")
                if e.get("warning_signs"):
                    st.markdown("**Warning Signs (seek immediate care):**")
                    for w in e["warning_signs"]:
                        st.markdown(f'<div class="warning-card">{w}</div>', unsafe_allow_html=True)
                st.markdown(f"**Long-term Outlook:** {e.get('long_term_outlook', '')}")

    # Questions for Doctor
    questions = result.get("questions_for_doctor", [])
    if questions:
        st.divider()
        st.subheader("Questions for Your Next Doctor Visit")
        for q in questions:
            st.markdown(f'<div class="question-card"><strong>{q.get("question", "")}</strong><br/>'
                       f'<em>Why: {q.get("why_important", "")}</em></div>', unsafe_allow_html=True)

    # Resource Directory
    resources = result.get("resource_directory", [])
    if resources:
        st.divider()
        st.subheader("Resource Directory")
        rdf = pd.DataFrame([{
            "Resource": r.get("resource", ""),
            "Type": r.get("type", ""),
            "Description": r.get("description", ""),
            "Eligibility": r.get("eligibility", ""),
            "Contact": r.get("contact", ""),
        } for r in resources])
        st.dataframe(rdf, use_container_width=True, hide_index=True)

    st.divider()
    st.download_button("Download Advocacy Report (JSON)", json.dumps(result, indent=2),
                       "patient_advocacy_report.json", "application/json")
