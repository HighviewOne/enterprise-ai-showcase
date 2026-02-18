"""GMAT Prep Test Coach - Streamlit Application."""

import os
import json
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.coach import generate_questions, evaluate_answers

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #1a237e 0%, #283593 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .q-card { background: #f8f9fa; border-radius: 10px; padding: 1.2rem;
        border-left: 4px solid #1a237e; margin-bottom: 1rem; }
    .correct { background: #e8f5e9; border-left: 4px solid #4caf50; }
    .incorrect { background: #ffebee; border-left: 4px solid #f44336; }
    .diff-easy { color: #4caf50; font-weight: bold; }
    .diff-med { color: #ff9800; font-weight: bold; }
    .diff-hard { color: #f44336; font-weight: bold; }
    .topic-tag { display: inline-block; background: #e8eaf6; color: #1a237e;
        padding: 0.2rem 0.5rem; border-radius: 20px; margin: 0.1rem; font-size: 0.8rem; }
    .strat-card { background: #e8eaf6; border-radius: 8px; padding: 1rem;
        border-left: 4px solid #3f51b5; margin: 0.3rem 0; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input

st.markdown("""<div class="hero"><h1>GMAT Prep Coach</h1>
<p>Adaptive practice questions with AI-powered scoring, explanations, and personalized study plans</p></div>""",
unsafe_allow_html=True)

# Initialize session state
if "questions" not in st.session_state:
    st.session_state.questions = None
if "evaluation" not in st.session_state:
    st.session_state.evaluation = None
if "phase" not in st.session_state:
    st.session_state.phase = "config"

# Phase 1: Configuration
if st.session_state.phase == "config":
    with st.form("config_form"):
        st.subheader("Practice Session Setup")
        c1, c2 = st.columns(2)
        with c1:
            section = st.selectbox("GMAT Section",
                ["Quantitative Reasoning", "Verbal Reasoning", "Data Insights"])
            difficulty = st.selectbox("Difficulty Level",
                ["Easy", "Medium", "Hard", "Mixed"], index=1)
            num_questions = st.slider("Number of Questions", 3, 10, 5)
        with c2:
            target_score = st.selectbox("Target GMAT Score",
                ["600-650", "650-700", "700-730", "730-770", "770-800"], index=2)
            study_stage = st.selectbox("Study Stage",
                ["Just Starting", "Building Foundations", "Practicing Regularly",
                 "Final Review / Test Week"])
            weak_areas = st.text_input("Known Weak Areas",
                value="Data Sufficiency, Probability, Sentence Correction")
        context = st.text_input("Additional Context",
                                 value="Working professional, studying 1-2 hours/day on weeknights.")

        gen_btn = st.form_submit_button("Generate Practice Questions",
                                         type="primary", use_container_width=True)

    if gen_btn:
        if not api_key:
            st.error("API key required.")
            st.stop()
        config = dict(
            section=section, difficulty=difficulty, num_questions=num_questions,
            target_score=target_score, study_stage=study_stage,
            weak_areas=weak_areas, context=context,
        )
        with st.spinner("Generating practice questions..."):
            try:
                result = generate_questions(config, api_key)
                st.session_state.questions = result
                st.session_state.phase = "practice"
                st.rerun()
            except Exception as e:
                st.error(f"Generation failed: {e}")

# Phase 2: Practice
elif st.session_state.phase == "practice":
    result = st.session_state.questions
    info = result.get("session_info", {})
    overview = result.get("section_overview", {})

    st.markdown(f"**Section:** {info.get('section', '')} | "
                f"**Difficulty:** {info.get('difficulty', '')} | "
                f"**Questions:** {info.get('num_questions', 0)} | "
                f"**Est. Time:** {info.get('estimated_time_minutes', 0)} min")

    if overview:
        with st.expander("Section Strategies"):
            st.markdown(f"**What GMAT Tests:** {overview.get('what_gmat_tests', '')}")
            st.markdown(f"**Scoring:** {overview.get('scoring_info', '')}")
            for s in overview.get("key_strategies", []):
                st.markdown(f"- {s}")

    st.divider()
    questions = result.get("questions", [])

    with st.form("answer_form"):
        answers = {}
        for q in questions:
            qid = q.get("id", 0)
            diff = q.get("difficulty", "Medium")
            diff_cls = "diff-easy" if diff == "Easy" else "diff-hard" if diff == "Hard" else "diff-med"

            st.markdown(f"""<div class="q-card">
                <strong>Q{qid}.</strong>
                <span class="{diff_cls}">[{diff}]</span>
                <span class="topic-tag">{q.get('type', '')}</span>
                <span class="topic-tag">{q.get('topic', '')}</span>
                <p style="margin-top:0.5rem; white-space: pre-wrap;">{q.get('stem', '')}</p>
            </div>""", unsafe_allow_html=True)

            choices = q.get("choices", {})
            options = [f"{k}: {v}" for k, v in sorted(choices.items())]
            ans = st.radio(f"Your answer for Q{qid}:", options,
                          key=f"q_{qid}", index=None, horizontal=True)
            answers[qid] = ans

        col1, col2 = st.columns(2)
        with col1:
            submit_btn = st.form_submit_button("Submit Answers & Get Feedback",
                                                type="primary", use_container_width=True)
        with col2:
            new_btn = st.form_submit_button("New Practice Set")

    if new_btn:
        st.session_state.phase = "config"
        st.session_state.questions = None
        st.session_state.evaluation = None
        st.rerun()

    if submit_btn:
        # Check all answered
        unanswered = [qid for qid, ans in answers.items() if ans is None]
        if unanswered:
            st.error(f"Please answer all questions. Missing: Q{', Q'.join(str(q) for q in unanswered)}")
            st.stop()

        # Build QA data for evaluation
        qa_lines = []
        for q in questions:
            qid = q.get("id", 0)
            student_ans = answers[qid][0] if answers[qid] else "?"
            qa_lines.append(f"Q{qid}: {q.get('stem', '')}")
            for k, v in sorted(q.get("choices", {}).items()):
                qa_lines.append(f"  {k}: {v}")
            qa_lines.append(f"Correct Answer: {q.get('correct_answer', '')}")
            qa_lines.append(f"Student Answer: {student_ans}")
            qa_lines.append("")

        qa_data = "\n".join(qa_lines)

        with st.spinner("Evaluating your performance..."):
            try:
                evaluation = evaluate_answers(qa_data, api_key)
                st.session_state.evaluation = evaluation
                st.session_state.phase = "results"
                st.rerun()
            except Exception as e:
                st.error(f"Evaluation failed: {e}")

# Phase 3: Results
elif st.session_state.phase == "results":
    evaluation = st.session_state.evaluation
    questions = st.session_state.questions.get("questions", [])

    # Score Summary
    score = evaluation.get("score_summary", {})
    st.subheader("Score Summary")
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Correct", f"{score.get('correct', 0)} / {score.get('total_questions', 0)}")
    s2.metric("Accuracy", f"{score.get('accuracy_pct', 0)}%")
    s3.metric("Est. Percentile", score.get("estimated_section_score", "N/A"))
    s4.metric("Performance", score.get("performance_level", "N/A"))

    # Accuracy gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score.get("accuracy_pct", 0),
        title={"text": "Accuracy"},
        gauge={
            "axis": {"range": [0, 100]},
            "bar": {"color": "#1a237e"},
            "steps": [
                {"range": [0, 40], "color": "#ffcdd2"},
                {"range": [40, 70], "color": "#fff9c4"},
                {"range": [70, 100], "color": "#c8e6c9"},
            ],
        }
    ))
    fig.update_layout(height=250)
    st.plotly_chart(fig, use_container_width=True)

    # Per-question Review
    st.divider()
    st.subheader("Question-by-Question Review")
    reviews = evaluation.get("per_question_review", [])
    for rev in reviews:
        card_cls = "correct" if rev.get("is_correct") else "incorrect"
        icon = "+" if rev.get("is_correct") else "x"
        st.markdown(f"""<div class="q-card {card_cls}">
            <strong>Q{rev.get('id', '')} [{icon}]</strong>
            Your answer: <strong>{rev.get('student_answer', '')}</strong> |
            Correct: <strong>{rev.get('correct_answer', '')}</strong><br/>
            <em>Concept: {rev.get('concept_tested', '')}</em>
        </div>""", unsafe_allow_html=True)
        with st.expander(f"Q{rev.get('id', '')} - Detailed Explanation"):
            st.markdown(rev.get("explanation", ""))
            if rev.get("improvement_tip"):
                st.info(f"**Tip:** {rev['improvement_tip']}")

    # Strengths / Weaknesses
    st.divider()
    sw1, sw2 = st.columns(2)
    with sw1:
        st.subheader("Strengths")
        for s in evaluation.get("strength_areas", []):
            st.success(s)
    with sw2:
        st.subheader("Areas to Improve")
        for w in evaluation.get("weakness_areas", []):
            st.warning(w)

    # Study Plan
    plan = evaluation.get("study_plan", {})
    if plan:
        st.divider()
        st.subheader("Personalized Study Plan")
        st.markdown(f"**Time Allocation:** {plan.get('time_allocation', '')}")
        pc1, pc2 = st.columns(2)
        with pc1:
            st.markdown("**Immediate Focus:**")
            for f in plan.get("immediate_focus", []):
                st.markdown(f"- {f}")
            st.markdown("**Recommended Practice:**")
            for p in plan.get("recommended_practice", []):
                st.markdown(f"- {p}")
        with pc2:
            st.markdown("**Resources:**")
            for r in plan.get("resources", []):
                st.markdown(f"- {r}")

    # Motivation
    if evaluation.get("motivation"):
        st.divider()
        st.markdown(f"""<div class="strat-card" style="text-align:center;">
            <h4>{evaluation['motivation']}</h4>
        </div>""", unsafe_allow_html=True)

    # Actions
    st.divider()
    ac1, ac2 = st.columns(2)
    with ac1:
        if st.button("Practice Again (Same Settings)", use_container_width=True):
            st.session_state.phase = "practice"
            st.session_state.evaluation = None
            st.rerun()
    with ac2:
        if st.button("New Practice Session", use_container_width=True, type="primary"):
            st.session_state.phase = "config"
            st.session_state.questions = None
            st.session_state.evaluation = None
            st.rerun()

    # Export
    full_result = {
        "questions": st.session_state.questions,
        "evaluation": evaluation,
    }
    st.download_button("Download Results (JSON)", json.dumps(full_result, indent=2),
                       "gmat_practice.json", "application/json")
