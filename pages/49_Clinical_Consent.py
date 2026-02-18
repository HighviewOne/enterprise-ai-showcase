"""ConsentAI - Clinical Trial Consent Form Analysis - Streamlit Application."""

import os
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from engines.consent_engine import analyze_consent

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #1b5e20 0%, #00695c 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: #a5d6a7; margin: 0; }
    .risk-card { background: #f8f9fa; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem; }
    .risk-serious { border-left: 4px solid #f44336; }
    .risk-moderate { border-left: 4px solid #ff9800; }
    .risk-mild { border-left: 4px solid #4caf50; }
    .flag-card { background: #fff3e0; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem; }
    .flag-high { border-left: 4px solid #d32f2f; }
    .flag-medium { border-left: 4px solid #ff9800; }
    .flag-low { border-left: 4px solid #fdd835; }
    .pro-card { background: #e8f5e9; border-radius: 8px; padding: 0.6rem; margin-bottom: 0.3rem; }
    .con-card { background: #ffebee; border-radius: 8px; padding: 0.6rem; margin-bottom: 0.3rem; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**ConsentAI** transforms dense clinical trial consent forms into accessible, "
            "patient-friendly summaries and interactive Q&A.")

st.markdown("""<div class="hero"><h1>ConsentAI</h1>
<p>Making clinical trial consent forms understandable for every patient</p></div>""",
unsafe_allow_html=True)

SAMPLE_CONSENT = """INFORMED CONSENT FORM - PHASE III CLINICAL TRIAL

PROTOCOL: ONCO-2024-0847
TITLE: A Randomized, Double-Blind, Placebo-Controlled Phase III Study of Pembrolizumab (MK-3475) Plus Chemotherapy Versus Placebo Plus Chemotherapy as First-Line Treatment in Participants with Advanced Non-Small Cell Lung Cancer (NSCLC)

SPONSOR: Global Oncology Research Alliance (GORA)
PRINCIPAL INVESTIGATOR: Dr. Sarah Chen, MD, PhD - Memorial Cancer Center

1. PURPOSE OF THE STUDY
You are being asked to take part in a research study. This study is testing whether adding an immunotherapy drug called pembrolizumab to standard chemotherapy works better than chemotherapy alone for treating advanced non-small cell lung cancer (NSCLC) that has spread to other parts of the body or cannot be removed by surgery. Approximately 1,200 participants will be enrolled across 180 sites in 25 countries.

2. PROCEDURES
If you agree to participate, you will be randomly assigned (like flipping a coin) to one of two groups:
- Group A: Pembrolizumab 200mg IV every 3 weeks + carboplatin/pemetrexed chemotherapy
- Group B: Placebo IV every 3 weeks + carboplatin/pemetrexed chemotherapy
Neither you nor your doctor will know which group you are in. Treatment continues for up to 35 cycles (approximately 2 years) or until disease progression, unacceptable toxicity, or withdrawal.

Screening Period (2-4 weeks): Physical exam, blood tests, CT/PET scan, tumor biopsy, ECG, medical history review
Treatment Period (up to 2 years): IV infusion every 3 weeks (approximately 30-60 minutes per infusion), blood tests before each cycle, CT scans every 9 weeks, quality of life questionnaires
Follow-up Period (2 years after treatment): Visits every 3 months for the first year, then every 6 months

3. RISKS AND DISCOMFORTS
Pembrolizumab may cause the immune system to attack normal organs. Serious risks include:
- Immune-mediated pneumonitis (inflammation of the lungs) - occurs in 3-5% of patients, can be fatal in rare cases (<0.5%)
- Immune-mediated hepatitis (liver inflammation) - occurs in 1-2% of patients
- Immune-mediated colitis (bowel inflammation) - occurs in 1-3% of patients, may require hospitalization
- Thyroid disorders (hypothyroidism/hyperthyroidism) - occurs in 8-12% of patients
- Immune-mediated nephritis (kidney inflammation) - occurs in <1% of patients
- Severe skin reactions - occurs in 1-2% of patients
- Type 1 diabetes mellitus - occurs in <1% of patients
- Infusion reactions - occurs in 1-4% of patients

Chemotherapy side effects include: nausea/vomiting, hair loss, fatigue, low blood counts (increased infection risk), peripheral neuropathy, kidney toxicity.

There may be risks that are currently unknown.

4. BENEFITS
You may or may not benefit from this study. Possible benefits include tumor shrinkage, slowed disease progression, and potentially extended survival. Based on prior Phase II data, the combination showed a 47% objective response rate compared to 18% with chemotherapy alone. However, this study is being conducted to confirm these preliminary findings.

5. ALTERNATIVES
You do not have to join this study. Alternative treatment options include: standard chemotherapy alone, other approved immunotherapy combinations, radiation therapy, participation in other clinical trials, or best supportive care (symptom management only).

6. COMPENSATION
You will be reimbursed for travel expenses up to $75 per visit. The study drug and study-related procedures will be provided at no cost. Standard-of-care costs may be billed to your insurance.

7. CONFIDENTIALITY
Your medical records will be kept confidential. However, regulatory authorities (FDA, EMA), the sponsor (GORA), the Institutional Review Board (IRB), and authorized representatives may review your records. Data will be de-identified for analysis. Results may be published in medical journals without identifying you.

8. VOLUNTARY PARTICIPATION
Your participation is entirely voluntary. You may withdraw at any time without penalty or loss of benefits to which you are otherwise entitled. Your decision will not affect your medical care. If you withdraw, data collected up to that point may still be used in the analysis.

9. INJURY PROVISIONS
If you are injured as a direct result of being in this study, Memorial Cancer Center will provide necessary medical treatment. The costs of this treatment may be billed to your insurance. No other compensation is routinely available. You do not waive any legal rights by signing this form.

CONTACT: For questions about the study - Dr. Sarah Chen: (555) 234-5678
For questions about your rights as a research participant - IRB Office: (555) 345-6789
For emergencies - 24-hour study nurse line: (555) 456-7890"""

with st.form("consent_form"):
    consent_text = st.text_area("Clinical Trial Consent Form", height=300, value=SAMPLE_CONSENT)
    st.markdown("**Patient Profile**")
    pc1, pc2, pc3, pc4 = st.columns(4)
    with pc1:
        patient_age = st.number_input("Patient Age", min_value=18, max_value=110, value=62)
    with pc2:
        education_level = st.selectbox("Education Level",
            ["Elementary School", "Middle School", "High School", "Some College",
             "Bachelor's Degree", "Master's Degree", "Doctoral Degree"],
            index=3)
    with pc3:
        language_preference = st.selectbox("Language Preference",
            ["English", "Spanish", "Mandarin", "Hindi", "Arabic", "Portuguese",
             "French", "German", "Japanese", "Korean"],
            index=0)
    with pc4:
        health_literacy = st.selectbox("Health Literacy Level",
            ["Low", "Below Average", "Average", "Above Average", "High"],
            index=2)

    submitted = st.form_submit_button("Analyze Consent Form", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        consent_text=consent_text[:80000],
        patient_age=str(patient_age),
        education_level=education_level,
        language_preference=language_preference,
        health_literacy=health_literacy,
    )

    with st.spinner("Analyzing consent form..."):
        try:
            result = analyze_consent(config, api_key)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    # Consent Summary
    summary = result.get("consent_summary", {})
    st.subheader("Consent Summary")
    sm1, sm2, sm3, sm4 = st.columns(4)
    sm1.metric("Trial Name", summary.get("trial_name", "")[:30])
    sm2.metric("Phase", summary.get("trial_phase", ""))
    sm3.metric("Duration", summary.get("duration", ""))
    sm4.metric("Participants", summary.get("participant_count", ""))
    st.info(summary.get("plain_language_summary", ""))

    # Key Risks & Benefits side by side
    rc1, rc2 = st.columns(2)
    risks = result.get("key_risks", [])
    if risks:
        with rc1:
            st.divider()
            st.subheader("Key Risks")
            for r in risks:
                sev = r.get("severity", "Moderate").lower()
                cls = f"risk-{sev}"
                st.markdown(
                    f'<div class="risk-card {cls}">'
                    f'<strong>{r.get("risk", "")}</strong> '
                    f'({r.get("severity", "")} - {r.get("likelihood", "")})<br/>'
                    f'{r.get("plain_explanation", "")}<br/>'
                    f'<em>Management: {r.get("what_doctors_will_do", "")}</em></div>',
                    unsafe_allow_html=True)

    benefits = result.get("benefits_explained", {})
    if benefits:
        with rc2:
            st.divider()
            st.subheader("Benefits Explained")
            for b in benefits.get("potential_benefits", []):
                st.markdown(f"- {b}")
            st.markdown(f"**Likelihood:** {benefits.get('likelihood_of_benefit', '')}")
            st.markdown(f"**vs Standard Care:** {benefits.get('compared_to_standard_care', '')}")

    # Procedures Timeline
    timeline = result.get("procedures_timeline", [])
    if timeline:
        st.divider()
        st.subheader("Procedures Timeline")
        tl_df = pd.DataFrame([{
            "Phase": t.get("phase", ""),
            "Timeframe": t.get("timeframe", ""),
            "Visits": t.get("visits_required", ""),
            "Time Commitment": t.get("time_commitment", ""),
            "Procedures": ", ".join(t.get("procedures", [])),
        } for t in timeline])
        st.dataframe(tl_df, use_container_width=True, hide_index=True)

    # Rights & Decision Support side by side
    dc1, dc2 = st.columns(2)
    rights = result.get("rights_and_protections", {})
    if rights:
        with dc1:
            st.divider()
            st.subheader("Your Rights & Protections")
            st.markdown(f"**Voluntary:** {rights.get('voluntary_participation', '')}")
            st.markdown(f"**Withdrawal:** {rights.get('right_to_withdraw', '')}")
            st.markdown(f"**Privacy:** {rights.get('confidentiality', '')}")
            st.markdown(f"**Compensation:** {rights.get('compensation', '')}")
            st.markdown(f"**If Injured:** {rights.get('injury_provisions', '')}")

    decision = result.get("decision_support", {})
    if decision:
        with dc2:
            st.divider()
            st.subheader("Decision Support")
            for p in decision.get("pros", []):
                st.markdown(f'<div class="pro-card">+ {p}</div>', unsafe_allow_html=True)
            for c in decision.get("cons", []):
                st.markdown(f'<div class="con-card">- {c}</div>', unsafe_allow_html=True)
            if decision.get("questions_to_ask_doctor"):
                st.markdown("**Questions to Ask Your Doctor:**")
                for q in decision["questions_to_ask_doctor"]:
                    st.markdown(f"- {q}")

    # FAQ
    faq = result.get("faq", [])
    if faq:
        st.divider()
        st.subheader("Frequently Asked Questions")
        for item in faq:
            with st.expander(item.get("question", "")):
                st.markdown(item.get("answer", ""))

    # Readability & Accessibility
    ra1, ra2 = st.columns(2)
    readability = result.get("readability_assessment", {})
    if readability:
        with ra1:
            st.divider()
            st.subheader("Readability Assessment")
            st.metric("Original Reading Level", readability.get("original_reading_level", ""))
            st.metric("Recommended Level", readability.get("recommended_reading_level", ""))
            st.metric("Accessibility Grade", readability.get("accessibility_grade", ""))
            jargon = readability.get("jargon_terms_found", [])
            if jargon:
                st.markdown("**Jargon Found:**")
                for j in jargon:
                    st.markdown(f"- {j}")

    access = result.get("accessibility_notes", {})
    if access:
        with ra2:
            st.divider()
            st.subheader("Accessibility Notes")
            st.markdown(f"**Language:** {access.get('language_considerations', '')}")
            st.markdown(f"**Cultural Notes:** {access.get('cultural_sensitivity', '')}")
            if access.get("simplified_version_needed"):
                st.warning("A simplified version of this consent form is recommended.")
            if access.get("interpreter_recommended"):
                st.warning("An interpreter is recommended for this patient.")

    # Red Flags
    flags = result.get("red_flags", [])
    if flags:
        st.divider()
        st.subheader("Red Flags")
        for f in flags:
            sev = f.get("severity", "Medium").lower()
            cls = f"flag-{sev}"
            st.markdown(
                f'<div class="flag-card {cls}">'
                f'<strong>{f.get("concern", "")}</strong> ({f.get("severity", "")})<br/>'
                f'{f.get("explanation", "")}<br/>'
                f'<em>Ask about: {f.get("recommendation", "")}</em></div>',
                unsafe_allow_html=True)

    st.divider()
    st.download_button("Download Consent Analysis (JSON)", json.dumps(result, indent=2),
                       "consent_analysis.json", "application/json")
