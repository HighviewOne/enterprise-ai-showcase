"""Smart Course Generator (AI Contenta) - Streamlit Application."""

import os
import json
import streamlit as st
from dotenv import load_dotenv

from engines.course_engine import generate_course

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #ff6f00 0%, #ffca28 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .module-card { background: #f8f9fa; border-radius: 10px; padding: 1.2rem;
        border-left: 4px solid #ff6f00; margin-bottom: 0.8rem; }
    .lesson-card { background: #fff8e1; border-radius: 8px; padding: 0.8rem;
        margin: 0.3rem 0; border-left: 3px solid #ffca28; }
    .activity-tag { display: inline-block; background: #e3f2fd; color: #1565c0;
        padding: 0.2rem 0.5rem; border-radius: 20px; margin: 0.1rem; font-size: 0.8rem; }
    .assess-card { background: #fce4ec; border-radius: 8px; padding: 0.8rem;
        border-left: 4px solid #e91e63; margin: 0.3rem 0; }
    .project-card { background: #e8f5e9; border-radius: 10px; padding: 1rem;
        border-left: 4px solid #4caf50; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input

st.markdown("""<div class="hero"><h1>AI Contenta - Smart Course Generator</h1>
<p>Generate complete course curricula with lessons, activities, assessments, and projects in minutes</p></div>""",
unsafe_allow_html=True)

with st.form("course_form"):
    st.subheader("Course Specifications")
    c1, c2 = st.columns(2)
    with c1:
        subject = st.text_input("Course Subject",
            value="Introduction to Machine Learning for Business Professionals")
        level = st.selectbox("Level",
            ["Beginner", "Intermediate", "Advanced", "Mixed Levels"])
        num_modules = st.slider("Number of Modules", 3, 10, 5)
        format_type = st.selectbox("Delivery Format",
            ["Online Self-Paced", "Live Virtual (Zoom)", "In-Person Classroom",
             "Hybrid (Online + In-Person)", "Workshop (Intensive)"])
        domain = st.text_input("Industry/Domain",
            value="Business / Technology / Data-driven Decision Making")
    with c2:
        key_topics = st.text_area("Key Topics to Cover",
            value="ML fundamentals, supervised vs unsupervised learning, common algorithms "
                  "(regression, classification, clustering), model evaluation, practical "
                  "applications in business, tools (Python basics, scikit-learn), "
                  "ethics and bias in ML",
            height=100)
        audience = st.text_input("Audience Background",
            value="Business managers and analysts with no coding experience. "
                  "Comfortable with Excel and basic statistics.")
        learning_style = st.selectbox("Learning Style Focus",
            ["Hands-on / Project-Based", "Lecture + Discussion",
             "Case Study Driven", "Flipped Classroom", "Blended"])
        assessment_pref = st.selectbox("Assessment Preference",
            ["Quizzes + Final Project", "Assignments Only", "Portfolio-Based",
             "Peer Reviews + Presentation", "Certification Exam Style"])
    requirements = st.text_input("Additional Requirements",
        value="Include real-world business case studies. "
              "No heavy math - focus on intuition and application. "
              "Provide ready-to-use templates.")

    submitted = st.form_submit_button("Generate Course", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        subject=subject, level=level, num_modules=num_modules,
        format=format_type, domain=domain, key_topics=key_topics,
        audience=audience, learning_style=learning_style,
        assessment_pref=assessment_pref, requirements=requirements,
    )

    with st.spinner("Generating your course curriculum..."):
        try:
            result = generate_course(config, api_key)
        except Exception as e:
            st.error(f"Generation failed: {e}")
            st.stop()

    # Course Overview
    overview = result.get("course_overview", {})
    st.subheader(overview.get("title", ""))
    st.markdown(f"*{overview.get('subtitle', '')}*")
    st.markdown(overview.get("description", ""))

    ov1, ov2, ov3 = st.columns(3)
    ov1.metric("Duration", overview.get("duration", "N/A"))
    ov2.metric("Difficulty", overview.get("difficulty", "N/A"))
    ov3.metric("Format", overview.get("format", "N/A"))

    st.markdown(f"**Target Audience:** {overview.get('target_audience', '')}")
    if overview.get("prerequisites"):
        st.markdown(f"**Prerequisites:** {', '.join(overview['prerequisites'])}")

    st.markdown("**Learning Outcomes:**")
    for lo in overview.get("learning_outcomes", []):
        st.markdown(f"- {lo}")

    # Modules
    modules = result.get("modules", [])
    if modules:
        st.divider()
        st.subheader(f"Course Modules ({len(modules)})")

        for mod in modules:
            with st.expander(
                f"Module {mod.get('module_number', '')} — {mod.get('title', '')} "
                f"({mod.get('duration', '')})", expanded=False):

                st.markdown(f"**Overview:** {mod.get('overview', '')}")
                st.markdown("**Objectives:**")
                for obj in mod.get("learning_objectives", []):
                    st.markdown(f"- {obj}")

                # Lessons
                lessons = mod.get("lessons", [])
                for lesson in lessons:
                    st.markdown(f"""<div class="lesson-card">
                        <strong>Lesson {lesson.get('lesson_number', '')}: {lesson.get('title', '')}</strong>
                        ({lesson.get('duration', '')})
                    </div>""", unsafe_allow_html=True)

                    st.markdown("**Content:**")
                    for point in lesson.get("content_outline", []):
                        st.markdown(f"- {point}")

                    if lesson.get("instructor_notes"):
                        st.caption(f"Instructor Notes: {lesson['instructor_notes']}")

                    activities = lesson.get("activities", [])
                    if activities:
                        for act in activities:
                            st.markdown(f'<span class="activity-tag">{act.get("type", "")}</span> '
                                       f'{act.get("description", "")} ({act.get("duration", "")})',
                                       unsafe_allow_html=True)

                    if lesson.get("resources"):
                        st.caption(f"Resources: {', '.join(lesson['resources'])}")
                    st.markdown("---")

                # Assessment
                assess = mod.get("assessment", {})
                if assess:
                    st.markdown(f"""<div class="assess-card">
                        <strong>Assessment: {assess.get('title', '')}</strong> ({assess.get('type', '')})<br/>
                        {assess.get('description', '')}
                    </div>""", unsafe_allow_html=True)

                    rubric = assess.get("rubric_criteria", [])
                    if rubric:
                        st.markdown("**Rubric:**")
                        for r in rubric:
                            st.markdown(f"- **{r.get('criterion', '')}** ({r.get('weight', '')}): "
                                       f"{r.get('description', '')}")

                    samples = assess.get("sample_questions", [])
                    if samples:
                        st.markdown("**Sample Questions:**")
                        for sq in samples:
                            st.markdown(f"- [{sq.get('type', '')}] {sq.get('question', '')}")
                            st.caption(f"Answer: {sq.get('answer_key', '')}")

    # Final Project
    fp = result.get("final_project", {})
    if fp:
        st.divider()
        st.subheader("Final Project")
        st.markdown(f"""<div class="project-card">
            <h4>{fp.get('title', '')}</h4>
            <p>{fp.get('description', '')}</p>
            <strong>Requirements:</strong>
            <ul>{''.join(f'<li>{r}</li>' for r in fp.get('requirements', []))}</ul>
            <strong>Evaluation:</strong>
            <ul>{''.join(f'<li>{c}</li>' for c in fp.get('evaluation_criteria', []))}</ul>
            <small>Timeline: {fp.get('suggested_timeline', '')}</small>
        </div>""", unsafe_allow_html=True)

    # Supplementary Materials
    supp = result.get("supplementary_materials", {})
    if supp:
        st.divider()
        st.subheader("Supplementary Materials")
        sp1, sp2 = st.columns(2)
        with sp1:
            st.markdown("**Reading List:**")
            for r in supp.get("reading_list", []):
                st.markdown(f"- {r}")
            st.markdown("**Tools Needed:**")
            for t in supp.get("tools_needed", []):
                st.markdown(f"- {t}")
        with sp2:
            st.markdown("**Templates to Provide:**")
            for t in supp.get("templates", []):
                st.markdown(f"- {t}")
            st.markdown("**Community Resources:**")
            for c in supp.get("community_resources", []):
                st.markdown(f"- {c}")

    st.divider()
    st.download_button("Download Course Curriculum (JSON)", json.dumps(result, indent=2),
                       "course_curriculum.json", "application/json")
