"""AI Policy Intelligence System - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.doc_parser import extract_text
from engines.policy_analyzer import analyze_policies

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .conf-critical { background: #f8d7da; border-left: 5px solid #dc3545;
        border-radius: 8px; padding: 1rem; margin-bottom: 0.6rem; }
    .conf-high { background: #fff3cd; border-left: 5px solid #fd7e14;
        border-radius: 8px; padding: 1rem; margin-bottom: 0.6rem; }
    .conf-medium { background: #d1ecf1; border-left: 5px solid #17a2b8;
        border-radius: 8px; padding: 1rem; margin-bottom: 0.6rem; }
    .conf-low { background: #d4edda; border-left: 5px solid #28a745;
        border-radius: 8px; padding: 1rem; margin-bottom: 0.6rem; }
    .gap-card { background: #fff3cd; border-radius: 8px; padding: 0.8rem;
        margin-bottom: 0.4rem; border-left: 4px solid #ffc107; }
    .outdated-card { background: #f0f0f0; border-radius: 8px; padding: 0.8rem;
        margin-bottom: 0.4rem; border-left: 4px solid #6c757d; }
    .score-box { text-align: center; padding: 1.2rem; border-radius: 10px; color: white; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input

st.markdown("""<div class="hero"><h1>AI Policy Intelligence</h1>
<p>Detect conflicts, map to regulations, and surface gaps across your policy documents</p></div>""",
unsafe_allow_html=True)

# Input
st.subheader("Upload Policy Documents")
uploaded = st.file_uploader("Upload policies (multiple allowed)",
    type=["pdf", "docx", "txt"], accept_multiple_files=True)
paste = st.text_area("Or paste policy text", height=150, placeholder="Paste your policies here...")

regulations = st.multiselect("Check Against Regulations",
    ["GDPR", "SOX", "HIPAA", "CCPA", "PCI-DSS", "OSHA", "FERPA", "GLBA", "NIST CSF"],
    default=["GDPR", "SOX", "CCPA"])

if st.button("Analyze Policies", type="primary", use_container_width=True):
    if not api_key:
        st.error("API key required.")
        st.stop()

    policy_text = ""
    for f in (uploaded or []):
        try:
            policy_text += f"\n\n=== {f.name} ===\n" + extract_text(f.name, f.read())
        except Exception as e:
            st.error(f"Error: {e}")
    if paste.strip():
        policy_text += "\n\n" + paste.strip()

    if not policy_text.strip():
        st.error("Upload or paste policy documents.")
        st.stop()

    with st.spinner("Analyzing policies for conflicts, gaps, and regulatory alignment..."):
        try:
            result = analyze_policies(policy_text, ", ".join(regulations), api_key)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    summary = result.get("summary", {})
    conflicts = result.get("conflicts", [])
    reg_map = result.get("regulatory_mapping", [])
    outdated = result.get("outdated_provisions", [])
    inventory = result.get("policy_inventory", [])

    # Score
    st.divider()
    score = summary.get("health_score", 0)
    color = "#28a745" if score >= 80 else "#ffc107" if score >= 60 else "#dc3545"
    st.markdown(f"""<div class="score-box" style="background: linear-gradient(135deg, {color}dd, {color}88);">
        <h1 style="margin:0; color:white;">{score}/100</h1>
        <p style="margin:0; color:white;">Policy Health Score</p>
    </div>""", unsafe_allow_html=True)
    st.markdown(f"**{summary.get('executive_summary', '')}**")

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Policies", summary.get("total_policies", 0))
    m2.metric("Clauses", summary.get("total_clauses", 0))
    m3.metric("Conflicts", summary.get("conflicts_found", len(conflicts)))
    m4.metric("Reg. Gaps", summary.get("regulatory_gaps", 0))
    m5.metric("Outdated", summary.get("outdated_provisions", len(outdated)))

    # Policy inventory
    if inventory:
        st.divider()
        st.subheader("Policy Inventory")
        df_inv = pd.DataFrame(inventory)
        st.dataframe(df_inv, use_container_width=True, hide_index=True)

    # Conflicts
    if conflicts:
        st.divider()
        st.subheader(f"Policy Conflicts ({len(conflicts)})")
        for c in sorted(conflicts, key=lambda x: {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}.get(x.get("severity", ""), 4)):
            sev = c.get("severity", "medium").lower()
            st.markdown(f"""<div class="conf-{sev}">
                <strong>{c.get('id', '')} [{c.get('severity', '')}] — {c.get('type', '')}</strong><br/>
                <strong>Policies:</strong> {', '.join(c.get('policies_involved', []))}<br/>
                <em>Clause A:</em> "{c.get('clause_a', '')}"<br/>
                <em>Clause B:</em> "{c.get('clause_b', '')}"<br/>
                <strong>Issue:</strong> {c.get('description', '')}<br/>
                <strong>Resolution:</strong> {c.get('recommendation', '')}
                <small style="float:right;">Priority: {c.get('priority', '')}</small>
            </div>""", unsafe_allow_html=True)

    # Regulatory mapping
    if reg_map:
        st.divider()
        st.subheader("Regulatory Alignment")
        coverage_counts = {"Full": 0, "Partial": 0, "Missing": 0}
        for r in reg_map:
            cov = r.get("coverage", "Missing")
            coverage_counts[cov] = coverage_counts.get(cov, 0) + 1

        fig = go.Figure(go.Bar(
            x=list(coverage_counts.keys()), y=list(coverage_counts.values()),
            marker_color=["#28a745", "#ffc107", "#dc3545"]))
        fig.update_layout(title="Regulatory Coverage", height=280)
        st.plotly_chart(fig, use_container_width=True)

        df_reg = pd.DataFrame([{
            "Regulation": r.get("regulation", ""),
            "Internal Policy": r.get("relevant_policy", ""),
            "Coverage": r.get("coverage", ""),
            "Gaps": r.get("gaps", ""),
            "Action": r.get("action_needed", ""),
        } for r in reg_map])
        st.dataframe(df_reg, use_container_width=True, hide_index=True)

    # Outdated
    if outdated:
        st.divider()
        st.subheader("Outdated Provisions")
        for o in outdated:
            st.markdown(f"""<div class="outdated-card">
                <strong>{o.get('policy', '')}</strong><br/>
                <em>Current:</em> "{o.get('clause', '')}"<br/>
                <strong>Why outdated:</strong> {o.get('reason', '')}<br/>
                <strong>Suggested update:</strong> {o.get('suggested_update', '')}
            </div>""", unsafe_allow_html=True)

    # Action plan
    actions = result.get("action_plan", [])
    if actions:
        st.divider()
        st.subheader("Action Plan")
        df_act = pd.DataFrame([{
            "Priority": a.get("priority", ""),
            "Action": a.get("action", ""),
            "Owner": a.get("owner", ""),
            "Deadline": a.get("deadline", ""),
        } for a in actions])
        st.dataframe(df_act, use_container_width=True, hide_index=True)

    # Export
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("Download Full Report (JSON)", json.dumps(result, indent=2),
                           "policy_analysis.json", "application/json")
    with c2:
        if conflicts:
            df_conf = pd.DataFrame([{
                "ID": c.get("id"), "Severity": c.get("severity"), "Type": c.get("type"),
                "Policies": ", ".join(c.get("policies_involved", [])),
                "Description": c.get("description"), "Resolution": c.get("recommendation"),
            } for c in conflicts])
            st.download_button("Download Conflicts (CSV)", df_conf.to_csv(index=False),
                               "policy_conflicts.csv", "text/csv")
