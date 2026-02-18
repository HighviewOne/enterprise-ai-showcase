"""AI Gym & Fitness Assistant - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.fitness_engine import analyze_fitness

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #e65100 0%, #ff6d00 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .workout-card { background: #f8f9fa; border-radius: 10px; padding: 1.2rem;
        border-top: 4px solid #ff6d00; margin-bottom: 0.8rem; }
    .score-badge { display: inline-block; padding: 0.3rem 0.8rem; border-radius: 20px;
        color: white; font-weight: bold; font-size: 0.9rem; }
    .muscle-tag { display: inline-block; background: #fff3e0; color: #e65100;
        padding: 0.2rem 0.5rem; border-radius: 20px; margin: 0.1rem; font-size: 0.8rem; }
    .win-tag { display: inline-block; background: #e8f5e9; color: #2e7d32;
        padding: 0.2rem 0.5rem; border-radius: 20px; margin: 0.1rem; font-size: 0.8rem; }
    .improve-tag { display: inline-block; background: #fff8e1; color: #f57f17;
        padding: 0.2rem 0.5rem; border-radius: 20px; margin: 0.1rem; font-size: 0.8rem; }
    .next-card { background: #e8f5e9; border-radius: 10px; padding: 1rem;
        border-left: 4px solid #4caf50; margin-bottom: 0.4rem; }
    .motivation-card { background: #fce4ec; border-radius: 10px; padding: 1.2rem;
        text-align: center; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input

st.markdown("""<div class="hero"><h1>AI Fitness Coach</h1>
<p>Log your workouts and get personalized coaching, progress insights, and smart recommendations</p></div>""",
unsafe_allow_html=True)

SAMPLE_LOG = """Monday - Push Day:
Bench Press: 4x8 @ 185 lbs
Incline Dumbbell Press: 3x10 @ 65 lbs
Overhead Press: 3x8 @ 115 lbs
Cable Flyes: 3x12 @ 30 lbs
Tricep Pushdowns: 3x12 @ 50 lbs
Lateral Raises: 3x15 @ 20 lbs

Wednesday - Pull Day:
Deadlifts: 4x5 @ 315 lbs
Barbell Rows: 4x8 @ 185 lbs
Lat Pulldowns: 3x10 @ 140 lbs
Face Pulls: 3x15 @ 40 lbs
Barbell Curls: 3x10 @ 75 lbs
Hammer Curls: 3x12 @ 30 lbs

