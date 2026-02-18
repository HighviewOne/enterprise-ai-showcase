"""HireQ - AI Mock Interview Coach - Streamlit Application."""

import os
import json
import streamlit as st
from dotenv import load_dotenv

from engines.interviewer import get_interview_response, parse_evaluation, get_display_text

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #6c5ce7 0%, #a29bfe 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .score-big { text-align: center; padding: 1.5rem; border-radius: 12px; color: white;
        background: linear-gradient(135deg, #6c5ce7, #a29bfe); margin-bottom: 1rem; }
    .score-card { background: #f8f9fa; border-radius: 8px; padding: 0.8rem;
        text-align: center; margin-bottom: 0.5rem; }
    .feedback-card { background: #f0f0ff; border-radius: 8px; padding: 1rem;
        margin-bottom: 0.5rem; border-left: 4px solid #6c5ce7; }
    .strength { display: inline-block; background: #d4edda; color: #155724;
        padding: 0.25rem 0.6rem; border-radius: 20px; margin: 0.1rem; font-size: 0.85rem; }
    .improve { display: inline-block; background: #fff3cd; color: #856404;
        padding: 0.25rem 0.6rem; border-radius: 20px; margin: 0.1rem; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input

    st.divider()

    if st.session_state.get("interview_active"):
        st.markdown("### Interview Tips")
        st.markdown("- Use the **STAR method** for behavioral questions")
        st.markdown("- Be specific with examples")
        st.markdown("- Keep answers 1-2 minutes")
        st.markdown("- Say **'end interview'** when you're ready for feedback")
        st.divider()
        if st.button("End Interview & Get Feedback", use_container_width=True):
            st.session_state["messages"].append({"role": "user", "content": "I'd like to end the interview and get my evaluation."})
            st.rerun()
        if st.button("New Interview", use_container_width=True, type="secondary"):
            for key in ["messages", "interview_active", "config", "evaluation"]:
                st.session_state.pop(key, None)
            st.rerun()

    # Past results
    if st.session_state.get("evaluation"):
        ev = st.session_state["evaluation"]
        st.divider()
        st.markdown(f"### Last Score: {ev.get('overall_score', 0)}/100")
        st.markdown(f"**Verdict:** {ev.get('hire_recommendation', 'N/A')}")
        export = json.dumps(ev, indent=2)
        st.download_button("Export Evaluation", export, "interview_evaluation.json", "application/json")

# Header
st.markdown("""<div class="hero"><h1>HireQ</h1>
<p>AI-powered mock interviews with real-time evaluation and coaching</p></div>""",
unsafe_allow_html=True)

# Setup or interview
if not st.session_state.get("interview_active"):
    st.subheader("Configure Your Interview")

    c1, c2 = st.columns(2)
    with c1:
        role = st.text_input("Target Role", value="Senior Software Engineer",
                              placeholder="e.g., Product Manager, Data Scientist")
        level = st.selectbox("Experience Level",
            ["Entry Level / New Grad", "Mid-Level (2-5 years)", "Senior (5-10 years)",
             "Staff / Principal", "Director / VP", "C-Suite"])
    with c2:
        interview_type = st.selectbox("Interview Type",
            ["Mixed (Behavioral + Technical)", "Behavioral Only", "Technical Only",
             "Case Study", "System Design", "Leadership & Management"])
        difficulty = st.selectbox("Starting Difficulty",
            ["Easy (warm-up)", "Medium (standard)", "Hard (challenging)", "Expert (top-tier)"],
            index=1)

    focus_areas = st.text_input("Focus Areas (optional)",
        value="System design, leadership, problem-solving",
        placeholder="e.g., data structures, stakeholder management, conflict resolution")

    if st.button("Start Interview", type="primary", use_container_width=True):
        if not api_key:
            st.error("API key required.")
            st.stop()

        config = dict(
            role=role, level=level, interview_type=interview_type,
            difficulty=difficulty, focus_areas=focus_areas or "general",
        )
        st.session_state["config"] = config
        st.session_state["messages"] = []
        st.session_state["interview_active"] = True
        st.session_state["evaluation"] = None

        # Get opening message
        opening = [{"role": "user", "content": f"Hi, I'm ready for my {interview_type.lower()} interview for the {role} position. Please begin."}]
        response = get_interview_response(opening, config, api_key)
        st.session_state["messages"] = opening + [{"role": "assistant", "content": response}]
        st.rerun()

else:
    # Active interview
    config = st.session_state["config"]
    messages = st.session_state["messages"]

    # Display chat
    for msg in messages:
        if msg["role"] == "user" and msg == messages[0]:
            continue  # Skip the setup message
        avatar = "🎤" if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=avatar):
            display = get_display_text(msg["content"])
            st.markdown(display)

            # Check for evaluation
            ev = parse_evaluation(msg["content"])
            if ev:
                st.session_state["evaluation"] = ev

    # Show evaluation if present
    if st.session_state.get("evaluation"):
        ev = st.session_state["evaluation"]
        st.divider()
        st.header("Interview Evaluation")

        # Overall score
        score = ev.get("overall_score", 0)
        color = "#28a745" if score >= 80 else "#ffc107" if score >= 60 else "#dc3545"
        st.markdown(f"""<div class="score-big" style="background: linear-gradient(135deg, {color}dd, {color}88);">
            <h1 style="margin:0; color:white;">{score}/100</h1>
            <p style="margin:0; color:white;">Recommendation: {ev.get('hire_recommendation', 'N/A')}</p>
        </div>""", unsafe_allow_html=True)

        # Sub-scores
        scores = ev.get("scores", {})
        cols = st.columns(5)
        score_labels = [
            ("Content", scores.get("content_quality", 0)),
            ("Communication", scores.get("communication", 0)),
            ("Technical", scores.get("technical_depth", 0)),
            ("Problem Solving", scores.get("problem_solving", 0)),
            ("Cultural Fit", scores.get("cultural_fit", 0)),
        ]
        for col, (label, val) in zip(cols, score_labels):
            with col:
                sc = "#28a745" if val >= 80 else "#ffc107" if val >= 60 else "#dc3545"
                st.markdown(f"""<div class="score-card">
                    <h3 style="color:{sc}; margin:0;">{val}</h3>
                    <small>{label}</small>
                </div>""", unsafe_allow_html=True)

        # Strengths & improvements
        s_col, i_col = st.columns(2)
        with s_col:
            st.markdown("**Strengths:**")
            tags = "".join(f'<span class="strength">{s}</span>' for s in ev.get("strengths", []))
            st.markdown(tags, unsafe_allow_html=True)
        with i_col:
            st.markdown("**Areas to Improve:**")
            tags = "".join(f'<span class="improve">{a}</span>' for a in ev.get("areas_for_improvement", []))
            st.markdown(tags, unsafe_allow_html=True)

        # Per-question feedback
        qf = ev.get("question_feedback", [])
        if qf:
            st.subheader("Question-by-Question Feedback")
            for i, q in enumerate(qf, 1):
                sc = q.get("score", 0)
                color = "#28a745" if sc >= 80 else "#ffc107" if sc >= 60 else "#dc3545"
                st.markdown(f"""<div class="feedback-card">
                    <strong>Q{i}: {q.get('question_summary', '')}</strong>
                    <span style="float:right; color:{color}; font-weight:bold;">{sc}/100</span><br/>
                    <em>Feedback:</em> {q.get('feedback', '')}<br/>
                    <small><em>Tip:</em> {q.get('ideal_answer_tip', '')}</small>
                </div>""", unsafe_allow_html=True)

        # Next steps
        steps = ev.get("next_steps", [])
        if steps:
            st.subheader("Recommended Next Steps")
            for s in steps:
                st.markdown(f"- {s}")

    # Chat input (only if no evaluation yet)
    if not st.session_state.get("evaluation"):
        if answer := st.chat_input("Type your answer..."):
            if not api_key:
                st.error("API key required.")
                st.stop()

            messages.append({"role": "user", "content": answer})
            with st.chat_message("user"):
                st.markdown(answer)

            with st.chat_message("assistant", avatar="🎤"):
                with st.spinner("..."):
                    response = get_interview_response(messages, config, api_key)
                display = get_display_text(response)
                st.markdown(display)

            messages.append({"role": "assistant", "content": response})

            ev = parse_evaluation(response)
            if ev:
                st.session_state["evaluation"] = ev
                st.rerun()
