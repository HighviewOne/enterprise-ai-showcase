"""ChaosAgent - AI-Powered Chaos Engineering for Kubernetes - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.chaos_engine import run_chaos_analysis

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #b71c1c 0%, #e65100 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: #ffcc80; margin: 0; }
    .finding-card { background: #f8f9fa; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem; }
    .finding-critical { border-left: 4px solid #d32f2f; }
    .finding-high { border-left: 4px solid #f44336; }
    .finding-medium { border-left: 4px solid #ff9800; }
    .finding-low { border-left: 4px solid #4caf50; }
    .step-inject { background: #ffebee; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem; border-left: 4px solid #f44336; }
    .step-observe { background: #e3f2fd; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem; border-left: 4px solid #1976d2; }
    .step-rollback { background: #e8f5e9; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem; border-left: 4px solid #388e3c; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**ChaosAgent** orchestrates AI-powered chaos engineering experiments for "
            "Kubernetes clusters and surfaces actionable resilience insights.")

st.markdown("""<div class="hero"><h1>ChaosAgent</h1>
<p>AI-powered chaos engineering for Kubernetes resilience testing</p></div>""",
unsafe_allow_html=True)

with st.form("chaos_form"):
    c1, c2 = st.columns(2)
    with c1:
        namespace = st.text_input("Namespace", value="production")
        services = st.text_area("Services (one per line)", height=120,
            value="payment-service\norder-service\nuser-service\nredis-cluster\napi-gateway\nnotification-service")
    with c2:
        node_count = st.number_input("Node Count", min_value=1, max_value=500, value=12)
        replicas = st.text_area("Replica Counts (service: count, one per line)", height=120,
            value="payment-service: 3\norder-service: 4\nuser-service: 3\nredis-cluster: 3\napi-gateway: 2\nnotification-service: 2")

    chaos_scenario = st.text_area("Chaos Scenario (natural language)", height=150,
        value="Simulate network partition between payment-service and order-service in "
              "production namespace, then kill 2 of 3 redis pods. Additionally, introduce "
              "500ms latency on the api-gateway for 60 seconds. We want to validate that "
              "the system degrades gracefully, circuit breakers activate, and no data is "
              "lost during the cascading failure.")

    submitted = st.form_submit_button("Run Chaos Analysis", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    cluster_config = (
        f"Namespace: {namespace}\n"
        f"Node Count: {node_count}\n"
        f"Services:\n{services}\n"
        f"Replica Counts:\n{replicas}"
    )
    config = dict(cluster_config=cluster_config, chaos_scenario=chaos_scenario)

    with st.spinner("Analyzing chaos scenario..."):
        try:
            result = run_chaos_analysis(config, api_key)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    # Scenario Plan
    plan = result.get("scenario_plan", {})
    st.subheader("Scenario Plan")
    pm1, pm2, pm3, pm4 = st.columns(4)
    pm1.metric("Scenario", plan.get("scenario_name", "")[:30])
    pm2.metric("Chaos Type", plan.get("chaos_type", ""))
    pm3.metric("Duration", f"{plan.get('duration_minutes', 0)} min")
    pm4.metric("Targets", str(len(plan.get("target_services", []))))
    st.info(f"**Objective:** {plan.get('objective', '')}")
    st.markdown(f"**Hypothesis:** {plan.get('hypothesis', '')}")

    # Blast Radius Visualization
    blast = result.get("blast_radius", {})
    if blast:
        st.divider()
        st.subheader("Blast Radius")

        direct = blast.get("directly_affected", [])
        indirect = blast.get("indirectly_affected", [])

        # Build blast radius chart
        labels = []
        severities = []
        impact_types = []
        for item in direct:
            labels.append(item.get("service", ""))
            severities.append(item.get("severity", "Medium"))
            impact_types.append("Direct")
        for item in indirect:
            labels.append(item.get("service", ""))
            severities.append(item.get("severity", "Medium"))
            impact_types.append("Indirect")

        if labels:
            sev_map = {"Critical": 4, "High": 3, "Medium": 2, "Low": 1}
            color_map = {"Critical": "#d32f2f", "High": "#f44336", "Medium": "#ff9800", "Low": "#4caf50"}
            sev_values = [sev_map.get(s, 1) for s in severities]
            colors = [color_map.get(s, "#ff9800") for s in severities]
            symbols = ["circle" if t == "Direct" else "diamond" for t in impact_types]

            fig = go.Figure()
            for i, label in enumerate(labels):
                fig.add_trace(go.Scatter(
                    x=[impact_types[i]], y=[sev_values[i]],
                    mode="markers+text",
                    marker=dict(size=sev_values[i] * 20, color=colors[i],
                                symbol=symbols[i], opacity=0.7),
                    text=[label], textposition="top center",
                    name=f"{label} ({impact_types[i]})",
                    showlegend=True,
                ))
            fig.update_layout(
                title="Blast Radius - Service Impact",
                yaxis=dict(title="Severity", tickvals=[1, 2, 3, 4],
                          ticktext=["Low", "Medium", "High", "Critical"]),
                xaxis=dict(title="Impact Type"),
                height=400,
            )
            st.plotly_chart(fig, use_container_width=True)

        # Dependency chain
        deps = blast.get("dependency_chain", [])
        if deps:
            st.markdown("**Dependency Chain:**")
            for d in deps:
                st.code(d)

        st.warning(f"**User Impact:** {blast.get('estimated_user_impact', '')}")

    # Experiment Steps
    steps = result.get("experiment_steps", [])
    if steps:
        st.divider()
        st.subheader("Experiment Steps")
        for step in steps:
            phase = step.get("phase", "Observe").lower()
            cls = f"step-{phase}" if phase in ("inject", "observe", "rollback") else "step-observe"
            st.markdown(
                f'<div class="{cls}">'
                f'<strong>Step {step.get("step_number", "")}: {step.get("phase", "")}</strong> '
                f'({step.get("duration_seconds", 0)}s)<br/>'
                f'{step.get("action", "")}<br/>'
                f'<code>{step.get("command", "")}</code><br/>'
                f'<em>Success: {step.get("success_criteria", "")}</em></div>',
                unsafe_allow_html=True)

    # Expected Behavior & Resilience Findings
    ec1, ec2 = st.columns(2)
    expected = result.get("expected_behavior", {})
    if expected:
        with ec1:
            st.divider()
            st.subheader("Expected Behavior")
            st.markdown(f"**Resilient Response:** {expected.get('resilient_response', '')}")
            st.markdown(f"**Degraded Mode:** {expected.get('degraded_mode', '')}")
            st.markdown(f"**Recovery Target:** {expected.get('recovery_time_target', '')}")
            cbs = expected.get("circuit_breakers", [])
            if cbs:
                st.markdown("**Circuit Breakers:**")
                for cb in cbs:
                    st.markdown(f"- {cb}")

    findings = result.get("resilience_findings", [])
    if findings:
        with ec2:
            st.divider()
            st.subheader("Resilience Findings")
            for f in findings:
                sev = f.get("severity", "Medium").lower()
                cls = f"finding-{sev}"
                cat = f.get("category", "")
                icon = "+" if cat == "Strength" else "-" if cat == "Weakness" else "~"
                st.markdown(
                    f'<div class="finding-card {cls}">'
                    f'<strong>[{icon}] {f.get("finding", "")}</strong> '
                    f'({f.get("severity", "")})<br/>'
                    f'Component: {f.get("affected_component", "")}<br/>'
                    f'Evidence: {f.get("evidence", "")}</div>',
                    unsafe_allow_html=True)

    # Remediation Recommendations
    recs = result.get("remediation_recommendations", [])
    if recs:
        st.divider()
        st.subheader("Remediation Recommendations")
        rec_df = pd.DataFrame([{
            "Priority": r.get("priority", ""),
            "Recommendation": r.get("recommendation", ""),
            "Effort": r.get("effort", ""),
            "Implementation": r.get("implementation", ""),
        } for r in recs])
        st.dataframe(rec_df, use_container_width=True, hide_index=True)

    # SLA Impact
    sla = result.get("sla_impact_assessment", {})
    if sla:
        st.divider()
        st.subheader("SLA Impact Assessment")
        sc1, sc2, sc3 = st.columns(3)
        sc1.metric("Availability Impact", sla.get("availability_impact", ""))
        sc2.metric("Latency Impact", sla.get("latency_impact", ""))
        sc3.metric("MTTR Estimate", sla.get("mttr_estimate", ""))
        if sla.get("affected_slos"):
            st.markdown("**Affected SLOs:**")
            for s in sla["affected_slos"]:
                st.markdown(f"- {s}")

    # Runbook
    runbook = result.get("runbook_generation", {})
    if runbook:
        st.divider()
        st.subheader(f"Incident Runbook: {runbook.get('incident_title', '')}")
        with st.expander("Detection", expanded=False):
            for d in runbook.get("detection", []):
                st.markdown(f"- {d}")
        with st.expander("Triage Steps", expanded=False):
            for i, t in enumerate(runbook.get("triage_steps", []), 1):
                st.markdown(f"{i}. {t}")
        with st.expander("Mitigation Steps", expanded=False):
            for i, m in enumerate(runbook.get("mitigation_steps", []), 1):
                st.markdown(f"{i}. {m}")
        with st.expander("Resolution Steps", expanded=False):
            for i, r in enumerate(runbook.get("resolution_steps", []), 1):
                st.markdown(f"{i}. {r}")

    st.divider()
    st.download_button("Download Chaos Report (JSON)", json.dumps(result, indent=2),
                       "chaos_report.json", "application/json")
