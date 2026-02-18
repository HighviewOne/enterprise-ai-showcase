"""Conversational Assessment - AI-Era Critical Thinking Evaluation - Streamlit Application."""

import os
import json
import streamlit as st
from dotenv import load_dotenv

from engines.assess_engine import get_assessment_response, get_final_assessment

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #4a148c 0%, #6a1b9a 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .score-card { background: #f8f9fa; border-radius: 10px; padding: 1rem; margin-bottom: 0.5rem;
        border-left: 4px solid #6a1b9a; }
    .grade-a { color: #4caf50; font-size: 2rem; font-weight: bold; }
    .grade-b { color: #8bc34a; font-size: 2rem; font-weight: bold; }
    .grade-c { color: #ff9800; font-size: 2rem; font-weight: bold; }
    .grade-d { color: #f44336; font-size: 2rem; font-weight: bold; }
    .grade-f { color: #b71c1c; font-size: 2rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()

    st.subheader("Assessment Setup")
    subject = st.selectbox("Subject",
        ["Computer Science", "Mathematics", "Physics", "Biology", "Economics",
         "History", "Literature", "Business/Management", "Psychology", "Other"])
    topic = st.text_input("Specific Topic",
        value="Object-Oriented Programming — Inheritance vs Composition")
    st.divider()
    st.info("**MasterEd** assesses critical thinking through Socratic dialogue. "
            "It probes for genuine understanding, not just correct answers.")

st.markdown("""<div class="hero"><h1>MasterEd - Conversational Assessment</h1>
<p>AI-powered Socratic assessment — evaluating how you think, not just what you answer</p></div>""",
unsafe_allow_html=True)

# Session state
if "assess_messages" not in st.session_state:
    st.session_state.assess_messages = []
if "assess_history" not in st.session_state:
    st.session_state.assess_history = []
if "running_scores" not in st.session_state:
    st.session_state.running_scores = []
if "final_report" not in st.session_state:
    st.session_state.final_report = None

# Display conversation
for msg in st.session_state.assess_history:
    with st.chat_message(msg["role"], avatar="🎓" if msg["role"] == "assistant" else "🧑‍🎓"):
        st.markdown(msg["content"])

# Running scores in sidebar
if st.session_state.running_scores:
    with st.sidebar:
        st.divider()
        st.subheader("Running Assessment")
        latest = st.session_state.running_scores[-1]
        for dim, score in latest.items():
            bar_color = "#4caf50" if score >= 7 else "#f44336" if score <= 3 else "#ff9800"
            st.markdown(f"**{dim.replace('_', ' ').title()}:** {score}/10")
            st.progress(score / 10)

# Chat input
col1, col2 = st.columns([5, 1])
if prompt := st.chat_input("Type your response..."):
    if not api_key:
        st.error("API key required.")
        st.stop()

    # Show user message
    st.session_state.assess_history.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(prompt)

    # Build messages for API
    st.session_state.assess_messages.append({"role": "user", "content": prompt})

    with st.spinner("Thinking..."):
        try:
            result = get_assessment_response(
                st.session_state.assess_messages, subject, topic, api_key)
        except Exception as e:
            st.error(f"Assessment failed: {e}")
            st.stop()

    response_text = result.get("response_to_student", "")
    scores = result.get("running_score", {})
    notes = result.get("assessment_notes", {})

    # Store assistant response
    st.session_state.assess_messages.append({"role": "assistant", "content": json.dumps(result)})
    st.session_state.assess_history.append({"role": "assistant", "content": response_text})
    if scores:
        st.session_state.running_scores.append(scores)

    with st.chat_message("assistant", avatar="🎓"):
        st.markdown(response_text)

    st.rerun()

# Start / Finish buttons
bc1, bc2, bc3 = st.columns(3)
with bc1:
    if st.button("Start Assessment", type="primary", use_container_width=True):
        if not api_key:
            st.error("API key required.")
        else:
            start_msg = f"I'd like to be assessed on {topic} in {subject}. Please begin."
            st.session_state.assess_messages = [{"role": "user", "content": start_msg}]
            st.session_state.assess_history = [{"role": "user", "content": start_msg}]
            st.session_state.running_scores = []
            st.session_state.final_report = None

            with st.spinner("Preparing assessment..."):
                try:
                    result = get_assessment_response(
                        st.session_state.assess_messages, subject, topic, api_key)
                except Exception as e:
                    st.error(f"Failed: {e}")
                    st.stop()

            response_text = result.get("response_to_student", "")
            st.session_state.assess_messages.append({"role": "assistant", "content": json.dumps(result)})
            st.session_state.assess_history.append({"role": "assistant", "content": response_text})
            scores = result.get("running_score", {})
            if scores:
                st.session_state.running_scores.append(scores)
            st.rerun()

with bc2:
    if st.button("Finish & Get Report", use_container_width=True):
        if not api_key:
            st.error("API key required.")
        elif len(st.session_state.assess_messages) < 2:
            st.warning("Have a conversation first before generating a report.")
        else:
            with st.spinner("Generating final assessment..."):
                try:
                    report = get_final_assessment(
                        st.session_state.assess_messages, subject, topic, api_key)
                    st.session_state.final_report = report
                except Exception as e:
                    st.error(f"Report failed: {e}")
            st.rerun()

with bc3:
    if st.button("Reset", use_container_width=True):
        st.session_state.assess_messages = []
        st.session_state.assess_history = []
        st.session_state.running_scores = []
        st.session_state.final_report = None
        st.rerun()

# Final Report
if st.session_state.final_report:
    st.divider()
    st.subheader("Final Assessment Report")
    fa = st.session_state.final_report.get("final_assessment", {})

    rc1, rc2, rc3 = st.columns(3)
    grade = fa.get("overall_grade", "C")
    grade_cls = f"grade-{grade.lower()}" if grade in "ABCDF" else "grade-c"
    with rc1:
        st.markdown(f'<span class="{grade_cls}">Grade: {grade}</span>', unsafe_allow_html=True)
    with rc2:
        st.metric("Score", f"{fa.get('overall_score', 0)}/100")
    with rc3:
        st.metric("Level", fa.get("understanding_level", ""))

    st.info(fa.get("summary", ""))

    fc1, fc2 = st.columns(2)
    with fc1:
        st.markdown("**Strengths:**")
        for s in fa.get("strengths", []):
            st.markdown(f"- {s}")
    with fc2:
        st.markdown("**Areas for Growth:**")
        for a in fa.get("areas_for_growth", []):
            st.markdown(f"- {a}")

    # Concept Mastery
    concepts = fa.get("concept_mastery", [])
    if concepts:
        st.markdown("**Concept Mastery:**")
        for c in concepts:
            mastery = c.get("mastery", "Developing")
            icon = "✅" if mastery == "Mastered" else "🔄" if mastery == "Developing" else "❌"
            st.markdown(f"{icon} **{c.get('concept', '')}** — {mastery}")
            st.caption(c.get("evidence", ""))

    # Thinking Patterns
    patterns = fa.get("thinking_patterns", {})
    if patterns:
        st.markdown("**Thinking Pattern Scores:**")
        for dim, data in patterns.items():
            if isinstance(data, dict):
                score = data.get("score", 5)
                st.markdown(f'<div class="score-card"><strong>{dim.replace("_", " ").title()}</strong>: '
                           f'{score}/10 — {data.get("evidence", "")}</div>', unsafe_allow_html=True)

    # Recommendations
    recs = fa.get("recommendations", [])
    if recs:
        st.markdown("**Recommendations:**")
        for r in recs:
            st.markdown(f"- {r}")

    if fa.get("educator_notes"):
        with st.expander("Educator Notes"):
            st.markdown(fa["educator_notes"])

    st.download_button("Download Assessment Report (JSON)",
                       json.dumps(st.session_state.final_report, indent=2),
                       "assessment_report.json", "application/json")
