"""AI Wellness & Nutrition Platform (NutriNext) - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.wellness_engine import analyze_wellness

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #2e7d32 0%, #66bb6a 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .bio-card { background: #f8f9fa; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem; }
    .bio-optimal { border-left: 4px solid #4caf50; }
    .bio-normal { border-left: 4px solid #8bc34a; }
    .bio-borderline { border-left: 4px solid #ff9800; }
    .bio-alert { border-left: 4px solid #f44336; }
    .supp-card { background: #e8f5e9; border-radius: 8px; padding: 0.8rem;
        border-left: 4px solid #2e7d32; margin-bottom: 0.4rem; }
    .food-card { background: #fff8e1; border-radius: 8px; padding: 0.6rem; margin: 0.2rem 0; }
    .stack-card { background: #f3e5f5; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.warning("**Disclaimer:** This tool is for educational purposes only. "
               "Always consult a healthcare provider before starting supplements or making dietary changes.")

st.markdown("""<div class="hero"><h1>NutriNext - AI Wellness Platform</h1>
<p>Personalized nutrition insights from your biomarkers — deficiency detection, supplement stacks, and dietary plans</p></div>""",
unsafe_allow_html=True)

SAMPLE_LABS = """Complete Blood Count:
- Hemoglobin: 11.8 g/dL (ref: 12.0-16.0)
- Hematocrit: 35.2% (ref: 36-46%)
- MCV: 88 fL (ref: 80-100)
- Ferritin: 15 ng/mL (ref: 20-200)
- Iron: 45 mcg/dL (ref: 60-170)

Metabolic Panel:
- Vitamin D (25-OH): 18 ng/mL (ref: 30-100)
- Vitamin B12: 280 pg/mL (ref: 200-900)
- Folate: 5.2 ng/mL (ref: >3.0)
- Magnesium: 1.7 mg/dL (ref: 1.7-2.2)
- Calcium: 9.4 mg/dL (ref: 8.5-10.5)
- TSH: 3.8 mIU/L (ref: 0.4-4.0)

Lipid Panel:
- Total Cholesterol: 215 mg/dL (ref: <200)
- LDL: 138 mg/dL (ref: <100)
- HDL: 52 mg/dL (ref: >60)
- Triglycerides: 125 mg/dL (ref: <150)

Inflammation:
- hs-CRP: 2.8 mg/L (ref: <1.0 low risk, 1-3 moderate)
- Homocysteine: 12.5 umol/L (ref: 5-15)

