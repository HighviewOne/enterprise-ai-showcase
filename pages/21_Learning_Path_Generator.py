"""Personalized Learning Path Generator - Streamlit Application."""

import os
import json
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.learning_engine import generate_learning_path

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #0277bd 0%, #039be5 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .module-card { background: #f8f9fa; border-radius: 10px; padding: 1.2rem;
        border-left: 4px solid #0277bd; margin-bottom: 0.8rem; }
    .topic-item { background: #e1f5fe; border-radius: 6px; padding: 0.5rem;
        margin: 0.2rem 0; }
    .resource-tag { display: inline-block; background: #e8eaf6; color: #283593;
        padding: 0.2rem 0.5rem; border-radius: 20px; margin: 0.1rem; font-size: 0.8rem; }
    .milestone-box { background: #e8f5e9; border-radius: 8px; padding: 0.8rem;
        border-left: 4px solid #4caf50; margin: 0.3rem 0; }
    .quiz-card { background: #f3e5f5; border-radius: 8px; padding: 1rem;
        border-left: 4px solid #7b1fa2; margin-bottom: 0.5rem; }
    .week-card { background: #fff8e1; border-radius: 6px; padding: 0.6rem;
        border-left: 3px solid #f9a825; margin: 0.2rem 0; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input

st.markdown("""<div class="hero"><h1>QuestLoom - Learning Path Generator</h1>
<p>AI-powered personalized curriculum with adaptive modules, resources, and practice assessments</p></div>""",
unsafe_allow_html=True)

with st.form("learn_form"):
    st.subheader("Your Learning Profile")
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Your Name", value="Jordan")
        current_role = st.text_input("Current Role", value="Marketing Manager")
        subject = st.selectbox("Subject Area",
            ["Data Science & Machine Learning", "Web Development (Full-Stack)",
             "Cloud Computing & DevOps", "Cybersecurity", "Product Management",
             "UX/UI Design", "Mobile Development", "AI & LLM Engineering",
             "Blockchain & Web3", "Business Analytics", "Other"])
        goal = st.text_area("Learning Goal",
            value="Transition from marketing to a data analyst role. Need to learn Python, "
                  "SQL, data visualization, and basic ML to get hired within 6 months.",
            height=80)
    with c2:
        current_knowledge = st.text_area("Current Knowledge Level",
            value="Comfortable with Excel and basic statistics. Used Google Analytics and "
                  "Tableau at a surface level. No programming experience. Strong business "
                  "acumen and communication skills.",
            height=80)
        available_time = st.selectbox("Available Study Time",
            ["2-4 hours/week", "5-8 hours/week", "10-15 hours/week",
             "15-20 hours/week", "20+ hours/week"], index=2)
        preference = st.selectbox("Learning Preference",
            ["Video courses + hands-on projects", "Reading + exercises",
             "Interactive/project-based", "Structured bootcamp style",
             "Self-paced exploration"])
        deadline = st.text_input("Timeline / Deadline", value="6 months (by July 2025)")
        budget = st.selectbox("Budget for Resources",
            ["Free resources only", "Up to $50/month", "Up to $200/month",
             "Up to $500 total", "No budget constraint"], index=1)

    context = st.text_input("Additional Context",
        value="Learn best in mornings. Prefer practical, project-based learning over theory.")

    submitted = st.form_submit_button("Generate My Learning Path",
                                       type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        name=name, current_role=current_role, subject=subject, goal=goal,
        current_knowledge=current_knowledge, available_time=available_time,
        preference=preference, deadline=deadline, budget=budget, context=context,
    )

    with st.spinner("Designing your personalized learning path..."):
        try:
            result = generate_learning_path(config, api_key)
        except Exception as e:
            st.error(f"Generation failed: {e}")
            st.stop()

    # Learner Assessment
    assess = result.get("learner_assessment", {})
    st.subheader("Your Assessment")
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("Current Level", assess.get("current_level", "N/A"))
    a2.metric("Readiness Score", f"{assess.get('readiness_score', 0)}/100")
    a3.metric("Learning Style", assess.get("learning_style_suggestion", "N/A"))
    a4.metric("Est. Completion", assess.get("estimated_completion", "N/A"))

    sc1, sc2 = st.columns(2)
    with sc1:
        st.success("**Strengths:** " + ", ".join(assess.get("strengths", [])))
    with sc2:
        st.warning("**Gaps to Fill:** " + ", ".join(assess.get("gaps", [])))

    # Learning Path
    path = result.get("learning_path", {})
    modules = path.get("modules", [])
    if modules:
        st.divider()
        st.subheader(f"{path.get('title', 'Your Learning Path')}")
        st.markdown(f"*{path.get('description', '')}*")
        st.markdown(f"**{path.get('total_modules', 0)} modules** | "
                   f"**~{path.get('total_hours', 0)} hours total**")

        # Progress visualization
        fig = go.Figure(go.Bar(
            x=[f"M{m.get('module_number', '')}" for m in modules],
            y=[m.get("duration_hours", 0) for m in modules],
            text=[m.get("title", "")[:20] for m in modules],
            textposition="outside",
            marker_color=["#0277bd" if m.get("difficulty") == "Beginner"
                          else "#f9a825" if m.get("difficulty") == "Intermediate"
                          else "#e53935" for m in modules],
            hovertext=[m.get("title", "") for m in modules],
        ))
        fig.update_layout(title="Module Duration (hours)", height=300,
                          yaxis_title="Hours")
        st.plotly_chart(fig, use_container_width=True)

        # Module details
        for mod in modules:
            with st.expander(f"Module {mod.get('module_number', '')} — {mod.get('title', '')} "
                           f"({mod.get('duration_hours', 0)}h, {mod.get('difficulty', '')})",
                           expanded=False):
                st.markdown(f"**{mod.get('description', '')}**")

                if mod.get("prerequisites"):
                    st.caption(f"Prerequisites: {', '.join(mod['prerequisites'])}")

                st.markdown("**Learning Objectives:**")
                for obj in mod.get("learning_objectives", []):
                    st.markdown(f"- {obj}")

                topics = mod.get("topics", [])
                if topics:
                    st.markdown("**Topics:**")
                    for t in topics:
                        resources = " ".join(
                            f'<span class="resource-tag">{r.get("type", "")}: {r.get("title", "")}</span>'
                            for r in t.get("resources", []))
                        st.markdown(f"""<div class="topic-item">
                            <strong>{t.get('topic', '')}</strong>
                            [{t.get('type', '')}] — {t.get('estimated_minutes', 0)} min<br/>
                            {resources}
                        </div>""", unsafe_allow_html=True)

                mp = mod.get("milestone_project", {})
                if mp:
                    st.markdown(f"""<div class="milestone-box">
                        <strong>Milestone Project:</strong> {mp.get('title', '')}<br/>
                        {mp.get('description', '')}<br/>
                        <small>Skills: {', '.join(mp.get('skills_applied', []))}</small>
                    </div>""", unsafe_allow_html=True)

                asmt = mod.get("assessment", {})
                if asmt:
                    st.caption(f"Assessment: {asmt.get('type', '')} — {asmt.get('passing_criteria', '')}")

    # Practice Questions
    questions = result.get("practice_questions", [])
    if questions:
        st.divider()
        st.subheader("Practice Questions")
        for i, q in enumerate(questions, 1):
            with st.expander(f"Q{i}: {q.get('topic', '')} [{q.get('difficulty', '')}]"):
                st.markdown(f"**{q.get('question', '')}**")
                choices = q.get("choices", {})
                for k, v in sorted(choices.items()):
                    prefix = "-> " if k == q.get("correct_answer", "") else "   "
                    st.markdown(f"{prefix}**{k}.** {v}")
                st.success(f"**Answer: {q.get('correct_answer', '')}** — {q.get('explanation', '')}")

    # Study Schedule
    sched = result.get("study_schedule", {})
    if sched:
        st.divider()
        st.subheader("Study Schedule")
        st.markdown(f"**Recommended Pace:** {sched.get('recommended_pace', '')}")

        weeks = sched.get("weekly_breakdown", [])
        if weeks:
            for w in weeks:
                st.markdown(f"""<div class="week-card">
                    <strong>Week {w.get('week', '')}</strong> — {w.get('focus', '')}
                    ({w.get('hours', 0)}h) | Deliverable: {w.get('deliverable', '')}
                </div>""", unsafe_allow_html=True)

        tips = sched.get("study_tips", [])
        if tips:
            st.markdown("**Study Tips:**")
            for t in tips:
                st.markdown(f"- {t}")

    # Motivation
    mot = result.get("motivation", {})
    if mot:
        st.divider()
        st.subheader("Stay Motivated")
        st.info(f"**Career Relevance:** {mot.get('career_relevance', '')}")
        st.markdown("**Quick Wins:**")
        for w in mot.get("quick_wins", []):
            st.markdown(f"- {w}")

    # Export
    st.divider()
    st.download_button("Download Learning Path (JSON)", json.dumps(result, indent=2),
                       "learning_path.json", "application/json")
