"""CareCompass - AI Patient Assistant - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.care_engine import assess_care

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #00695c 0%, #00897b 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .urgency-emergency { background: #ffcdd2; border: 2px solid #f44336;
        padding: 1rem; border-radius: 10px; text-align: center; }
    .urgency-urgent { background: #ffe0b2; border: 2px solid #ff9800;
        padding: 1rem; border-radius: 10px; }
    .urgency-semi { background: #fff9c4; border: 2px solid #fdd835;
        padding: 1rem; border-radius: 10px; }
    .urgency-routine { background: #c8e6c9; border: 2px solid #4caf50;
        padding: 1rem; border-radius: 10px; }
    .care-card { background: #f8f9fa; border-radius: 10px; padding: 1rem;
        margin-bottom: 0.5rem; }
    .care-recommended { border-left: 4px solid #4caf50; }
    .care-not { border-left: 4px solid #bdbdbd; }
    .cost-card { background: #e0f2f1; border-radius: 8px; padding: 0.8rem;
        margin-bottom: 0.4rem; }
    .checklist-item { background: #f3e5f5; border-radius: 6px; padding: 0.4rem 0.8rem;
        margin: 0.2rem 0; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.error("**Emergency?** Call **911** immediately.")
    st.warning("**Disclaimer:** This tool provides general information only. "
               "It is NOT a substitute for professional medical advice, diagnosis, or treatment.")

st.markdown("""<div class="hero"><h1>CareCompass</h1>
<p>Understand your symptoms, find the right care level, and compare costs transparently</p></div>""",
unsafe_allow_html=True)

with st.form("care_form"):
    st.subheader("Tell Us About Your Symptoms")
    c1, c2 = st.columns(2)
    with c1:
        symptoms = st.text_area("Describe your symptoms",
            value="I've had a persistent headache for 3 days, mostly on the right side. "
                  "It's throbbing and gets worse when I bend over. I also have some nasal "
                  "congestion, mild fever (100.2F), and pressure around my eyes and forehead.",
            height=120)
        duration = st.text_input("How long have you had these symptoms?",
            value="3 days, gradually getting worse")
        severity = st.slider("Pain/Discomfort Severity (1=mild, 10=severe)", 1, 10, 6)
    with c2:
        age = st.number_input("Age", min_value=0, max_value=120, value=35)
        gender = st.selectbox("Gender", ["Male", "Female", "Non-binary", "Prefer not to say"])
        location = st.text_input("Location (city/state)", value="Chicago, IL")
        insurance = st.selectbox("Insurance Status",
            ["Insured (PPO)", "Insured (HMO)", "Insured (High-Deductible/HSA)",
             "Medicare", "Medicaid", "Uninsured"])

    st.divider()
    h1, h2 = st.columns(2)
    with h1:
        history = st.text_input("Relevant Medical History",
            value="Seasonal allergies, occasional migraines")
    with h2:
        medications = st.text_input("Current Medications",
            value="Cetirizine 10mg daily, ibuprofen as needed")
    context = st.text_input("Additional Context",
        value="I work from home. Have been using a humidifier. OTC decongestants aren't helping much.")

    submitted = st.form_submit_button("Assess My Options", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        age=age, gender=gender, location=location, insurance=insurance,
        symptoms=symptoms, duration=duration, severity=severity,
        history=history, medications=medications, context=context,
    )

    with st.spinner("Analyzing your symptoms and care options..."):
        try:
            result = assess_care(config, api_key)
        except Exception as e:
            st.error(f"Assessment failed: {e}")
            st.stop()

    st.warning(result.get("disclaimer", "For informational purposes only."))

    # Urgency Assessment
    sa = result.get("symptom_assessment", {})
    urgency = sa.get("urgency_level", "Routine")
    urg_cls = ("urgency-emergency" if "Emergency" in urgency
               else "urgency-urgent" if "Urgent" in urgency and "Semi" not in urgency
               else "urgency-semi" if "Semi" in urgency
               else "urgency-routine")

    st.markdown(f"""<div class="{urg_cls}">
        <h2>Urgency: {urgency}</h2>
        <p>{sa.get('summary', '')}</p>
    </div>""", unsafe_allow_html=True)

    if sa.get("when_to_seek_emergency"):
        st.error(f"**Seek emergency care if:** {sa['when_to_seek_emergency']}")

    red_flags = sa.get("red_flags", [])
    if red_flags:
        st.markdown("**Red Flags to Watch For:**")
        for rf in red_flags:
            st.markdown(f"- {rf}")

    # Possible Conditions
    conditions = sa.get("possible_conditions", [])
    if conditions:
        st.divider()
        st.subheader("What This Could Be")
        for cond in conditions:
            likelihood = cond.get("likelihood", "Medium")
            color = "#4caf50" if likelihood == "High" else "#ff9800" if likelihood == "Medium" else "#9e9e9e"
            st.markdown(f"- **{cond.get('condition', '')}** "
                       f"<span style='color:{color};'>({likelihood} likelihood)</span> — "
                       f"{cond.get('description', '')}", unsafe_allow_html=True)

    # Care Recommendations
    recs = result.get("care_recommendations", [])
    if recs:
        st.divider()
        st.subheader("Care Options")
        for r in recs:
            cls = "care-recommended" if r.get("recommended") else "care-not"
            icon = "-> " if r.get("recommended") else ""
            rec_label = "RECOMMENDED" if r.get("recommended") else ""
            st.markdown(f"""<div class="care-card {cls}">
                <strong>{icon}{r.get('care_type', '')}</strong>
                {f' <span style="color:#4caf50; font-weight:bold;">[{rec_label}]</span>' if rec_label else ''}<br/>
                {r.get('reasoning', '')}<br/>
                <small>Typical Wait: {r.get('typical_wait', 'N/A')} | Best for: {r.get('best_for', '')}</small>
            </div>""", unsafe_allow_html=True)

    # Cost Comparison
    costs = result.get("cost_comparison", [])
    if costs:
        st.divider()
        st.subheader("Cost Comparison")

        cost_df = pd.DataFrame([{
            "Care Type": c.get("care_type", ""),
            "Uninsured Est.": c.get("estimated_cost_uninsured", "N/A"),
            "Insured Est.": c.get("estimated_cost_insured", "N/A"),
            "Typical Copay": c.get("typical_copay", "N/A"),
        } for c in costs])
        st.dataframe(cost_df, use_container_width=True, hide_index=True)

        for c in costs:
            if c.get("cost_saving_tips"):
                st.caption(f"**{c.get('care_type', '')} tip:** {c['cost_saving_tips']}")

    # Self-Care + Preparation side by side
    sc_col, prep_col = st.columns(2)

    selfcare = result.get("self_care_guidance", {})
    if selfcare and selfcare.get("applicable"):
        with sc_col:
            st.divider()
            st.subheader("Self-Care Options")
            for m in selfcare.get("measures", []):
                st.markdown(f"- {m}")
            if selfcare.get("otc_options"):
                st.markdown("**OTC Options:**")
                for o in selfcare["otc_options"]:
                    st.markdown(f"- {o}")
            if selfcare.get("when_to_escalate"):
                st.warning(f"**Escalate if:** {selfcare['when_to_escalate']}")

    checklist = result.get("preparation_checklist", [])
    questions = result.get("questions_for_doctor", [])
    with prep_col:
        st.divider()
        st.subheader("Prepare for Your Visit")
        if checklist:
            st.markdown("**Bring/Do:**")
            for item in checklist:
                st.markdown(f'<div class="checklist-item">{item}</div>', unsafe_allow_html=True)
        if questions:
            st.markdown("**Questions to Ask:**")
            for q in questions:
                st.markdown(f"- {q}")

    # Insurance Tips
    ins = result.get("insurance_tips", {})
    if ins:
        st.divider()
        st.subheader("Insurance & Cost Tips")
        ic1, ic2 = st.columns(2)
        with ic1:
            st.markdown(f"**Coverage:** {ins.get('coverage_considerations', '')}")
            st.markdown(f"**Pre-auth:** {ins.get('pre_authorization', '')}")
            st.markdown(f"**In-Network:** {ins.get('in_network_importance', '')}")
        with ic2:
            for fa in ins.get("financial_assistance", []):
                st.info(fa)

    # Follow-up
    fu = result.get("follow_up", {})
    if fu:
        st.divider()
        st.subheader("What to Expect")
        st.markdown(f"**Timeline:** {fu.get('expected_timeline', '')}")
        st.markdown(f"**Follow-up:** {fu.get('follow_up_needed', '')}")
        for sign in fu.get("monitoring_signs", []):
            st.markdown(f"- Watch for: {sign}")

    # Export
    st.divider()
    st.download_button("Download Assessment (JSON)", json.dumps(result, indent=2),
                       "care_assessment.json", "application/json")
