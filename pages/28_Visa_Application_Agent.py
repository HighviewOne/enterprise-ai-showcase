"""AI Visa Application Agent - B1/B2 Visa Guidance - Streamlit Application."""

import os
import json
import streamlit as st
from dotenv import load_dotenv

from engines.visa_engine import analyze_application

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .risk-card { background: #f8f9fa; border-radius: 10px; padding: 1.2rem; margin-bottom: 0.8rem; }
    .risk-low { border-left: 4px solid #4caf50; }
    .risk-medium { border-left: 4px solid #ff9800; }
    .risk-high { border-left: 4px solid #f44336; }
    .check-pass { color: #4caf50; font-weight: bold; }
    .check-fail { color: #f44336; font-weight: bold; }
    .check-warn { color: #ff9800; font-weight: bold; }
    .step-card { background: #e3f2fd; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
        border-left: 4px solid #1565c0; }
    .mistake-card { background: #fff3e0; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
        border-left: 4px solid #e65100; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.warning("**Disclaimer:** This is an educational tool only. It does NOT constitute "
               "legal or immigration advice. Always consult a licensed immigration attorney "
               "for your specific situation.")

st.markdown("""<div class="hero"><h1>AI Visa Application Agent</h1>
<p>AI-powered B1/B2 visa application guidance — DS-160 help, interview prep, and consulate tips</p></div>""",
unsafe_allow_html=True)

with st.form("visa_form"):
    st.subheader("Applicant Information")
    c1, c2, c3 = st.columns(3)
    with c1:
        full_name = st.text_input("Full Name (as on passport)", value="Priya Sharma")
        dob = st.text_input("Date of Birth", value="1975-03-15")
    with c2:
        nationality = st.text_input("Nationality", value="India")
        passport_number = st.text_input("Passport Number", value="K8834521")
    with c3:
        purpose = st.selectbox("Purpose of Visit",
            ["Tourism/Sightseeing", "Business Meetings", "Medical Treatment",
             "Visiting Family/Friends", "Conference/Event", "Mixed Purpose"], index=3)
        duration = st.text_input("Intended Duration of Stay", value="3 weeks")

    sponsor = st.text_input("US Sponsor/Host Details",
        value="Brother - Rajesh Sharma, US Citizen since 2015, residing in Houston, TX. "
              "Software Engineer at Dell Technologies.")

    st.subheader("Employment & Financial Details")
    e1, e2 = st.columns(2)
    with e1:
        employment_status = st.selectbox("Employment Status",
            ["Employed", "Self-Employed", "Retired", "Student", "Homemaker"])
        occupation = st.text_input("Current Occupation", value="Senior Manager, IT Operations")
        employer = st.text_input("Employer/Organization", value="Infosys Ltd, Bangalore")
    with e2:
        monthly_income = st.text_input("Monthly Income (USD equivalent)", value="$3,000")
        savings = st.text_area("Savings & Assets",
            value="Fixed Deposits: INR 40 lakh (~$48,000)\n"
                  "Mutual Funds: INR 15 lakh (~$18,000)\n"
                  "Property: Owned apartment in Bangalore (valued ~$120,000)\n"
                  "Provident Fund: INR 25 lakh (~$30,000)", height=120)
        previous_visa = st.selectbox("Previous US Visa",
            ["No - First time applicant", "Yes - Approved", "Yes - Rejected"])

    st.subheader("Travel & Consulate")
    t1, t2 = st.columns(2)
    with t1:
        travel_history = st.text_area("Countries Visited (last 5 years)",
            value="UK (2023 - tourist, 10 days)\nSingapore (2022 - business, 5 days)\n"
                  "Thailand (2021 - tourist, 7 days)\nDubai (2024 - transit + tourist, 4 days)",
            height=120)
    with t2:
        consulate = st.text_input("Preferred Consulate City", value="Mumbai")
        additional_info = st.text_area("Additional Information",
            value="Married with two children (ages 12 and 16) who attend school in Bangalore. "
                  "Husband is employed as a professor at IISc. Family will remain in India during visit.",
            height=120)

    submitted = st.form_submit_button("Analyze Application", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        full_name=full_name, dob=dob, nationality=nationality, passport_number=passport_number,
        purpose=purpose, sponsor=sponsor, employment_status=employment_status,
        occupation=occupation, employer=employer, monthly_income=monthly_income,
        savings=savings, previous_visa=previous_visa, travel_history=travel_history,
        duration=duration, consulate=consulate, additional_info=additional_info,
    )

    with st.spinner("Analysing application..."):
        try:
            result = analyze_application(config, api_key)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    # Applicant Assessment
    assess = result.get("applicant_assessment", {})
    st.subheader("Applicant Assessment")
    m1, m2, m3, m4 = st.columns(4)
    elig = assess.get("eligibility_rating", "Moderate")
    elig_color = "#4caf50" if elig == "Strong" else "#f44336" if elig == "Weak" else "#ff9800"
    m1.metric("Eligibility", elig)
    m2.metric("Visa Type", assess.get("visa_type_recommendation", "B1/B2"))
    risk = assess.get("risk_level", "Medium")
    m3.metric("Risk Level", risk)
    m4.metric("Recommendation", "Proceed" if risk != "High" else "Caution")

    risk_cls = "risk-low" if risk == "Low" else "risk-high" if risk == "High" else "risk-medium"
    st.markdown(f'<div class="risk-card {risk_cls}">{assess.get("overall_assessment", "")}</div>',
                unsafe_allow_html=True)

    ac1, ac2 = st.columns(2)
    with ac1:
        st.markdown("**Strengths:**")
        for s in assess.get("strengths", []):
            st.markdown(f'- <span class="check-pass">{s}</span>', unsafe_allow_html=True)
    with ac2:
        st.markdown("**Risk Factors:**")
        for r in assess.get("risk_factors", []):
            st.markdown(f'- <span class="check-warn">{r}</span>', unsafe_allow_html=True)

    # DS-160 Guidance
    ds160 = result.get("ds160_guidance", [])
    if ds160:
        st.divider()
        st.subheader("DS-160 Section-by-Section Guidance")
        for section in ds160:
            with st.expander(f"📋 {section.get('section', '')}"):
                for field in section.get("fields", []):
                    st.markdown(f"**{field.get('field', '')}**")
                    st.markdown(f"  Guidance: {field.get('guidance', '')}")
                    if field.get("tip"):
                        st.caption(f"Tip: {field['tip']}")

    # Document Checklist
    docs = result.get("document_checklist", [])
    if docs:
        st.divider()
        st.subheader("Document Checklist")
        for doc in docs:
            status = doc.get("status", "Required")
            icon = "✅" if status == "Required" else "📎" if status == "Recommended" else "📄"
            cls = "check-fail" if status == "Required" else "check-warn" if status == "Recommended" else "check-pass"
            st.markdown(f'{icon} <span class="{cls}">[{status}]</span> **{doc.get("document", "")}** — {doc.get("notes", "")}',
                       unsafe_allow_html=True)

    # Interview Preparation
    interview = result.get("interview_preparation", {})
    if interview:
        st.divider()
        st.subheader("Interview Preparation")
        for q in interview.get("common_questions", []):
            with st.expander(f"❓ {q.get('question', '')}"):
                st.markdown(f"**Recommended Approach:** {q.get('recommended_approach', '')}")
                st.info(f"**Sample Answer:** {q.get('sample_answer', '')}")
                if q.get("pitfalls"):
                    st.warning(f"**Avoid:** {q['pitfalls']}")

        ic1, ic2 = st.columns(2)
        with ic1:
            st.markdown("**General Tips:**")
            for tip in interview.get("general_tips", []):
                st.markdown(f"- {tip}")
        with ic2:
            st.markdown(f"**Dress Code:** {interview.get('dress_code', 'Business formal')}")
            st.markdown(f"**Timing:** {interview.get('timing', 'Arrive 15 minutes early')}")

    # Consulate Guidance
    consulate_info = result.get("consulate_guidance", {})
    if consulate_info:
        st.divider()
        st.subheader("Consulate Guidance")
        cg1, cg2 = st.columns(2)
        with cg1:
            st.markdown(f"**Recommended Consulate:** {consulate_info.get('recommended_consulate', '')}")
            st.markdown(f"**Processing Time:** {consulate_info.get('processing_time', '')}")
            st.markdown(f"**Appointment Tips:** {consulate_info.get('appointment_tips', '')}")
        with cg2:
            drop = consulate_info.get("drop_off_eligibility", False)
            drop_cls = "check-pass" if drop else "check-fail"
            st.markdown(f'**Interview Waiver (Drop-off):** <span class="{drop_cls}">{"Eligible" if drop else "Not Eligible"}</span>',
                       unsafe_allow_html=True)
            st.caption(consulate_info.get("drop_off_details", ""))
            if consulate_info.get("emergency_appointment"):
                st.caption(f"Emergency: {consulate_info['emergency_appointment']}")

    # Timeline
    timeline = result.get("timeline", [])
    if timeline:
        st.divider()
        st.subheader("Application Timeline")
        for i, step in enumerate(timeline, 1):
            st.markdown(f'<div class="step-card"><strong>Step {i}: {step.get("step", "")}</strong><br/>'
                       f'⏰ {step.get("timeframe", "")} — {step.get("notes", "")}</div>',
                       unsafe_allow_html=True)

    # Common Mistakes
    mistakes = result.get("common_mistakes", [])
    if mistakes:
        st.divider()
        st.subheader("Common Mistakes to Avoid")
        for m in mistakes:
            st.markdown(f'<div class="mistake-card"><strong>⚠️ {m.get("mistake", "")}</strong><br/>'
                       f'Consequence: {m.get("consequence", "")}<br/>'
                       f'<em>Prevention: {m.get("prevention", "")}</em></div>',
                       unsafe_allow_html=True)

    # Overall Recommendation
    rec = result.get("overall_recommendation", "")
    if rec:
        st.divider()
        st.success(f"**Overall Recommendation:** {rec}")

    st.divider()
    st.download_button("Download Guidance Report (JSON)", json.dumps(result, indent=2),
                       "visa_guidance.json", "application/json")
