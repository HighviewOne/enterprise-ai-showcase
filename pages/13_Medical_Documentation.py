"""AI Medical Documentation Assistant - Streamlit Application."""

import os
import json
import streamlit as st
from dotenv import load_dotenv

from engines.doc_engine import generate_clinical_note

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #00b4d8 0%, #0077b6 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .soap-card { background: #f8f9fa; border-radius: 10px; padding: 1.2rem;
        margin-bottom: 0.8rem; }
    .soap-s { border-top: 4px solid #2196F3; }
    .soap-o { border-top: 4px solid #4CAF50; }
    .soap-a { border-top: 4px solid #FF9800; }
    .soap-p { border-top: 4px solid #9C27B0; }
    .code-chip { display: inline-block; background: #e3f2fd; color: #1565c0;
        padding: 0.2rem 0.6rem; border-radius: 20px; margin: 0.1rem; font-size: 0.85rem;
        font-weight: 500; }
    .flag-warn { background: #fff3cd; border-left: 4px solid #ffc107;
        padding: 0.8rem; border-radius: 6px; margin: 0.3rem 0; }
    .flag-danger { background: #f8d7da; border-left: 4px solid #dc3545;
        padding: 0.8rem; border-radius: 6px; margin: 0.3rem 0; }
    .flag-info { background: #d1ecf1; border-left: 4px solid #17a2b8;
        padding: 0.8rem; border-radius: 6px; margin: 0.3rem 0; }
    .dx-card { background: #f0f7ff; border-radius: 8px; padding: 0.8rem;
        border-left: 4px solid #0077b6; margin-bottom: 0.4rem; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.warning("**Disclaimer:** This tool is for educational and demonstration purposes only. "
               "It should NOT be used for actual clinical documentation or medical decision-making.")

st.markdown("""<div class="hero"><h1>AI Medical Documentation Assistant</h1>
<p>Transform doctor-patient conversations into structured clinical notes with SOAP format and coding suggestions</p></div>""",
unsafe_allow_html=True)

SAMPLE_TRANSCRIPT = """Doctor: Good morning, Mrs. Johnson. What brings you in today?

Patient: Hi Doctor. I've been having these terrible headaches for the past two weeks. They're mostly on the right side and sometimes I feel nauseous with them.

Doctor: I'm sorry to hear that. Can you describe the headaches more? How often do they happen?

Patient: They come about 3-4 times a week, usually in the afternoon. The pain is throbbing and rates about a 7 out of 10. Light makes it worse and I have to lie down in a dark room.

Doctor: Have you had headaches like this before?

Patient: I used to get migraines in my 20s but they went away. I'm 45 now and they seem to be back. My mother also had migraines.

Doctor: Are you taking anything for them currently?

Patient: Just over-the-counter ibuprofen, 400mg, but it only helps a little. I'm also on lisinopril 10mg for my blood pressure and metformin 500mg twice daily for my diabetes.

Doctor: Any allergies?

Patient: Yes, I'm allergic to sulfa drugs - I get a rash.

Doctor: Let me do a quick exam. Your blood pressure today is 138/88. Neurological exam is normal - pupils equal and reactive, no focal deficits. There's some tenderness over the right temporal area.

Doctor: Based on your history and exam, this looks like a recurrence of migraine without aura. I'd like to start you on sumatriptan 50mg to take at the onset of a headache. I also want to consider a preventive medication. Let's try propranolol 40mg daily since it can also help with your blood pressure.

Patient: Are there any side effects I should watch for?

Doctor: Sumatriptan can cause tingling or chest tightness - if you get chest pain, stop and call us. Propranolol may cause fatigue initially. Keep a headache diary and avoid known triggers like stress, bright lights, and skipping meals. Let's see you back in 6 weeks. If the headaches worsen or you develop any vision changes, come in sooner.

Patient: Thank you, Doctor."""

with st.form("doc_form"):
    transcript = st.text_area("Doctor-Patient Conversation Transcript",
                               value=SAMPLE_TRANSCRIPT, height=300,
                               placeholder="Paste the conversation transcript here...")
    c1, c2 = st.columns(2)
    with c1:
        specialty = st.selectbox("Specialty",
            ["General Practice / Family Medicine", "Internal Medicine", "Neurology",
             "Cardiology", "Orthopedics", "Dermatology", "Pediatrics",
             "Psychiatry", "OB/GYN", "Emergency Medicine", "Other"])
    with c2:
        setting = st.selectbox("Visit Setting",
            ["Outpatient Clinic", "Emergency Department", "Telehealth",
             "Inpatient", "Urgent Care"])
    notes = st.text_input("Additional Context",
                           value="Follow-up patient, established care.",
                           placeholder="Any additional notes for the scribe...")

    submitted = st.form_submit_button("Generate Clinical Note", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()
    if not transcript.strip():
        st.error("Please provide a conversation transcript.")
        st.stop()

    config = dict(transcript=transcript, specialty=specialty, setting=setting, notes=notes)

    with st.spinner("Generating clinical documentation..."):
        try:
            result = generate_clinical_note(config, api_key)
        except Exception as e:
            st.error(f"Generation failed: {e}")
            st.stop()

    st.warning(result.get("disclaimer", "For educational purposes only."))

    # Patient Summary
    ps = result.get("patient_summary", {})
    st.subheader("Visit Overview")
    vc1, vc2, vc3 = st.columns(3)
    vc1.metric("Chief Complaint", ps.get("chief_complaint", "N/A")[:50])
    vc2.metric("Visit Type", ps.get("visit_type", "N/A"))
    vc3.metric("Urgency", ps.get("urgency", "N/A"))

    # SOAP Note
    soap = result.get("soap_note", {})
    st.divider()
    st.subheader("SOAP Note")

    # Subjective
    subj = soap.get("subjective", {})
    st.markdown('<div class="soap-card soap-s"><h4>S - Subjective</h4>', unsafe_allow_html=True)
    st.markdown(f"**HPI:** {subj.get('history_of_present_illness', 'N/A')}")

    ros = subj.get("review_of_systems", [])
    if ros:
        st.markdown("**Review of Systems:**")
        for r in ros:
            st.markdown(f"- **{r.get('system', '')}:** {r.get('findings', '')}")

    pmh = subj.get("past_medical_history", [])
    if pmh:
        st.markdown(f"**PMH:** {', '.join(pmh)}")
    meds = subj.get("medications", [])
    if meds:
        st.markdown(f"**Medications:** {', '.join(meds)}")
    allergies = subj.get("allergies", [])
    if allergies:
        st.markdown(f"**Allergies:** {', '.join(allergies)}")
    if subj.get("social_history"):
        st.markdown(f"**Social Hx:** {subj['social_history']}")
    if subj.get("family_history"):
        st.markdown(f"**Family Hx:** {subj['family_history']}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Objective
    obj = soap.get("objective", {})
    st.markdown('<div class="soap-card soap-o"><h4>O - Objective</h4>', unsafe_allow_html=True)
    st.markdown(f"**Vitals:** {obj.get('vital_signs', 'Not documented')}")
    pe = obj.get("physical_exam", [])
    if pe:
        st.markdown("**Physical Exam:**")
        for exam in pe:
            st.markdown(f"- **{exam.get('area', '')}:** {exam.get('findings', '')}")
    st.markdown(f"**Labs:** {obj.get('lab_results', 'None')}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Assessment
    assess = soap.get("assessment", {})
    st.markdown('<div class="soap-card soap-a"><h4>A - Assessment</h4>', unsafe_allow_html=True)
    dx_list = assess.get("diagnoses", [])
    for i, dx in enumerate(dx_list, 1):
        conf = dx.get("confidence", "Medium")
        conf_color = "#28a745" if conf == "High" else "#ffc107" if conf == "Medium" else "#dc3545"
        st.markdown(f"""<div class="dx-card">
            <strong>{i}. {dx.get('condition', '')}</strong>
            <span class="code-chip">{dx.get('icd10_suggestion', '')}</span>
            <span style="color:{conf_color}; font-weight:bold;"> ({conf} confidence)</span><br/>
            Status: {dx.get('status', 'N/A')}
        </div>""", unsafe_allow_html=True)

    ddx = assess.get("differential_diagnoses", [])
    if ddx:
        st.markdown(f"**Differential Dx:** {', '.join(ddx)}")
    if assess.get("clinical_reasoning"):
        st.info(f"**Clinical Reasoning:** {assess['clinical_reasoning']}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Plan
    plan = soap.get("plan", {})
    st.markdown('<div class="soap-card soap-p"><h4>P - Plan</h4>', unsafe_allow_html=True)

    treatments = plan.get("treatments", [])
    if treatments:
        st.markdown("**Treatments:**")
        for tx in treatments:
            st.markdown(f"- **{tx.get('action', '')}:** {tx.get('details', '')}")

    rx = plan.get("medications_prescribed", [])
    if rx:
        st.markdown("**Medications Prescribed:**")
        for med in rx:
            st.markdown(f"- **{med.get('name', '')}** {med.get('dose', '')} — "
                       f"{med.get('frequency', '')} for {med.get('duration', 'as directed')}")

    labs = plan.get("labs_ordered", [])
    if labs:
        st.markdown(f"**Labs Ordered:** {', '.join(labs)}")
    refs = plan.get("referrals", [])
    if refs:
        st.markdown(f"**Referrals:** {', '.join(refs)}")
    if plan.get("follow_up"):
        st.markdown(f"**Follow-up:** {plan['follow_up']}")
    edu = plan.get("patient_education", [])
    if edu:
        st.markdown("**Patient Education:**")
        for e in edu:
            st.markdown(f"- {e}")
    st.markdown('</div>', unsafe_allow_html=True)

    # Coding Suggestions
    coding = result.get("coding_suggestions", {})
    if coding:
        st.divider()
        st.subheader("Coding Suggestions")
        cc1, cc2 = st.columns(2)
        with cc1:
            st.markdown("**CPT Codes:**")
            for c in coding.get("cpt_codes", []):
                st.markdown(f'<span class="code-chip">{c.get("code", "")}</span> '
                           f'{c.get("description", "")} — <em>{c.get("rationale", "")}</em>',
                           unsafe_allow_html=True)
        with cc2:
            st.markdown("**ICD-10 Codes:**")
            for c in coding.get("icd10_codes", []):
                st.markdown(f'<span class="code-chip">{c.get("code", "")}</span> '
                           f'{c.get("description", "")} — <em>{c.get("rationale", "")}</em>',
                           unsafe_allow_html=True)
        if coding.get("visit_level"):
            st.info(f"**E&M Level:** {coding['visit_level']} — {coding.get('level_justification', '')}")

    # Quality Flags
    flags = result.get("quality_flags", {})
    if flags:
        st.divider()
        st.subheader("Quality & Safety Flags")
        for item in flags.get("safety_alerts", []):
            st.markdown(f'<div class="flag-danger">{item}</div>', unsafe_allow_html=True)
        for item in flags.get("missing_information", []):
            st.markdown(f'<div class="flag-warn">{item}</div>', unsafe_allow_html=True)
        for item in flags.get("documentation_tips", []):
            st.markdown(f'<div class="flag-info">{item}</div>', unsafe_allow_html=True)

    # Export
    st.divider()
    st.download_button("Download Clinical Note (JSON)", json.dumps(result, indent=2),
                       "clinical_note.json", "application/json")
