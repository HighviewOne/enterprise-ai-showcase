"""AI Resume Matcher - Streamlit Application."""

import os
import streamlit as st
from dotenv import load_dotenv

from engines.resume_parser import extract_text
from engines.analyzer import analyze_resume

load_dotenv()

# --- Page Config ---
    page_title="AI Resume Matcher",
    page_icon="📄",
    layout="wide",
)

# --- Custom CSS ---
st.markdown("""
<style>
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 1rem;
    }
    .score-card h1 {
        font-size: 3rem;
        margin: 0;
        color: white;
    }
    .score-card p {
        margin: 0;
        opacity: 0.9;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        border-left: 4px solid;
    }
    .tag-matched {
        display: inline-block;
        background: #d4edda;
        color: #155724;
        padding: 0.25rem 0.6rem;
        border-radius: 20px;
        margin: 0.15rem;
        font-size: 0.85rem;
    }
    .tag-missing {
        display: inline-block;
        background: #f8d7da;
        color: #721c24;
        padding: 0.25rem 0.6rem;
        border-radius: 20px;
        margin: 0.15rem;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


def get_score_color(score: int) -> str:
    if score >= 80:
        return "#28a745"
    elif score >= 60:
        return "#ffc107"
    elif score >= 40:
        return "#fd7e14"
    return "#dc3545"


def render_results(results: dict):
    """Render the analysis results."""
    overall = results["overall_score"]
    color = get_score_color(overall)

    # Overall Score
    st.markdown(f"""
    <div class="score-card" style="background: linear-gradient(135deg, {color}dd 0%, {color}88 100%);">
        <h1>{overall}/100</h1>
        <p>Overall ATS Compatibility Score</p>
    </div>
    """, unsafe_allow_html=True)

    # Summary
    st.markdown(f"**Assessment:** {results['summary']}")
    st.divider()

    # Sub-scores
    col1, col2, col3, col4 = st.columns(4)
    scores = [
        ("Keyword Match", results["keyword_match_score"], col1),
        ("Skills Alignment", results["skills_alignment_score"], col2),
        ("Experience", results["experience_relevance_score"], col3),
        ("Education", results["education_match_score"], col4),
    ]
    for label, score, col in scores:
        with col:
            sc = get_score_color(score)
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: {sc};">
                <h2 style="color: {sc}; margin: 0;">{score}%</h2>
                <p style="margin: 0; font-size: 0.9rem;">{label}</p>
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # Keywords & Skills
    left, right = st.columns(2)

    with left:
        st.subheader("Keywords")
        if results["matched_keywords"]:
            tags = "".join(f'<span class="tag-matched">{k}</span>' for k in results["matched_keywords"])
            st.markdown(f"**Matched:** {tags}", unsafe_allow_html=True)
        if results["missing_keywords"]:
            tags = "".join(f'<span class="tag-missing">{k}</span>' for k in results["missing_keywords"])
            st.markdown(f"**Missing:** {tags}", unsafe_allow_html=True)

    with right:
        st.subheader("Skills")
        if results["matched_skills"]:
            tags = "".join(f'<span class="tag-matched">{s}</span>' for s in results["matched_skills"])
            st.markdown(f"**Matched:** {tags}", unsafe_allow_html=True)
        if results["missing_skills"]:
            tags = "".join(f'<span class="tag-missing">{s}</span>' for s in results["missing_skills"])
            st.markdown(f"**Missing:** {tags}", unsafe_allow_html=True)

    st.divider()

    # Strengths & Improvements
    left2, right2 = st.columns(2)

    with left2:
        st.subheader("Strengths")
        for s in results.get("strengths", []):
            st.markdown(f"- {s}")

    with right2:
        st.subheader("Improvement Suggestions")
        for i, s in enumerate(results.get("improvement_suggestions", []), 1):
            st.markdown(f"**{i}.** {s}")


# --- Main App ---
st.title("📄 AI Resume Matcher")
st.markdown("Upload your resume and a job description to get an instant ATS compatibility analysis with actionable feedback.")

# API Key
api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input(
        "Anthropic API Key",
        value=api_key,
        type="password",
        help="Enter your Anthropic API key. You can also set it in a .env file.",
    )
    if api_key_input:
        api_key = api_key_input

    st.divider()
    st.markdown("**Supported formats:** PDF, DOCX, TXT")
    st.markdown("**Model:** Claude Sonnet 4.5")

# Input Section
col_resume, col_jd = st.columns(2)

with col_resume:
    st.subheader("Resume")
    resume_file = st.file_uploader(
        "Upload your resume",
        type=["pdf", "docx", "txt"],
        key="resume",
    )
    resume_text_input = st.text_area(
        "Or paste resume text",
        height=200,
        placeholder="Paste your resume content here...",
        key="resume_text",
    )

with col_jd:
    st.subheader("Job Description")
    jd_file = st.file_uploader(
        "Upload job description",
        type=["pdf", "docx", "txt"],
        key="jd",
    )
    jd_text_input = st.text_area(
        "Or paste job description",
        height=200,
        placeholder="Paste the job description here...",
        key="jd_text",
    )

# Analyze Button
if st.button("Analyze Match", type="primary", use_container_width=True):
    # Validate API key
    if not api_key:
        st.error("Please provide an Anthropic API key in the sidebar or .env file.")
        st.stop()

    # Extract resume text
    resume_text = ""
    if resume_file:
        try:
            resume_text = extract_text(resume_file.name, resume_file.read())
        except Exception as e:
            st.error(f"Error reading resume: {e}")
            st.stop()
    elif resume_text_input.strip():
        resume_text = resume_text_input.strip()

    if not resume_text:
        st.error("Please upload a resume file or paste resume text.")
        st.stop()

    # Extract job description text
    jd_text = ""
    if jd_file:
        try:
            jd_text = extract_text(jd_file.name, jd_file.read())
        except Exception as e:
            st.error(f"Error reading job description: {e}")
            st.stop()
    elif jd_text_input.strip():
        jd_text = jd_text_input.strip()

    if not jd_text:
        st.error("Please upload a job description file or paste job description text.")
        st.stop()

    # Run analysis
    with st.spinner("Analyzing resume against job description..."):
        try:
            results = analyze_resume(resume_text, jd_text, api_key)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    st.divider()
    render_results(results)
