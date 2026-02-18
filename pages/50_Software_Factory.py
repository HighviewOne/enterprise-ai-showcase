"""BlueprintAI - Software Factory Technical Blueprint Generator - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.factory_engine import generate_blueprint

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #0d47a1 0%, #1565c0 50%, #0277bd 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: #80d8ff; margin: 0; }
    .risk-card { background: #f8f9fa; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem; }
    .risk-high { border-left: 4px solid #f44336; }
    .risk-medium { border-left: 4px solid #ff9800; }
    .risk-low { border-left: 4px solid #4caf50; }
    .phase-card { background: #e3f2fd; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
        border-left: 4px solid #1565c0; }
    .cost-card { background: #f1f8e9; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem;
        border-left: 4px solid #558b2f; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**BlueprintAI** transforms high-level business concepts into enterprise-grade "
            "technical blueprints with architecture, cost estimates, and implementation roadmaps.")

st.markdown("""<div class="hero"><h1>BlueprintAI</h1>
<p>From business concept to technical blueprint in minutes</p></div>""",
unsafe_allow_html=True)

with st.form("factory_form"):
    business_concept = st.text_area("Business Concept", height=180,
        value="Build a real-time fraud detection system for a mid-size bank processing 50K "
              "transactions/day. The system needs to score each transaction in under 100ms, "
              "support rule-based and ML-based detection, integrate with the existing core "
              "banking system via REST APIs, provide a dashboard for fraud analysts to review "
              "flagged transactions, and generate regulatory reports (SAR filing). Must comply "
              "with PCI-DSS, SOX, and bank secrecy act requirements. The system should handle "
              "10x traffic spikes during peak shopping seasons.")

    c1, c2, c3 = st.columns(3)
    with c1:
        target_platform = st.selectbox("Target Cloud Platform",
            ["AWS", "Azure", "Google Cloud", "Multi-Cloud", "On-Premise + Cloud Hybrid"],
            index=0)
        team_size = st.selectbox("Team Size",
            ["2-3 (Startup)", "4-6 (Small)", "7-12 (Medium)", "13-20 (Large)", "20+ (Enterprise)"],
            index=2)
    with c2:
        tech_preferences = st.text_area("Tech Preferences (optional)", height=100,
            value="Python for ML services, Java/Spring Boot for transaction processing, "
                  "React for frontend, PostgreSQL preferred, Kafka for streaming")
        timeline = st.selectbox("Timeline",
            ["3 months (MVP)", "6 months (V1)", "9 months (Full)", "12 months (Enterprise)", "18+ months"],
            index=2)
    with c3:
        budget_range = st.selectbox("Budget Range",
            ["$50K-$100K", "$100K-$250K", "$250K-$500K", "$500K-$1M", "$1M-$5M", "$5M+"],
            index=3)

    submitted = st.form_submit_button("Generate Blueprint", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        business_concept=business_concept,
        target_platform=target_platform,
        tech_preferences=tech_preferences,
        team_size=team_size,
        timeline=timeline,
        budget_range=budget_range,
    )

    with st.spinner("Generating technical blueprint..."):
        try:
            result = generate_blueprint(config, api_key)
        except Exception as e:
            st.error(f"Blueprint generation failed: {e}")
            st.stop()

    # Executive Summary
    summary = result.get("executive_summary", {})
    st.subheader("Executive Summary")
    em1, em2, em3, em4 = st.columns(4)
    em1.metric("Project", summary.get("project_name", ""))
    em2.metric("Complexity", summary.get("complexity", ""))
    em3.metric("Confidence", summary.get("confidence_level", ""))
    em4.metric("Differentiators", str(len(summary.get("key_differentiators", []))))
    st.info(summary.get("vision", ""))

    # Requirements
    reqs = result.get("requirements_analysis", {})
    if reqs:
        st.divider()
        st.subheader("Requirements Analysis")
        r1, r2 = st.columns(2)
        func_reqs = reqs.get("functional_requirements", [])
        if func_reqs:
            with r1:
                st.markdown("**Functional Requirements**")
                fr_df = pd.DataFrame([{
                    "ID": r.get("id", ""),
                    "Requirement": r.get("requirement", ""),
                    "Priority": r.get("priority", ""),
                    "Complexity": r.get("complexity", ""),
                } for r in func_reqs])
                st.dataframe(fr_df, use_container_width=True, hide_index=True)

        nf_reqs = reqs.get("non_functional_requirements", [])
        if nf_reqs:
            with r2:
                st.markdown("**Non-Functional Requirements**")
                nfr_df = pd.DataFrame([{
                    "ID": r.get("id", ""),
                    "Category": r.get("category", ""),
                    "Requirement": r.get("requirement", ""),
                    "Target": r.get("target_metric", ""),
                } for r in nf_reqs])
                st.dataframe(nfr_df, use_container_width=True, hide_index=True)

    # Architecture & Tech Stack
    arch = result.get("architecture_blueprint", {})
    tech = result.get("technology_stack", {})
    ac1, ac2 = st.columns(2)
    if arch:
        with ac1:
            st.divider()
            st.subheader(f"Architecture: {arch.get('pattern', '')}")
            components = arch.get("components", [])
            if components:
                comp_df = pd.DataFrame([{
                    "Component": c.get("name", ""),
                    "Type": c.get("type", ""),
                    "Technology": c.get("technology", ""),
                    "Responsibility": c.get("responsibility", ""),
                } for c in components])
                st.dataframe(comp_df, use_container_width=True, hide_index=True)

    if tech:
        with ac2:
            st.divider()
            st.subheader("Technology Stack")
            for key in ["frontend", "backend", "database", "cache", "message_queue", "monitoring", "ci_cd"]:
                item = tech.get(key, {})
                if item and isinstance(item, dict):
                    label = key.replace("_", " ").title()
                    st.markdown(f"**{label}:** {item.get('technology', '')} - _{item.get('rationale', '')}_")

    # API Design
    apis = result.get("api_design", [])
    if apis:
        st.divider()
        st.subheader("API Design")
        api_df = pd.DataFrame([{
            "Method": a.get("method", ""),
            "Endpoint": a.get("endpoint", ""),
            "Description": a.get("description", ""),
            "Auth": a.get("auth", ""),
        } for a in apis])
        st.dataframe(api_df, use_container_width=True, hide_index=True)

    # Data Model
    data_model = result.get("data_model", [])
    if data_model:
        st.divider()
        st.subheader("Data Model")
        dm_df = pd.DataFrame([{
            "Entity": d.get("entity", ""),
            "Description": d.get("description", ""),
            "Key Fields": ", ".join(d.get("key_fields", [])),
            "Storage": d.get("storage", ""),
        } for d in data_model])
        st.dataframe(dm_df, use_container_width=True, hide_index=True)

    # Implementation Roadmap - Gantt Chart
    roadmap = result.get("implementation_roadmap", [])
    if roadmap:
        st.divider()
        st.subheader("Implementation Roadmap")

        # Build Gantt-style chart
        phases = []
        start_week = 0
        for phase in roadmap:
            duration = phase.get("duration_weeks", 4)
            phases.append({
                "phase": phase.get("phase", ""),
                "start": start_week,
                "end": start_week + duration,
                "duration": duration,
                "milestones": ", ".join(phase.get("milestones", [])),
            })
            start_week += duration

        if phases:
            colors = ["#1565c0", "#0277bd", "#00838f", "#00695c", "#2e7d32",
                      "#558b2f", "#9e9d24", "#f9a825", "#ff8f00", "#ef6c00"]
            fig = go.Figure()
            for i, p in enumerate(phases):
                fig.add_trace(go.Bar(
                    y=[p["phase"]],
                    x=[p["duration"]],
                    base=[p["start"]],
                    orientation="h",
                    marker=dict(color=colors[i % len(colors)]),
                    text=[f"{p['duration']}w"],
                    textposition="inside",
                    name=p["phase"],
                    hovertext=p["milestones"],
                ))
            fig.update_layout(
                title="Implementation Timeline (Weeks)",
                xaxis=dict(title="Weeks", dtick=4),
                yaxis=dict(autorange="reversed"),
                barmode="stack",
                height=max(300, len(phases) * 60),
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

        # Phase details
        for phase in roadmap:
            with st.expander(f"{phase.get('phase', '')} ({phase.get('duration_weeks', 0)} weeks)"):
                st.markdown("**Milestones:**")
                for m in phase.get("milestones", []):
                    st.markdown(f"- {m}")
                if phase.get("risks"):
                    st.markdown("**Risks:**")
                    for r in phase["risks"]:
                        st.warning(r)

    # Cost Estimate & Security side by side
    cc1, cc2 = st.columns(2)
    cost = result.get("cost_estimate", {})
    if cost:
        with cc1:
            st.divider()
            st.subheader("Cost Estimate")
            st.metric("Monthly Dev", cost.get("monthly_dev", ""))
            st.metric("Monthly Production", cost.get("monthly_production", ""))
            st.metric("Monthly at Scale", cost.get("monthly_scaled", ""))
            breakdown = cost.get("cost_breakdown", [])
            if breakdown:
                cb_df = pd.DataFrame([{
                    "Category": c.get("category", ""),
                    "Monthly Cost": c.get("monthly_cost", ""),
                    "Notes": c.get("notes", ""),
                } for c in breakdown])
                st.dataframe(cb_df, use_container_width=True, hide_index=True)

    security = result.get("security_architecture", {})
    if security:
        with cc2:
            st.divider()
            st.subheader("Security Architecture")
            st.markdown(f"**Authentication:** {security.get('authentication', '')}")
            st.markdown(f"**Authorization:** {security.get('authorization', '')}")
            st.markdown(f"**Encryption:** {security.get('data_encryption', '')}")
            st.markdown(f"**Network:** {security.get('network_security', '')}")
            compliance = security.get("compliance_requirements", [])
            if compliance:
                st.markdown("**Compliance:** " + ", ".join(compliance))

    # Team Structure
    team = result.get("team_structure", [])
    if team:
        st.divider()
        st.subheader("Team Structure")
        team_df = pd.DataFrame([{
            "Role": t.get("role", ""),
            "Count": t.get("count", 0),
            "Skills": ", ".join(t.get("skills", [])),
            "Phase": t.get("phase_needed", ""),
            "Full-Time": "Yes" if t.get("full_time") else "Part-Time",
        } for t in team])
        st.dataframe(team_df, use_container_width=True, hide_index=True)

    # Risk Assessment
    risks = result.get("risk_assessment", [])
    if risks:
        st.divider()
        st.subheader("Risk Assessment")
        for r in risks:
            impact = r.get("impact", "Medium").lower()
            cls = f"risk-{impact}"
            st.markdown(
                f'<div class="risk-card {cls}">'
                f'<strong>{r.get("risk", "")}</strong> '
                f'({r.get("category", "")} - Probability: {r.get("probability", "")}, '
                f'Impact: {r.get("impact", "")})<br/>'
                f'Mitigation: {r.get("mitigation", "")}<br/>'
                f'<em>Contingency: {r.get("contingency", "")}</em></div>',
                unsafe_allow_html=True)

    # Deployment Strategy
    deploy = result.get("deployment_strategy", {})
    if deploy:
        st.divider()
        st.subheader("Deployment Strategy")
        st.markdown(f"**Approach:** {deploy.get('approach', '')}")
        if deploy.get("ci_pipeline"):
            st.markdown("**CI Pipeline:** " + " -> ".join(deploy["ci_pipeline"]))
        if deploy.get("cd_pipeline"):
            st.markdown("**CD Pipeline:** " + " -> ".join(deploy["cd_pipeline"]))
        st.markdown(f"**Rollback:** {deploy.get('rollback_plan', '')}")

    st.divider()
    st.download_button("Download Blueprint (JSON)", json.dumps(result, indent=2),
                       "technical_blueprint.json", "application/json")
