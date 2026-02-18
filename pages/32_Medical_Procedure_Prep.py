"""Medical Procedure Prep - Pre-Procedure Patient Guidance - Streamlit Application."""

import os
import json
import streamlit as st
from dotenv import load_dotenv

from engines.prep_engine import prepare_guidance

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #00695c 0%, #00897b 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .prep-card { background: #f8f9fa; border-radius: 10px; padding: 1.2rem; margin-bottom: 0.8rem; }
    .timeline-card { background: #e3f2fd; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
        border-left: 4px solid #1565c0; }
    .anxiety-card { background: #f3e5f5; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
        border-left: 4px solid #7b1fa2; }
    .recovery-card { background: #e8f5e9; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
        border-left: 4px solid #2e7d32; }
    .warn-card { background: #ffebee; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem;
        border-left: 4px solid #c62828; }
    .check-item { padding: 0.3rem 0; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.warning("**Important:** This tool provides general educational guidance only. "
               "Always follow the specific instructions given by your doctor and care team.")

st.markdown("""<div class="hero"><h1>Preppy - Procedure Prep Assistant</h1>
<p>AI-powered pre-procedure guidance to help you prepare with confidence and reduce anxiety</p></div>""",
unsafe_allow_html=True)

with st.form("prep_form"):
    c1, c2 = st.columns(2)
    with c1:
        procedure = st.selectbox("Procedure",
            ["Colonoscopy", "Upper Endoscopy (EGD)", "Cataract Surgery",
             "Knee Arthroscopy", "MRI Scan", "CT Scan with Contrast",
             "Wisdom Teeth Extraction", "Cardiac Catheterization",
             "Laparoscopic Cholecystectomy (Gallbladder)", "Other"],
            index=0)
        age = st.text_input("Patient Age", value="55")
        date = st.text_input("Date Scheduled", value="February 20, 2025")
    with c2:
        facility = st.text_input("Doctor / Facility",
            value="Dr. Sarah Chen, GI Associates, Memorial Hospital")
        first_time = st.selectbox("First Time Having This Procedure?", ["Yes", "No"])
        conditions = st.text_input("Medical Conditions",
            value="Type 2 diabetes (controlled), mild hypertension")
    medications = st.text_area("Current Medications",
        value="Metformin 500mg twice daily\nLisinopril 10mg daily\nBaby aspirin 81mg daily\n"
              "Multivitamin daily", height=100)
    m1, m2 = st.columns(2)
    with m1:
        allergies = st.text_input("Allergies", value="Penicillin (rash), latex (mild)")
    with m2:
        concerns = st.text_area("Specific Concerns",
            value="Nervous about the sedation and prep drink. Worried about discomfort. "
                  "Need to know if I can take my diabetes medication the morning of.", height=100)

    submitted = st.form_submit_button("Get Preparation Guide", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        procedure=procedure, age=age, date=date, facility=facility,
        conditions=conditions, medications=medications, allergies=allergies,
        first_time=first_time, concerns=concerns,
    )

    with st.spinner("Preparing your personalised guide..."):
        try:
            result = prepare_guidance(config, api_key)
        except Exception as e:
            st.error(f"Preparation failed: {e}")
            st.stop()

    # Procedure Overview
    overview = result.get("procedure_overview", {})
    st.subheader(f"Your Procedure: {overview.get('procedure_name', procedure)}")
    oc1, oc2, oc3, oc4 = st.columns(4)
    oc1.metric("Duration", overview.get("duration", "N/A"))
    oc2.metric("Anesthesia", overview.get("anesthesia_type", "N/A"))
    oc3.metric("Setting", overview.get("setting", "N/A"))
    oc4.metric("Purpose", overview.get("common_name", ""))

    st.markdown(f'<div class="prep-card">{overview.get("what_to_expect", "")}</div>',
                unsafe_allow_html=True)
    st.caption(overview.get("purpose", ""))

    # Preparation Timeline
    timeline = result.get("preparation_timeline", [])
    if timeline:
        st.divider()
        st.subheader("Preparation Timeline")
        for t in timeline:
            st.markdown(f'<div class="timeline-card"><strong>{t.get("timeframe", "")}</strong></div>',
                       unsafe_allow_html=True)
            for task in t.get("tasks", []):
                st.markdown(f"  - {task}")
            if t.get("important_notes"):
                st.caption(f"Note: {t['important_notes']}")

    # Dietary & Medication side by side
    dc1, dc2 = st.columns(2)

    diet = result.get("dietary_instructions", {})
    if diet:
        with dc1:
            st.divider()
            st.subheader("Dietary Instructions")
            if diet.get("fasting_required"):
                st.error(f"Fasting required — stop eating/drinking: {diet.get('fasting_start', 'see instructions')}")
            st.markdown(f"**Morning of:** {diet.get('day_of_instructions', '')}")
            if diet.get("allowed_before"):
                st.markdown("**Allowed before fasting:**")
                for a in diet["allowed_before"]:
                    st.markdown(f"  - {a}")
            if diet.get("restricted"):
                st.markdown("**Avoid:**")
                for r in diet["restricted"]:
                    st.markdown(f"  - {r}")

    meds = result.get("medication_guidance", {})
    if meds:
        with dc2:
            st.divider()
            st.subheader("Medication Guidance")
            st.markdown(meds.get("general_advice", ""))
            if meds.get("usually_continue"):
                st.markdown("**Usually OK to continue:**")
                for m in meds["usually_continue"]:
                    st.markdown(f"  - {m}")
            if meds.get("usually_stop"):
                st.markdown("**Usually stopped before:**")
                for m in meds["usually_stop"]:
                    st.warning(m)
            if meds.get("important_warning"):
                st.error(meds["important_warning"])

    # What to Bring
    bring = result.get("what_to_bring", [])
    if bring:
        st.divider()
        st.subheader("What to Bring")
        bc1, bc2 = st.columns(2)
        half = len(bring) // 2 + 1
        with bc1:
            for b in bring[:half]:
                st.markdown(f"- {b}")
        with bc2:
            for b in bring[half:]:
                st.markdown(f"- {b}")

    # Anxiety Management
    anxiety = result.get("anxiety_management", {})
    if anxiety:
        st.divider()
        st.subheader("Managing Your Concerns")
        for c in anxiety.get("common_concerns", []):
            st.markdown(f'<div class="anxiety-card"><strong>Concern:</strong> {c.get("concern", "")}<br/>'
                       f'<strong>Reassurance:</strong> {c.get("reassurance", "")}<br/>'
                       f'<em>Tip: {c.get("tip", "")}</em></div>', unsafe_allow_html=True)

        if anxiety.get("relaxation_techniques"):
            st.markdown("**Relaxation Techniques:**")
            for t in anxiety["relaxation_techniques"]:
                st.markdown(f"- {t}")

        if anxiety.get("questions_for_doctor"):
            with st.expander("Good Questions to Ask Your Doctor"):
                for q in anxiety["questions_for_doctor"]:
                    st.markdown(f"- {q}")

    # Recovery
    recovery = result.get("recovery_expectations", {})
    if recovery:
        st.divider()
        st.subheader("Recovery Expectations")
        for label, key in [("Right After", "immediate_after"), ("First 24 Hours", "first_24_hours"),
                           ("First Week", "first_week"), ("Full Recovery", "full_recovery")]:
            if recovery.get(key):
                st.markdown(f'<div class="recovery-card"><strong>{label}:</strong> {recovery[key]}</div>',
                           unsafe_allow_html=True)

        if recovery.get("activity_restrictions"):
            st.markdown("**Activity Restrictions:**")
            for r in recovery["activity_restrictions"]:
                st.markdown(f"- {r}")

        if recovery.get("warning_signs"):
            st.markdown("**Warning Signs — Call Your Doctor If:**")
            for w in recovery["warning_signs"]:
                st.markdown(f'<div class="warn-card">{w}</div>', unsafe_allow_html=True)

    # Logistics
    logistics = result.get("logistics", {})
    if logistics:
        st.divider()
        st.subheader("Logistics")
        lc1, lc2, lc3, lc4 = st.columns(4)
        lc1.metric("Arrive By", logistics.get("arrival_time", "N/A"))
        lc2.metric("Companion", "Yes" if logistics.get("companion_needed") else "No")
        lc3.metric("Driving", logistics.get("driving_restriction", "N/A"))
        lc4.metric("Time Off", logistics.get("time_off_work", "N/A"))
        if logistics.get("follow_up"):
            st.caption(f"Follow-up: {logistics['follow_up']}")

    # Checklist
    checklist = result.get("checklist", [])
    if checklist:
        st.divider()
        st.subheader("Your Preparation Checklist")
        for category in ["Before", "Day-of", "After"]:
            items = [c for c in checklist if c.get("category") == category]
            if items:
                st.markdown(f"**{category}:**")
                for item in items:
                    st.checkbox(item.get("item", ""), key=f"chk_{item.get('item', '')[:30]}")

    # Reassuring Note
    note = result.get("reassuring_note", "")
    if note:
        st.divider()
        st.success(f"**A Note of Encouragement:** {note}")

    st.divider()
    st.download_button("Download Preparation Guide (JSON)", json.dumps(result, indent=2),
                       "procedure_prep.json", "application/json")