Blood Sugar:
- Fasting Glucose: 98 mg/dL (ref: 70-99)
- HbA1c: 5.6% (ref: <5.7)"""

with st.form("wellness_form"):
    st.subheader("Your Profile")
    c1, c2 = st.columns(2)
    with c1:
        age = st.number_input("Age", 18, 100, 38)
        gender = st.selectbox("Gender", ["Female", "Male", "Non-binary"])
        height = st.text_input("Height", value="5'6\" / 168 cm")
        weight = st.text_input("Weight", value="145 lbs / 66 kg")
        activity_level = st.selectbox("Activity Level",
            ["Sedentary", "Lightly Active (1-2x/week)", "Moderately Active (3-4x/week)",
             "Very Active (5+/week)", "Athlete"])
    with c2:
        diet_type = st.selectbox("Diet Type",
            ["Standard American", "Mediterranean", "Vegetarian", "Vegan",
             "Keto/Low-Carb", "Paleo", "Pescatarian", "No specific diet"])
        goals = st.text_input("Health Goals",
            value="Improve energy levels, optimize iron levels, reduce inflammation")
        current_supplements = st.text_input("Current Supplements",
            value="Multivitamin, fish oil 1000mg")
        conditions = st.text_input("Known Conditions",
            value="History of anemia, seasonal allergies")
        symptoms = st.text_input("Current Symptoms",
            value="Fatigue, brain fog, occasional hair loss, cold hands and feet")

    st.divider()
    lab_results = st.text_area("Lab Results (paste values with reference ranges)",
                                value=SAMPLE_LABS, height=250)
    context = st.text_input("Additional Context",
        value="Vegetarian for 5 years. Irregular periods. Want to optimize naturally before medication.")

    submitted = st.form_submit_button("Analyze My Biomarkers", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        age=age, gender=gender, height=height, weight=weight,
        activity_level=activity_level, diet_type=diet_type, goals=goals,
        current_supplements=current_supplements, conditions=conditions,
        symptoms=symptoms, lab_results=lab_results, context=context,
    )

    with st.spinner("Analyzing your biomarkers..."):
        try:
            result = analyze_wellness(config, api_key)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    st.warning(result.get("disclaimer", "For educational purposes only."))

    # Health Overview
    ho = result.get("health_overview", {})
    st.subheader("Health Overview")
    h1, h2 = st.columns([1, 2])
    with h1:
        fig_score = go.Figure(go.Indicator(
            mode="gauge+number", value=ho.get("wellness_score", 0),
            title={"text": "Wellness Score"},
            gauge={"axis": {"range": [0, 100]}, "bar": {"color": "#2e7d32"},
                   "steps": [{"range": [0, 40], "color": "#ffcdd2"},
                             {"range": [40, 70], "color": "#fff9c4"},
                             {"range": [70, 100], "color": "#c8e6c9"}]}))
        fig_score.update_layout(height=250)
        st.plotly_chart(fig_score, use_container_width=True)
    with h2:
        st.metric("Status", ho.get("overall_status", "N/A"))
        st.markdown(ho.get("summary", ""))
        st.markdown("**Top Priorities:** " + " | ".join(ho.get("top_priorities", [])))

    # Biomarker Analysis
    biomarkers = result.get("biomarker_analysis", [])
    if biomarkers:
        st.divider()
        st.subheader("Biomarker Analysis")
        for b in biomarkers:
            status = b.get("status", "Normal")
            cls = ("bio-optimal" if "Optimal" in status else "bio-alert" if "Low" in status or "High" in status
                   else "bio-borderline" if "Borderline" in status else "bio-normal")
            color = ("#4caf50" if "Optimal" in status else "#f44336" if status in ("Low", "High")
                     else "#ff9800" if "Borderline" in status else "#8bc34a")
            st.markdown(f"""<div class="bio-card {cls}">
                <strong>{b.get('biomarker', '')}</strong>:
                <strong style="color:{color};">{b.get('value', '')} ({status})</strong>
                — Ref: {b.get('normal_range', '')}<br/>
                <small>{b.get('significance', '')} | Diet: {b.get('dietary_connection', '')}</small>
            </div>""", unsafe_allow_html=True)

    # Deficiencies
    deficiencies = result.get("deficiencies_detected", [])
    if deficiencies:
        st.divider()
        st.subheader(f"Deficiencies Detected ({len(deficiencies)})")
        for d in deficiencies:
            sev_color = "#f44336" if d.get("severity") == "Severe" else "#ff9800" if d.get("severity") == "Moderate" else "#fdd835"
            supp = d.get("supplement_recommendation", {})
            foods = ", ".join(d.get("food_sources", []))
            st.markdown(f"""<div class="supp-card">
                <strong>{d.get('nutrient', '')}</strong>
                <span style="color:{sev_color}; font-weight:bold;"> [{d.get('severity', '')}]</span><br/>
                <strong>Evidence:</strong> {d.get('evidence', '')}<br/>
                <strong>Impact:</strong> {d.get('health_impact', '')}<br/>
                <strong>Food Sources:</strong> {foods}<br/>
                <strong>Supplement:</strong> {supp.get('product_type', '')} — {supp.get('suggested_dose', '')}
                ({supp.get('form', '')}) | Take: {supp.get('timing', '')} | Duration: {supp.get('duration', '')}
            </div>""", unsafe_allow_html=True)

    # Supplement Stack + Nutrition Plan
    sc, np = st.columns(2)

    stack = result.get("supplement_stack", {})
    if stack:
        with sc:
            st.divider()
            st.subheader("Daily Supplement Stack")
            for period, label in [("morning", "Morning"), ("afternoon", "Afternoon"), ("evening", "Evening")]:
                items = stack.get(period, [])
                if items:
                    st.markdown(f"""<div class="stack-card"><strong>{label}:</strong><br/>""" +
                               "<br/>".join(f"- {s.get('supplement', '')} {s.get('dose', '')} "
                                           f"{'(with food)' if s.get('with_food') else '(empty stomach)'}"
                                           for s in items) + "</div>", unsafe_allow_html=True)
            if stack.get("estimated_monthly_cost"):
                st.caption(f"Est. monthly cost: {stack['estimated_monthly_cost']}")
            if stack.get("priority_order"):
                st.info("**Priority order:** " + " > ".join(stack["priority_order"]))

    nutrition = result.get("nutrition_plan", {})
    if nutrition:
        with np:
            st.divider()
            st.subheader("Nutrition Plan")
            st.markdown(f"**Pattern:** {nutrition.get('dietary_pattern', '')}")
            st.markdown(f"**Hydration:** {nutrition.get('hydration', '')}")
            st.markdown("**Foods to Increase:**")
            for f in nutrition.get("foods_to_increase", []):
                st.markdown(f"""<div class="food-card">
                    <strong>{f.get('food', '')}</strong> — {f.get('benefit', '')}
                    <small>({f.get('serving', '')})</small>
                </div>""", unsafe_allow_html=True)
            st.markdown("**Foods to Limit:**")
            for f in nutrition.get("foods_to_limit", []):
                st.caption(f"Limit: {f.get('food', '')} — {f.get('reason', '')} (try: {f.get('alternative', '')})")

    # Lifestyle Recommendations
    lifestyle = result.get("lifestyle_recommendations", [])
    if lifestyle:
        st.divider()
        st.subheader("Lifestyle Recommendations")
        for lr in lifestyle:
            st.markdown(f"- **[{lr.get('category', '')}]** {lr.get('recommendation', '')} — "
                       f"*{lr.get('rationale', '')}*")

    # Retest Plan
    retest = result.get("retest_plan", {})
    if retest:
        st.divider()
        st.subheader("Retest Plan")
        st.markdown(f"**Retest in:** {retest.get('recommended_retest', '')}")
        st.markdown(f"**Expected improvement:** {retest.get('expected_improvement_timeline', '')}")
        st.markdown(f"**Markers to recheck:** {', '.join(retest.get('markers_to_recheck', []))}")

    st.divider()
    st.download_button("Download Wellness Report (JSON)", json.dumps(result, indent=2),
                       "wellness_report.json", "application/json")
