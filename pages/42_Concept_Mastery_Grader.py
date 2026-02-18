"""Concept Mastery Grader - Process-Based Evaluation - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.grader_engine import grade_submission

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #4a148c 0%, #7b1fa2 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .grade-card { border-radius: 10px; padding: 1.5rem; text-align: center; margin-bottom: 1rem; }
    .grade-a { background: #e8f5e9; border: 2px solid #4caf50; }
    .grade-b { background: #e8f5e9; border: 2px solid #8bc34a; }
    .grade-c { background: #fff3e0; border: 2px solid #ff9800; }
    .grade-d { background: #ffebee; border: 2px solid #f44336; }
    .grade-f { background: #ffebee; border: 2px solid #b71c1c; }
    .feedback-strength { background: #e8f5e9; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem;
        border-left: 4px solid #2e7d32; }
    .feedback-weakness { background: #fff3e0; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem;
        border-left: 4px solid #e65100; }
    .feedback-misconception { background: #ffebee; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem;
        border-left: 4px solid #c62828; }
    .feedback-clarify { background: #e3f2fd; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem;
        border-left: 4px solid #1565c0; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**Concept Mastery Grader** evaluates student work based on genuine conceptual "
            "understanding, not just final answers. Designed for the AI era.")

st.markdown("""<div class="hero"><h1>Concept Mastery Grader</h1>
<p>Evaluate genuine understanding, not just correct answers — AI-era assessment for educators</p></div>""",
unsafe_allow_html=True)

with st.form("grader_form"):
    c1, c2 = st.columns(2)
    with c1:
        subject = st.selectbox("Subject",
            ["Computer Science", "Mathematics", "Physics", "Biology", "Chemistry",
             "Economics", "History", "English/Writing", "Business"])
        topic = st.text_input("Topic", value="Recursion and Dynamic Programming")
        grade_level = st.selectbox("Grade Level",
            ["High School", "Undergraduate (Intro)", "Undergraduate (Advanced)",
             "Graduate", "Professional"], index=1)
    with c2:
        rubric_focus = st.selectbox("Grading Focus",
            ["Conceptual Understanding", "Problem-Solving Process",
             "Critical Thinking", "Application & Transfer", "Balanced"])
        strictness = st.selectbox("Strictness",
            ["Lenient", "Standard", "Rigorous"], index=1)
        concepts = st.text_input("Expected Concepts",
            value="Base case identification, recursive decomposition, memoisation, "
                  "time complexity analysis, bottom-up vs top-down approaches")

    prompt_text = st.text_area("Assignment Prompt", height=100,
        value="Explain the relationship between recursion and dynamic programming. "
              "Using the Fibonacci sequence as an example, demonstrate how a naive "
              "recursive solution can be optimised using (a) memoisation and (b) tabulation. "
              "Analyse the time and space complexity of each approach.")

    submission = st.text_area("Student Submission", height=250,
        value="Recursion is when a function calls itself. Dynamic programming is an optimization "
              "technique that stores previously computed results.\n\n"
              "For Fibonacci, the naive recursive approach is:\n"
              "fib(n) = fib(n-1) + fib(n-2), with base cases fib(0)=0, fib(1)=1\n\n"
              "This is slow because it recalculates the same values many times. The time "
              "complexity is O(2^n) because each call branches into two more calls.\n\n"
              "Memoisation fixes this by storing results in a dictionary. When we need fib(k), "
              "we first check if it's already calculated. This brings time complexity to O(n) "
              "because each fib(k) is computed only once. Space is O(n) for the memo table "
              "plus O(n) for the recursion stack.\n\n"
              "Tabulation is the bottom-up approach where we fill an array from fib(0) up to "
              "fib(n). Time is O(n), space is O(n) but we can optimize to O(1) by only keeping "
              "the last two values.\n\n"
              "Both approaches have the same time complexity but tabulation avoids recursion "
              "stack overhead and is generally preferred for large inputs.")

    submitted = st.form_submit_button("Grade Submission", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        subject=subject, topic=topic, prompt=prompt_text, grade_level=grade_level,
        concepts=concepts, submission=submission, rubric_focus=rubric_focus,
        strictness=strictness,
    )

    with st.spinner("Evaluating concept mastery..."):
        try:
            result = grade_submission(config, api_key)
        except Exception as e:
            st.error(f"Grading failed: {e}")
            st.stop()

    # Overall Assessment
    overall = result.get("overall_assessment", {})
    grade = overall.get("grade", "C")
    score = overall.get("score", 50)

    st.subheader("Overall Assessment")
    gc1, gc2, gc3 = st.columns([1, 1, 2])
    with gc1:
        cls = f"grade-{grade.lower()}" if grade in "ABCDF" else "grade-c"
        st.markdown(f'<div class="grade-card {cls}"><span style="font-size:3rem;font-weight:bold">'
                   f'{grade}</span><br/>Grade</div>', unsafe_allow_html=True)
    with gc2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=score,
            gauge={"axis": {"range": [0, 100]},
                   "bar": {"color": "#4caf50" if score >= 80 else "#ff9800" if score >= 60 else "#f44336"}},
        ))
        fig.update_layout(height=200, margin=dict(t=20, b=0, l=20, r=20))
        st.plotly_chart(fig, use_container_width=True)
    with gc3:
        st.metric("Mastery Level", overall.get("mastery_level", ""))
        ai_score = overall.get("ai_likelihood_score", 0)
        ai_color = "#f44336" if ai_score >= 7 else "#ff9800" if ai_score >= 4 else "#4caf50"
        st.markdown(f'AI-Generated Likelihood: <span style="color:{ai_color};font-weight:bold">'
                   f'{ai_score}/10</span>', unsafe_allow_html=True)
    st.info(overall.get("summary", ""))

    # Concept Evaluation
    concepts_eval = result.get("concept_evaluation", [])
    if concepts_eval:
        st.divider()
        st.subheader("Concept-by-Concept Evaluation")

        names = [c.get("concept", "")[:20] for c in concepts_eval]
        scores = [c.get("score", 5) for c in concepts_eval]
        fig_bar = go.Figure(go.Bar(
            x=names, y=scores,
            marker_color=["#4caf50" if s >= 7 else "#ff9800" if s >= 4 else "#f44336" for s in scores],
            text=[f"{s}/10" for s in scores], textposition="outside",
        ))
        fig_bar.update_layout(title="Concept Mastery Scores", height=300, yaxis_range=[0, 10])
        st.plotly_chart(fig_bar, use_container_width=True)

        for c in concepts_eval:
            mastery = c.get("mastery", "Developing")
            icon = "✅" if mastery == "Mastered" else "🔄" if mastery == "Developing" else "❌"
            with st.expander(f"{icon} {c.get('concept', '')} — {mastery} ({c.get('score', 0)}/10)"):
                if c.get("evidence_of_understanding"):
                    st.markdown("**Evidence of Understanding:**")
                    for e in c["evidence_of_understanding"]:
                        st.markdown(f"- {e}")
                if c.get("evidence_of_gaps"):
                    st.markdown("**Gaps:**")
                    for g in c["evidence_of_gaps"]:
                        st.warning(g)
                st.markdown(f"**Feedback:** {c.get('feedback', '')}")

    # Reasoning Analysis
    reasoning = result.get("reasoning_analysis", {})
    if reasoning:
        st.divider()
        st.subheader("Reasoning Analysis")
        dims = ["logical_flow", "depth_of_analysis", "original_thinking", "application_ability"]
        r_scores = []
        for d in dims:
            data = reasoning.get(d, {})
            if isinstance(data, dict):
                r_scores.append(data.get("score", 5))

        if r_scores:
            fig_radar = go.Figure(go.Scatterpolar(
                r=r_scores + [r_scores[0]],
                theta=[d.replace("_", " ").title() for d in dims] + [dims[0].replace("_", " ").title()],
                fill="toself", fillcolor="rgba(123, 31, 162, 0.2)", line_color="#7b1fa2",
            ))
            fig_radar.update_layout(polar=dict(radialaxis=dict(range=[0, 10])), height=300)
            st.plotly_chart(fig_radar, use_container_width=True)

        if reasoning.get("misconceptions_detected"):
            st.markdown("**Misconceptions Detected:**")
            for m in reasoning["misconceptions_detected"]:
                st.error(m)

    # Rubric Scores
    rubric = result.get("rubric_scores", [])
    if rubric:
        st.divider()
        st.subheader("Rubric Breakdown")
        rub_df = pd.DataFrame([{
            "Criterion": r.get("criterion", ""),
            "Points": f"{r.get('points_earned', 0)}/{r.get('max_points', 0)}",
            "Justification": r.get("justification", ""),
        } for r in rubric])
        st.dataframe(rub_df, use_container_width=True, hide_index=True)

    # Inline Feedback
    inline = result.get("inline_feedback", [])
    if inline:
        st.divider()
        st.subheader("Inline Feedback")
        for fb in inline:
            fb_type = fb.get("type", "").lower().replace(" ", "-")
            cls_map = {"strength": "feedback-strength", "weakness": "feedback-weakness",
                       "misconception": "feedback-misconception", "needs-clarification": "feedback-clarify"}
            cls = cls_map.get(fb_type, "feedback-clarify")
            st.markdown(f'<div class="{cls}"><em>"{fb.get("quote", "")}"</em><br/>'
                       f'<strong>[{fb.get("type", "")}]</strong> {fb.get("comment", "")}</div>',
                       unsafe_allow_html=True)

    # Improvement Suggestions
    improvements = result.get("improvement_suggestions", [])
    if improvements:
        st.divider()
        st.subheader("How to Improve")
        for imp in improvements:
            st.markdown(f"**{imp.get('area', '')}:** {imp.get('current_level', '')} → "
                       f"{imp.get('target_level', '')}")
            st.caption(f"Action: {imp.get('specific_action', '')}")

    # Follow-up Questions
    followup = result.get("follow_up_questions", [])
    if followup:
        st.divider()
        st.subheader("Follow-Up Questions to Verify Understanding")
        for q in followup:
            st.markdown(f"- {q}")

    # Instructor Notes
    notes = result.get("instructor_notes", "")
    if notes:
        with st.expander("Instructor Notes (Private)"):
            st.markdown(notes)

    st.divider()
    st.download_button("Download Grade Report (JSON)", json.dumps(result, indent=2),
                       "grade_report.json", "application/json")
