"""SmartSchool Reviser - Newsletter to Revision Activities - Streamlit Application."""

import os
import json
import streamlit as st
from dotenv import load_dotenv

from engines.reviser_engine import generate_revision

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #1565c0 0%, #42a5f5 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .activity-card { background: #f8f9fa; border-radius: 10px; padding: 1rem; margin-bottom: 0.6rem; }
    .act-quiz { border-left: 4px solid #7b1fa2; }
    .act-hands { border-left: 4px solid #2e7d32; }
    .act-discuss { border-left: 4px solid #1565c0; }
    .act-read { border-left: 4px solid #e65100; }
    .act-game { border-left: 4px solid #c62828; }
    .act-worksheet { border-left: 4px solid #37474f; }
    .schedule-card { background: #e3f2fd; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem;
        border-left: 4px solid #1565c0; }
    .vocab-card { background: #fff3e0; border-radius: 8px; padding: 0.6rem; margin-bottom: 0.3rem; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**SmartSchool Reviser** turns teacher newsletters into structured revision "
            "activities, quizzes, and study schedules for parents.")

st.markdown("""<div class="hero"><h1>SmartSchool Reviser</h1>
<p>Transform school newsletters into fun, age-appropriate revision activities for your child</p></div>""",
unsafe_allow_html=True)

with st.form("reviser_form"):
    newsletters = st.text_area("Paste Newsletter(s) Here", height=250,
        value="OAKWOOD ELEMENTARY - WEEKLY UPDATE - Grade 4\n"
              "Week of January 20, 2025\n\n"
              "MATH (Mrs. Rodriguez):\n"
              "This week we started our unit on fractions! Students learned about numerators and\n"
              "denominators, equivalent fractions, and comparing fractions using number lines.\n"
              "Next week: adding fractions with like denominators.\n"
              "Homework: Worksheet on equivalent fractions due Friday.\n\n"
              "SCIENCE (Mr. Chen):\n"
              "Our ecosystems unit continues. This week we explored food chains and food webs.\n"
              "Students identified producers, consumers, and decomposers in local ecosystems.\n"
              "Lab activity: built terrarium models to observe mini-ecosystems.\n"
              "Next week: energy flow and trophic levels.\n\n"
              "ENGLISH LANGUAGE ARTS (Ms. Thompson):\n"
              "Reading: We're reading 'Charlotte's Web' as a class. Students completed chapters 8-11.\n"
              "Discussion: character development and themes of friendship.\n"
              "Writing: Persuasive paragraph writing - students are drafting essays about school rules.\n"
              "Vocabulary: 10 new words from Charlotte's Web (see word list).\n"
              "Spelling test on Friday!\n\n"
              "SOCIAL STUDIES (Mrs. Rodriguez):\n"
              "We began studying Native American cultures of the Eastern Woodlands region.\n"
              "Students compared different tribal nations and their adaptations to the environment.")

    c1, c2 = st.columns(2)
    with c1:
        grade = st.selectbox("Child's Grade",
            ["Kindergarten", "1st Grade", "2nd Grade", "3rd Grade", "4th Grade",
             "5th Grade", "6th Grade", "7th Grade", "8th Grade"], index=4)
        strengths = st.text_input("Child's Strengths", value="Reading, science experiments")
    with c2:
        weaknesses = st.text_input("Areas Needing Help", value="Fractions, spelling")
        available_time = st.selectbox("Available Revision Time/Day",
            ["15 minutes", "20 minutes", "30 minutes", "45 minutes", "1 hour"], index=2)
    learning_style = st.selectbox("Learning Style Preference",
        ["Visual (charts, diagrams, videos)", "Hands-on (experiments, building)",
         "Verbal (reading, discussion)", "Mixed/Balanced"], index=3)

    submitted = st.form_submit_button("Generate Revision Plan", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        newsletters=newsletters, grade=grade, strengths=strengths,
        weaknesses=weaknesses, available_time=available_time, learning_style=learning_style,
    )

    with st.spinner("Creating revision activities..."):
        try:
            result = generate_revision(config, api_key)
        except Exception as e:
            st.error(f"Generation failed: {e}")
            st.stop()

    # Summary
    summary = result.get("newsletter_summary", {})
    st.subheader("Newsletter Summary")
    sm1, sm2, sm3 = st.columns(3)
    sm1.metric("Subjects", summary.get("subject_count", 0))
    sm2.metric("Grades", ", ".join(summary.get("grades_covered", [])))
    sm3.metric("Period", summary.get("period", ""))
    if summary.get("key_topics"):
        st.markdown("**Key Topics:** " + ", ".join(summary["key_topics"]))

    # Subjects with activities
    subjects = result.get("subjects", [])
    if subjects:
        st.divider()
        st.subheader("Revision Activities by Subject")
        for subj in subjects:
            with st.expander(f"📖 {subj.get('subject', '')} ({subj.get('grade', '')})"):
                st.markdown(f"**Current Topics:** {', '.join(subj.get('current_topics', []))}")
                if subj.get("upcoming_topics"):
                    st.caption(f"Coming Next: {', '.join(subj['upcoming_topics'])}")

                # Activities
                for act in subj.get("revision_activities", []):
                    act_type = act.get("type", "Activity").lower()
                    cls_map = {"quiz": "act-quiz", "hands-on": "act-hands", "discussion": "act-discuss",
                               "reading": "act-read", "game": "act-game", "worksheet": "act-worksheet"}
                    cls = cls_map.get(act_type, "act-discuss")
                    st.markdown(f'<div class="activity-card {cls}">'
                               f'<strong>[{act.get("type", "")}] {act.get("activity", "")}</strong><br/>'
                               f'Difficulty: {act.get("difficulty", "")} | '
                               f'Time: {act.get("time_needed", "")}</div>', unsafe_allow_html=True)
                    if act.get("parent_instructions"):
                        st.caption(f"Parent Guide: {act['parent_instructions']}")

                # Quiz questions
                quiz = subj.get("quiz_questions", [])
                if quiz:
                    st.markdown("**Practice Quiz:**")
                    for i, q in enumerate(quiz, 1):
                        st.markdown(f"**Q{i}.** {q.get('question', '')}")
                        if q.get("options"):
                            for opt in q["options"]:
                                st.markdown(f"  - {opt}")
                        with st.expander(f"Answer Q{i}"):
                            st.success(f"**Answer:** {q.get('answer', '')}")
                            st.caption(q.get("explanation", ""))

                # Vocabulary
                vocab = subj.get("vocabulary", [])
                if vocab:
                    st.markdown("**Vocabulary:**")
                    for v in vocab:
                        st.markdown(f'<div class="vocab-card"><strong>{v.get("term", "")}</strong>: '
                                   f'{v.get("definition", "")} — <em>{v.get("example", "")}</em></div>',
                                   unsafe_allow_html=True)

                if subj.get("parent_tips"):
                    st.info(f"**Parent Tip:** {subj['parent_tips']}")

    # Weekly Schedule
    schedule = result.get("weekly_schedule", [])
    if schedule:
        st.divider()
        st.subheader("Suggested Weekly Schedule")
        for s in schedule:
            st.markdown(f'<div class="schedule-card"><strong>{s.get("day", "")}</strong>: '
                       f'{s.get("subject", "")} — {s.get("activity", "")} '
                       f'({s.get("duration", "")})</div>', unsafe_allow_html=True)

    # Conversation Starters
    convos = result.get("conversation_starters", [])
    if convos:
        st.divider()
        st.subheader("Conversation Starters")
        st.markdown("Ask your child these questions to reinforce learning:")
        for c in convos:
            st.markdown(f"- {c}")

    # Resources
    resources = result.get("resources", [])
    if resources:
        st.divider()
        st.subheader("Helpful Resources")
        for r in resources:
            st.markdown(f"- **{r.get('resource', '')}** ({r.get('type', '')}) — "
                       f"{r.get('subject', '')}: {r.get('link_or_description', '')}")

    st.divider()
    st.download_button("Download Revision Plan (JSON)", json.dumps(result, indent=2),
                       "revision_plan.json", "application/json")