Friday - Legs:
Squats: 4x6 @ 275 lbs
Romanian Deadlifts: 3x10 @ 225 lbs
Leg Press: 3x12 @ 400 lbs
Leg Curls: 3x12 @ 90 lbs
Calf Raises: 4x15 @ 200 lbs
Walking Lunges: 3x12 each leg @ 40 lb dumbbells"""

with st.form("fitness_form"):
    st.subheader("Your Profile")
    p1, p2, p3, p4 = st.columns(4)
    with p1:
        name = st.text_input("Name", value="Alex")
        age = st.number_input("Age", min_value=13, max_value=80, value=28)
    with p2:
        gender = st.selectbox("Gender", ["Male", "Female", "Non-binary"])
        height = st.text_input("Height", value="5'10\" / 178 cm")
    with p3:
        weight = st.text_input("Weight", value="180 lbs / 82 kg")
        experience = st.selectbox("Experience Level",
            ["Beginner (0-6 months)", "Novice (6-12 months)",
             "Intermediate (1-3 years)", "Advanced (3+ years)"], index=2)
    with p4:
        goal = st.selectbox("Primary Goal",
            ["Build Muscle / Hypertrophy", "Increase Strength", "Lose Fat",
             "Improve Endurance", "General Fitness", "Athletic Performance"], index=0)
        days_per_week = st.selectbox("Training Days/Week", ["2", "3", "4", "5", "6"], index=2)

    e1, e2 = st.columns(2)
    with e1:
        equipment = st.multiselect("Equipment Access",
            ["Full Gym", "Barbells", "Dumbbells", "Cable Machine", "Machines",
             "Pull-up Bar", "Resistance Bands", "Bodyweight Only"],
            default=["Full Gym", "Barbells", "Dumbbells", "Cable Machine", "Machines"])
    with e2:
        limitations = st.text_input("Injuries / Limitations",
            value="Mild right shoulder impingement, avoid heavy overhead pressing")

    st.divider()
    st.subheader("Workout Log")
    workout_log = st.text_area("Paste your recent workouts (exercises, sets, reps, weight)",
                                value=SAMPLE_LOG, height=250)
    notes = st.text_input("Additional Notes",
                           value="Feeling a bit fatigued this week. Sleep has been ~6 hours/night.")

    submitted = st.form_submit_button("Analyze My Training", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        name=name, age=age, gender=gender, height=height, weight=weight,
        goal=goal, experience=experience, days_per_week=days_per_week,
        equipment=", ".join(equipment), limitations=limitations,
        workout_log=workout_log, notes=notes,
    )

    with st.spinner("Analyzing your training..."):
        try:
            result = analyze_fitness(config, api_key)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    st.markdown(f"**{result.get('athlete_profile_summary', '')}**")

    # Workout Analysis
    workouts = result.get("workout_analysis", [])
    if workouts:
        st.divider()
        st.subheader("Workout Analysis")

        # Effectiveness chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[w.get("session", "") for w in workouts],
            y=[w.get("effectiveness_score", 0) for w in workouts],
            marker_color=["#4caf50" if w.get("effectiveness_score", 0) >= 7
                          else "#ff9800" if w.get("effectiveness_score", 0) >= 5
                          else "#f44336" for w in workouts],
            text=[f"{w.get('effectiveness_score', 0)}/10" for w in workouts],
            textposition="outside",
        ))
        fig.update_layout(title="Workout Effectiveness Scores", height=300,
                          yaxis_range=[0, 10], yaxis_title="Score")
        st.plotly_chart(fig, use_container_width=True)

        for w in workouts:
            score = w.get("effectiveness_score", 0)
            s_color = "#4caf50" if score >= 7 else "#ff9800" if score >= 5 else "#f44336"
            muscles = "".join(f'<span class="muscle-tag">{m}</span>' for m in w.get("muscle_groups_hit", []))
            strengths = "".join(f'<span class="win-tag">{s}</span>' for s in w.get("strengths", []))
            improvements = "".join(f'<span class="improve-tag">{i}</span>' for i in w.get("improvements", []))

            st.markdown(f"""<div class="workout-card">
                <span class="score-badge" style="background:{s_color};">{score}/10</span>
                <strong style="margin-left:0.5rem;">{w.get('session', '')}</strong><br/>
                Volume: {w.get('volume_assessment', 'N/A')} | Intensity: {w.get('intensity_assessment', 'N/A')}<br/>
                <p>Muscles: {muscles}</p>
                <p>Strengths: {strengths}</p>
                <p>Improve: {improvements}</p>
            </div>""", unsafe_allow_html=True)

    # Progress Insights + Split Review
    col_l, col_r = st.columns(2)

    progress = result.get("progress_insights", {})
    if progress:
        with col_l:
            st.divider()
            st.subheader("Progress Insights")
            pi1, pi2 = st.columns(2)
            pi1.metric("Consistency", progress.get("overall_consistency", "N/A"))
            pi2.metric("Training Level", progress.get("estimated_training_age", "N/A"))
            pi3, pi4 = st.columns(2)
            pi3.metric("Strength Trend", progress.get("strength_trend", "N/A"))
            pi4.metric("Volume Trend", progress.get("volume_trend", "N/A"))
            for obs in progress.get("key_observations", []):
                st.markdown(f"- {obs}")
            for plat in progress.get("potential_plateaus", []):
                st.warning(f"Potential plateau: {plat}")

    split = result.get("weekly_split_review", {})
    if split:
        with col_r:
            st.divider()
            st.subheader("Split Review")
            st.metric("Current Split", split.get("current_split_type", "N/A"))
            st.markdown(f"**Balance:** {split.get('balance_assessment', 'N/A')}")
            st.markdown(f"**Recovery:** {split.get('recovery_assessment', 'N/A')}")
            mc = split.get("muscle_coverage", {})
            if mc.get("well_trained"):
                st.success(f"Well-trained: {', '.join(mc['well_trained'])}")
            if mc.get("undertrained"):
                st.warning(f"Undertrained: {', '.join(mc['undertrained'])}")
            if mc.get("overtrained"):
                st.error(f"Overtrained risk: {', '.join(mc['overtrained'])}")

    # Recommendations
    recs = result.get("recommendations", {})
    if recs:
        st.divider()
        st.subheader("Recommendations")
        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown("**Immediate Changes:**")
            for r in recs.get("immediate_changes", []):
                st.markdown(f"- {r}")
            st.markdown("**Program Adjustments:**")
            for r in recs.get("program_adjustments", []):
                st.markdown(f"- {r}")
        with rc2:
            st.markdown("**Nutrition Tips:**")
            for r in recs.get("nutrition_tips", []):
                st.markdown(f"- {r}")
            st.markdown("**Recovery Tips:**")
            for r in recs.get("recovery_tips", []):
                st.markdown(f"- {r}")

        swaps = recs.get("exercise_swaps", [])
        if swaps:
            st.markdown("**Exercise Swaps:**")
            swap_df = pd.DataFrame(swaps)
            st.dataframe(swap_df, use_container_width=True, hide_index=True)

    # Next Workout
    nxt = result.get("next_workout_suggestion", {})
    if nxt:
        st.divider()
        st.subheader(f"Next Workout: {nxt.get('focus', '')}")
        st.markdown(f"**Warm-up:** {nxt.get('warm_up', 'N/A')} | "
                   f"**Est. Duration:** {nxt.get('duration_estimate', 'N/A')}")
        exercises = nxt.get("exercises", [])
        if exercises:
            ex_df = pd.DataFrame(exercises)
            st.dataframe(ex_df, use_container_width=True, hide_index=True)

    # Motivation
    mot = result.get("motivation", {})
    if mot:
        st.divider()
        wins = "".join(f'<span class="win-tag">{w}</span>' for w in mot.get("wins", []))
        st.markdown(f"""<div class="motivation-card">
            <h3>Your Wins This Week</h3>
            <p>{wins}</p>
            <h4 style="margin-top:1rem;">"{mot.get('quote', '')}"</h4>
            <p style="margin-top:0.5rem;"><strong>Weekly Challenge:</strong> {mot.get('weekly_challenge', '')}</p>
        </div>""", unsafe_allow_html=True)

    # Export
    st.divider()
    st.download_button("Download Analysis (JSON)", json.dumps(result, indent=2),
                       "fitness_analysis.json", "application/json")
