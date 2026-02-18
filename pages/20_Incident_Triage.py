"""AI Incident Triage Assistant - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.triage_engine import triage_incident

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #b71c1c 0%, #e53935 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .sev1 { background: #ffcdd2; border-left: 4px solid #b71c1c; padding: 0.8rem; border-radius: 6px; }
    .sev2 { background: #ffe0b2; border-left: 4px solid #e65100; padding: 0.8rem; border-radius: 6px; }
    .sev3 { background: #fff9c4; border-left: 4px solid #f9a825; padding: 0.8rem; border-radius: 6px; }
    .sev4 { background: #c8e6c9; border-left: 4px solid #2e7d32; padding: 0.8rem; border-radius: 6px; }
    .action-card { background: #f8f9fa; border-radius: 8px; padding: 0.8rem;
        border-left: 4px solid #1565c0; margin-bottom: 0.4rem; }
    .timeline-card { background: #fafafa; border-left: 2px solid #9e9e9e;
        padding: 0.5rem 0.5rem 0.5rem 1rem; margin-left: 1rem; margin-bottom: 0.3rem; }
    .group-card { background: #e3f2fd; border-radius: 8px; padding: 0.8rem;
        margin-bottom: 0.5rem; }
    .comms-card { background: #f3e5f5; border-radius: 8px; padding: 1rem;
        border-left: 4px solid #7b1fa2; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input

st.markdown("""<div class="hero"><h1>AI Incident Triage Assistant</h1>
<p>Correlate alerts, identify root causes, and get actionable remediation steps in seconds</p></div>""",
unsafe_allow_html=True)

sample_alerts = ""
try:
    with open("examples/sample_alerts.txt") as f:
        sample_alerts = f.read()
except FileNotFoundError:
    pass

with st.form("triage_form"):
    alerts = st.text_area("Alerts, Logs & Error Traces",
                           value=sample_alerts, height=250,
                           placeholder="Paste alerts from Datadog, PagerDuty, CloudWatch, Sentry, etc.")

    c1, c2 = st.columns(2)
    with c1:
        environment = st.selectbox("Environment",
            ["Production", "Staging", "Development", "DR / Failover"])
        architecture = st.text_input("Architecture Overview",
            value="Microservices on AWS EKS. PostgreSQL RDS primary + 2 read replicas. "
                  "Redis cache cluster. ALB load balancer. Services: payment-service, "
                  "inventory-service, user-service, notification-service.")
    with c2:
        recent_changes = st.text_area("Recent Changes (deploys, config, infra)",
            value="- 2025-01-14 23:45 - Deployed payment-service v2.4.1 (new connection pool config)\n"
                  "- 2025-01-14 22:00 - RDS parameter group updated (max_connections: 150 -> 200)\n"
                  "- 2025-01-13 - Added 2 new read replicas for inventory-service",
            height=100)
        oncall_team = st.text_input("On-call Team",
            value="Platform Engineering (primary), Database Team (secondary)")

    context = st.text_input("Additional Context",
        value="This is peak transaction hour (2-3 AM UTC = evening US East). ~5,000 transactions/min.")

    submitted = st.form_submit_button("Triage Incident", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        alerts=alerts, environment=environment, architecture=architecture,
        recent_changes=recent_changes, oncall_team=oncall_team, context=context,
    )

    with st.spinner("Analyzing alerts and correlating signals..."):
        try:
            result = triage_incident(config, api_key)
        except Exception as e:
            st.error(f"Triage failed: {e}")
            st.stop()

    # Incident Summary
    inc = result.get("incident_summary", {})
    sev = inc.get("severity", "SEV3")
    sev_cls = "sev1" if "1" in sev else "sev2" if "2" in sev else "sev4" if "4" in sev else "sev3"
    st.markdown(f"""<div class="{sev_cls}">
        <h2>{sev} — {inc.get('title', 'Incident')}</h2>
        <strong>Status:</strong> {inc.get('status', 'Investigating')} |
        <strong>Blast Radius:</strong> {inc.get('blast_radius', 'N/A')} |
        <strong>Started:</strong> {inc.get('start_time', 'N/A')}<br/>
        <strong>Impact:</strong> {inc.get('impact', 'N/A')}<br/>
        <strong>Affected:</strong> {', '.join(inc.get('affected_services', []))}
    </div>""", unsafe_allow_html=True)

    # Alert Correlation
    groups = result.get("alert_correlation", [])
    if groups:
        st.divider()
        st.subheader("Alert Correlation")
        for g in groups:
            tag = g.get("is_symptom_or_cause", "Symptom")
            tag_color = "#f44336" if "Root" in tag else "#ff9800" if "Contributing" in tag else "#2196f3"
            alerts_list = "<br/>".join(f"- {a}" for a in g.get("alerts", []))
            st.markdown(f"""<div class="group-card">
                <strong>{g.get('group_name', '')}</strong>
                <span style="color:{tag_color}; font-weight:bold;"> [{tag}]</span><br/>
                {alerts_list}<br/>
                <em>Relationship: {g.get('relationship', '')}</em>
            </div>""", unsafe_allow_html=True)

    # Root Cause Analysis
    rca = result.get("root_cause_analysis", {})
    if rca:
        st.divider()
        st.subheader("Root Cause Analysis")
        conf = rca.get("confidence", "Medium")
        conf_color = "#4caf50" if conf == "High" else "#ff9800" if conf == "Medium" else "#f44336"
        st.markdown(f"**Primary Hypothesis:** {rca.get('primary_hypothesis', '')} "
                   f"<span style='color:{conf_color}; font-weight:bold;'>({conf} confidence)</span>",
                   unsafe_allow_html=True)

        st.markdown("**Evidence:**")
        for e in rca.get("evidence", []):
            st.markdown(f"- {e}")

        if rca.get("contributing_factors"):
            st.warning("**Contributing Factors:** " + " | ".join(rca["contributing_factors"]))

        alt = rca.get("alternative_hypotheses", [])
        if alt:
            st.markdown("**Alternative Hypotheses:**")
            for a in alt:
                st.markdown(f"- {a.get('hypothesis', '')} ({a.get('likelihood', '')} likelihood)")

        # Timeline
        timeline = rca.get("timeline_reconstruction", [])
        if timeline:
            st.markdown("**Timeline Reconstruction:**")
            for t in timeline:
                st.markdown(f"""<div class="timeline-card">
                    <strong>{t.get('time', '')}</strong> — {t.get('event', '')}<br/>
                    <small>{t.get('significance', '')}</small>
                </div>""", unsafe_allow_html=True)

    # Remediation
    rem = result.get("remediation", {})
    if rem:
        st.divider()
        st.subheader("Remediation Plan")

        immediate = rem.get("immediate_actions", [])
        if immediate:
            st.markdown("**Immediate Actions (NOW):**")
            for a in immediate:
                cmd = f"<br/><code>{a['command_hint']}</code>" if a.get("command_hint") else ""
                st.markdown(f"""<div class="action-card">
                    <strong>[{a.get('priority', 'P1')}]</strong> {a.get('action', '')}
                    — <em>Owner: {a.get('owner', 'TBD')}</em>{cmd}
                </div>""", unsafe_allow_html=True)

        stf, ltf = st.columns(2)
        with stf:
            short = rem.get("short_term_fixes", [])
            if short:
                st.markdown("**Short-term Fixes:**")
                for s in short:
                    st.markdown(f"- **{s.get('action', '')}** — {s.get('rationale', '')}")
        with ltf:
            long = rem.get("long_term_prevention", [])
            if long:
                st.markdown("**Long-term Prevention:**")
                for l in long:
                    st.markdown(f"- **{l.get('action', '')}** — {l.get('rationale', '')}")

    # Communication Templates
    comms = result.get("communication", {})
    if comms:
        st.divider()
        st.subheader("Communication")
        if comms.get("escalation_needed"):
            st.error(f"**Escalation needed!** Notify: {', '.join(comms.get('teams_to_notify', []))}")

        ct1, ct2 = st.columns(2)
        with ct1:
            st.markdown(f"""<div class="comms-card">
                <strong>Internal Update:</strong><br/>{comms.get('internal_update', '')}
            </div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="comms-card">
                <strong>Stakeholder Update:</strong><br/>{comms.get('stakeholder_update', '')}
            </div>""", unsafe_allow_html=True)
        with ct2:
            if comms.get("customer_facing"):
                st.markdown(f"""<div class="comms-card">
                    <strong>Status Page:</strong><br/>{comms['customer_facing']}
                </div>""", unsafe_allow_html=True)

    # Metrics to Watch
    metrics = result.get("metrics_to_watch", [])
    if metrics:
        st.divider()
        st.subheader("Recovery Metrics")
        met_df = pd.DataFrame([{
            "Metric": m.get("metric", ""),
            "Expected Recovery": m.get("expected_behavior", ""),
            "Dashboard": m.get("dashboard", ""),
        } for m in metrics])
        st.dataframe(met_df, use_container_width=True, hide_index=True)

    # Post-Incident
    post = result.get("post_incident", {})
    if post:
        st.divider()
        st.subheader("Post-Incident Follow-up")
        pc1, pc2 = st.columns(2)
        with pc1:
            st.markdown("**Blameless Review Topics:**")
            for t in post.get("blameless_review_topics", []):
                st.markdown(f"- {t}")
            st.markdown("**Process Improvements:**")
            for p in post.get("process_improvements", []):
                st.markdown(f"- {p}")
        with pc2:
            items = post.get("action_items", [])
            if items:
                st.markdown("**Action Items:**")
                ai_df = pd.DataFrame([{
                    "Item": i.get("item", ""),
                    "Priority": i.get("priority", ""),
                    "Owner": i.get("owner", ""),
                } for i in items])
                st.dataframe(ai_df, use_container_width=True, hide_index=True)

    # Export
    st.divider()
    st.download_button("Download Triage Report (JSON)", json.dumps(result, indent=2),
                       "incident_triage.json", "application/json")
