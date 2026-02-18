"""AI Compliance Audit Assistant - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.doc_parser import extract_text
from engines.auditor import run_audit

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .score-box { text-align: center; padding: 1.2rem; border-radius: 10px; color: white; }
    .finding-critical { background: #f8d7da; border-left: 5px solid #dc3545;
        border-radius: 8px; padding: 1rem; margin-bottom: 0.6rem; }
    .finding-high { background: #fff3cd; border-left: 5px solid #fd7e14;
        border-radius: 8px; padding: 1rem; margin-bottom: 0.6rem; }
    .finding-medium { background: #d1ecf1; border-left: 5px solid #17a2b8;
        border-radius: 8px; padding: 1rem; margin-bottom: 0.6rem; }
    .finding-low { background: #d4edda; border-left: 5px solid #28a745;
        border-radius: 8px; padding: 1rem; margin-bottom: 0.6rem; }
    .positive { background: #d4edda; border-left: 4px solid #28a745;
        border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.markdown("**Supported Frameworks:**")
    st.markdown("SOX, GDPR, HIPAA, PCI-DSS, OSHA, Employment Law, Internal Policies")

st.markdown("""<div class="hero"><h1>AI Compliance Audit Assistant</h1>
<p>Automated compliance scanning across finance, HR, IT, and operations</p></div>""",
unsafe_allow_html=True)

# ── Input ──
st.subheader("Audit Configuration")
c1, c2 = st.columns(2)
with c1:
    audit_scope = st.multiselect("Audit Scope", [
        "Finance & Expenses", "Data Privacy", "IT Security",
        "HR & Employment", "Operations & Safety", "Vendor Management"],
        default=["Finance & Expenses", "Data Privacy", "IT Security", "HR & Employment"])
    frameworks = st.multiselect("Regulatory Frameworks", [
        "SOX", "GDPR", "HIPAA", "PCI-DSS", "OSHA",
        "Internal Policies", "Employment Law"],
        default=["SOX", "GDPR", "Internal Policies"])
with c2:
    additional_context = st.text_area("Additional Context",
        value="This is a quarterly audit for Q4 2024. Focus on any compliance gaps that could result in regulatory penalties.",
        height=120)

st.divider()
st.subheader("Upload Documents")
pc1, pc2 = st.columns(2)
with pc1:
    st.markdown("**Policy Documents**")
    policy_files = st.file_uploader("Upload policies", type=["pdf", "docx", "txt"],
                                     accept_multiple_files=True, key="policies")
    policy_text_input = st.text_area("Or paste policy text", height=120,
                                      placeholder="Paste policy content...", key="policy_paste")
with pc2:
    st.markdown("**Activity / Transaction Logs**")
    activity_files = st.file_uploader("Upload logs", type=["pdf", "docx", "txt", "csv", "log"],
                                       accept_multiple_files=True, key="logs")
    activity_text_input = st.text_area("Or paste log data", height=120,
                                        placeholder="Paste activity logs...", key="log_paste")

if st.button("Run Compliance Audit", type="primary", use_container_width=True):
    if not api_key:
        st.error("API key required.")
        st.stop()

    # Gather texts
    policy_text = ""
    for f in (policy_files or []):
        try:
            policy_text += f"\n\n=== {f.name} ===\n" + extract_text(f.name, f.read())
        except Exception as e:
            st.error(f"Error reading {f.name}: {e}")
    if policy_text_input.strip():
        policy_text += "\n\n=== Pasted Policy ===\n" + policy_text_input.strip()

    activity_text = ""
    for f in (activity_files or []):
        try:
            activity_text += f"\n\n=== {f.name} ===\n" + extract_text(f.name, f.read())
        except Exception as e:
            st.error(f"Error reading {f.name}: {e}")
    if activity_text_input.strip():
        activity_text += "\n\n=== Pasted Logs ===\n" + activity_text_input.strip()

    if not policy_text and not activity_text:
        st.error("Please upload or paste at least one document.")
        st.stop()

    config = dict(
        audit_scope=", ".join(audit_scope),
        frameworks=", ".join(frameworks),
        policy_text=policy_text or "No policy documents provided.",
        activity_text=activity_text or "No activity logs provided.",
        additional_context=additional_context,
    )

    with st.spinner("Running compliance audit — scanning for violations..."):
        try:
            result = run_audit(config, api_key)
        except Exception as e:
            st.error(f"Audit failed: {e}")
            st.stop()

    st.session_state["audit_result"] = result

    # ── Results ──
    summary = result.get("audit_summary", {})
    findings = result.get("findings", [])

    st.divider()
    st.header("Audit Results")

    # Score
    score = summary.get("compliance_score", 0)
    risk = summary.get("overall_risk_level", "Unknown")
    color_map = {"Critical": "#dc3545", "High": "#fd7e14", "Medium": "#ffc107", "Low": "#28a745"}
    color = color_map.get(risk, "#6c757d")
    st.markdown(f"""<div class="score-box" style="background: linear-gradient(135deg, {color}dd, {color}88);">
        <h1 style="margin:0; color:white;">{score}/100</h1>
        <p style="margin:0; color:white;">Compliance Score — Overall Risk: {risk}</p>
    </div>""", unsafe_allow_html=True)
    st.markdown(f"**Executive Summary:** {summary.get('summary', '')}")

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Findings", summary.get("total_findings", len(findings)))
    m2.metric("Critical", summary.get("critical_findings", 0))
    m3.metric("Areas Audited", len(summary.get("areas_audited", [])))
    m4.metric("Frameworks Checked", len(frameworks))

    # Severity distribution
    sev_counts = {}
    cat_counts = {}
    for f in findings:
        s = f.get("severity", "Unknown")
        sev_counts[s] = sev_counts.get(s, 0) + 1
        c = f.get("category", "Other")
        cat_counts[c] = cat_counts.get(c, 0) + 1

    fig_col1, fig_col2 = st.columns(2)
    with fig_col1:
        if sev_counts:
            sev_colors = {"Critical": "#dc3545", "High": "#fd7e14", "Medium": "#ffc107", "Low": "#28a745"}
            fig = go.Figure(go.Pie(labels=list(sev_counts.keys()), values=list(sev_counts.values()),
                marker=dict(colors=[sev_colors.get(k, "#6c757d") for k in sev_counts.keys()]), hole=0.4))
            fig.update_layout(title="Findings by Severity", height=300)
            st.plotly_chart(fig, use_container_width=True)
    with fig_col2:
        if cat_counts:
            fig2 = go.Figure(go.Bar(x=list(cat_counts.keys()), y=list(cat_counts.values()),
                marker_color="#0f3460"))
            fig2.update_layout(title="Findings by Category", height=300)
            st.plotly_chart(fig2, use_container_width=True)

    # Findings
    st.divider()
    st.subheader(f"Audit Findings ({len(findings)})")
    for f in sorted(findings, key=lambda x: {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}.get(x.get("severity", ""), 4)):
        sev = f.get("severity", "medium").lower()
        st.markdown(f"""<div class="finding-{sev}">
            <strong>{f.get('id', '')} [{f.get('severity', '')}] — {f.get('title', '')}</strong><br/>
            <strong>Category:</strong> {f.get('category', '')} | <strong>Regulation:</strong> {f.get('regulation', '')}<br/>
            <strong>Description:</strong> {f.get('description', '')}<br/>
            <strong>Evidence:</strong> <em>{f.get('evidence', 'N/A')}</em><br/>
            <strong>Impact:</strong> {f.get('impact', '')}<br/>
            <strong>Remediation:</strong> {f.get('remediation', '')}<br/>
            <small><strong>Timeline:</strong> {f.get('timeline', '')} | <strong>Owner:</strong> {f.get('owner', '')}</small>
        </div>""", unsafe_allow_html=True)

    # Positive observations
    positives = result.get("positive_observations", [])
    if positives:
        st.divider()
        st.subheader("Positive Observations")
        for p in positives:
            st.markdown(f'<div class="positive">{p}</div>', unsafe_allow_html=True)

    # Recommendations
    recs = result.get("recommendations", [])
    if recs:
        st.divider()
        st.subheader("Recommendations")
        for r in recs:
            st.markdown(f"- **[{r.get('priority', '')}]** {r.get('recommendation', '')} — *{r.get('expected_benefit', '')}*")

    # Next steps
    steps = result.get("next_steps", [])
    if steps:
        st.divider()
        st.subheader("Next Steps")
        for i, s in enumerate(steps, 1):
            st.markdown(f"**{i}.** {s}")

    # Export
    st.divider()
    col_e1, col_e2 = st.columns(2)
    with col_e1:
        st.download_button("Download Full Report (JSON)", json.dumps(result, indent=2),
                           "compliance_audit_report.json", "application/json")
    with col_e2:
        if findings:
            df = pd.DataFrame([{
                "ID": f.get("id"), "Severity": f.get("severity"), "Title": f.get("title"),
                "Category": f.get("category"), "Regulation": f.get("regulation"),
                "Remediation": f.get("remediation"), "Timeline": f.get("timeline"),
                "Owner": f.get("owner"),
            } for f in findings])
            st.download_button("Download Findings (CSV)", df.to_csv(index=False),
                               "audit_findings.csv", "text/csv")
