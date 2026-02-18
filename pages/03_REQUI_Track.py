"""REQUI Track - Requirements Document Analyzer - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.doc_parser import extract_text
from engines.analyzer import extract_requirements, detect_contradictions, chat_about_requirements

load_dotenv()


st.markdown("""
<style>
    .req-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid #667eea;
    }
    .req-functional { border-left-color: #28a745; }
    .req-non-functional { border-left-color: #17a2b8; }
    .req-constraint { border-left-color: #ffc107; }
    .req-performance { border-left-color: #fd7e14; }
    .req-security { border-left-color: #dc3545; }
    .req-compliance { border-left-color: #6f42c1; }
    .req-interface { border-left-color: #20c997; }
    .conflict-high { background: #f8d7da; border-left: 4px solid #dc3545; }
    .conflict-medium { background: #fff3cd; border-left: 4px solid #ffc107; }
    .conflict-low { background: #d1ecf1; border-left: 4px solid #17a2b8; }
    .score-box {
        text-align: center;
        padding: 1.2rem;
        border-radius: 10px;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


def get_type_css(req_type: str) -> str:
    mapping = {
        "functional": "req-functional",
        "non-functional": "req-non-functional",
        "constraint": "req-constraint",
        "performance": "req-performance",
        "security": "req-security",
        "compliance": "req-compliance",
        "interface": "req-interface",
    }
    return mapping.get(req_type.lower(), "req-card")


def render_extraction_results(data: dict):
    """Render extracted requirements."""
    st.markdown(f"**Document Summary:** {data.get('document_summary', 'N/A')}")

    reqs = data.get("requirements", [])
    breakdown = data.get("type_breakdown", {})

    # Stats row
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Requirements", len(reqs))
    c2.metric("Requirement Types", len(breakdown))
    categories = set(r.get("category", "Unknown") for r in reqs)
    c3.metric("Categories", len(categories))

    # Type breakdown chart
    if breakdown:
        fig = px.pie(
            names=list(breakdown.keys()),
            values=list(breakdown.values()),
            title="Requirements by Type",
            hole=0.4,
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    # Priority breakdown
    priority_counts = {}
    for r in reqs:
        p = r.get("priority", "Not Specified")
        priority_counts[p] = priority_counts.get(p, 0) + 1
    if priority_counts:
        colors = {"Must Have": "#dc3545", "Should Have": "#ffc107",
                  "Nice to Have": "#28a745", "Not Specified": "#6c757d"}
        fig2 = go.Figure(go.Bar(
            x=list(priority_counts.keys()),
            y=list(priority_counts.values()),
            marker_color=[colors.get(k, "#667eea") for k in priority_counts.keys()],
        ))
        fig2.update_layout(title="Requirements by Priority", height=280)
        st.plotly_chart(fig2, use_container_width=True)


def render_traceability_table(reqs: list[dict]):
    """Render a traceability matrix table."""
    rows = []
    for r in reqs:
        rows.append({
            "ID": r.get("id", ""),
            "Title": r.get("title", ""),
            "Description": r.get("description", "")[:120] + ("..." if len(r.get("description", "")) > 120 else ""),
            "Source": r.get("source_ref", ""),
            "Type": r.get("type", ""),
            "Category": r.get("category", ""),
            "Priority": r.get("priority", ""),
            "Related To": ", ".join(r.get("related_to", [])),
        })
    return pd.DataFrame(rows)


def render_contradictions(contradictions_data: dict):
    """Render contradiction analysis results."""
    score = contradictions_data.get("overall_consistency_score", 0)
    color = "#28a745" if score >= 80 else "#ffc107" if score >= 60 else "#dc3545"
    st.markdown(f"""
    <div class="score-box" style="background: linear-gradient(135deg, {color}dd, {color}88);">
        <h1 style="margin:0; color:white;">{score}/100</h1>
        <p style="margin:0; color:white;">Consistency Score</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"**Summary:** {contradictions_data.get('summary', 'N/A')}")

    conflicts = contradictions_data.get("contradictions", [])
    if not conflicts:
        st.success("No contradictions or conflicts detected.")
        return

    st.subheader(f"Issues Found ({len(conflicts)})")
    for c in conflicts:
        sev = c.get("severity", "medium").lower()
        css = f"conflict-{sev}"
        req_ids = ", ".join(c.get("requirement_ids", []))
        st.markdown(f"""
        <div class="req-card {css}">
            <strong>[{c.get('severity', 'N/A')}] {c.get('type', 'Issue')}</strong> — {req_ids}<br/>
            {c.get('description', '')}<br/>
            <em>Recommendation:</em> {c.get('recommendation', 'N/A')}
        </div>
        """, unsafe_allow_html=True)


# ===================== MAIN APP =====================

st.title("📋 REQUI Track")
st.markdown("Upload requirement documents to automatically extract, classify, and analyze requirements. Detect contradictions and chat over your documents.")

# Sidebar
api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.markdown("**Supported formats:** PDF, DOCX, TXT")
    st.markdown("**Model:** Claude Sonnet 4.5")

# File Upload
st.subheader("Upload Documents")
uploaded_files = st.file_uploader(
    "Upload requirement documents (multiple allowed)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
)
text_input = st.text_area(
    "Or paste requirement text directly",
    height=150,
    placeholder="Paste your requirements document here...",
)

# Process documents
if st.button("Analyze Requirements", type="primary", use_container_width=True):
    if not api_key:
        st.error("Please provide an Anthropic API key in the sidebar.")
        st.stop()

    # Gather document text
    all_text = ""
    if uploaded_files:
        for f in uploaded_files:
            try:
                doc_text = extract_text(f.name, f.read())
                all_text += f"\n\n=== Document: {f.name} ===\n\n{doc_text}"
            except Exception as e:
                st.error(f"Error reading {f.name}: {e}")
    if text_input.strip():
        all_text += f"\n\n=== Pasted Text ===\n\n{text_input.strip()}"

    if not all_text.strip():
        st.error("Please upload documents or paste text.")
        st.stop()

    # Store document text in session
    st.session_state["doc_text"] = all_text

    # Step 1: Extract Requirements
    st.divider()
    with st.spinner("Extracting and classifying requirements..."):
        try:
            extraction = extract_requirements(all_text, api_key)
        except Exception as e:
            st.error(f"Extraction failed: {e}")
            st.stop()

    reqs = extraction.get("requirements", [])
    st.session_state["requirements"] = reqs
    st.session_state["extraction"] = extraction

    st.header("Extracted Requirements")
    render_extraction_results(extraction)

    # Traceability Table
    st.subheader("Traceability Matrix")
    df = render_traceability_table(reqs)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Individual requirement cards
    with st.expander(f"View All Requirements ({len(reqs)})", expanded=False):
        for r in reqs:
            css = get_type_css(r.get("type", ""))
            related = ", ".join(r.get("related_to", [])) or "None"
            st.markdown(f"""
            <div class="req-card {css}">
                <strong>{r.get('id', '')} — {r.get('title', '')}</strong><br/>
                {r.get('description', '')}<br/>
                <small>Type: {r.get('type', '')} | Category: {r.get('category', '')} |
                Priority: {r.get('priority', '')} | Source: {r.get('source_ref', '')} |
                Related: {related}</small>
            </div>
            """, unsafe_allow_html=True)

    # Step 2: Contradiction Detection
    st.divider()
    st.header("Contradiction & Conflict Analysis")
    if len(reqs) < 2:
        st.info("Need at least 2 requirements to analyze for contradictions.")
    else:
        with st.spinner("Analyzing for contradictions and conflicts..."):
            try:
                contradictions = detect_contradictions(reqs, api_key)
                st.session_state["contradictions"] = contradictions
                render_contradictions(contradictions)
            except Exception as e:
                st.error(f"Contradiction analysis failed: {e}")

    # Export
    st.divider()
    st.subheader("Export")
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        csv = df.to_csv(index=False)
        st.download_button("Download Traceability (CSV)", csv, "requirements_traceability.csv", "text/csv")
    with col_e2:
        full_json = json.dumps(extraction, indent=2)
        st.download_button("Download Full Analysis (JSON)", full_json, "requirements_analysis.json", "application/json")


# Chat Section (always visible if requirements exist)
if st.session_state.get("requirements"):
    st.divider()
    st.header("Chat with Your Documents")
    st.markdown("Ask questions about the requirements, document content, or analysis results.")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Display chat history
    for msg in st.session_state["chat_history"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if question := st.chat_input("Ask about your requirements..."):
        if not api_key:
            st.error("API key required for chat.")
        else:
            st.session_state["chat_history"].append({"role": "user", "content": question})
            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        answer = chat_about_requirements(
                            question,
                            st.session_state.get("doc_text", ""),
                            st.session_state["requirements"],
                            api_key,
                        )
                        st.markdown(answer)
                        st.session_state["chat_history"].append({"role": "assistant", "content": answer})
                    except Exception as e:
                        st.error(f"Chat failed: {e}")
