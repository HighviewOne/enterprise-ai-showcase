"""OpsAgent - Agentic Operations Assistant for Shared Platform Management - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.ops_engine import analyze_operations

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #263238 0%, #37474f 50%, #455a64 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: #80cbc4; margin: 0; }
    .go-box { background: #e8f5e9; border: 2px solid #2e7d32; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .nogo-box { background: #ffebee; border: 2px solid #c62828; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .conditional-box { background: #fff3e0; border: 2px solid #e65100; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .risk-card { background: #f8f9fa; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem; }
    .risk-high { border-left: 4px solid #f44336; }
    .risk-medium { border-left: 4px solid #ff9800; }
    .risk-low { border-left: 4px solid #4caf50; }
    .step-card { background: #f5f5f5; border-radius: 8px; padding: 0.8rem;
        margin-bottom: 0.4rem; border-left: 4px solid #1565c0; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**OpsAgent** streamlines shared service operations — databases, ETL, "
            "reporting, and admin tasks — through an intelligent, role-aware assistant.")

st.markdown("""<div class="hero"><h1>OpsAgent</h1>
<p>AI-powered operations assistant for shared platform management</p></div>""",
unsafe_allow_html=True)

with st.form("ops_form"):
    ops_request = st.text_area("Operations Request", height=250,
        value="Request: Migrate the customer_analytics database from PostgreSQL 12 to "
              "PostgreSQL 16 on the shared data platform.\n\n"
              "Context:\n"
              "- Database size: 2.3TB across 145 tables\n"
              "- 12 downstream ETL pipelines depend on this database\n"
              "- 8 Tableau dashboards and 3 Power BI reports pull from it\n"
              "- Contains PII (customer emails, phone numbers, addresses)\n"
              "- Current replication lag: avg 45 seconds\n"
              "- Peak query load: 2,500 queries/min during business hours (9AM-5PM EST)\n"
              "- The database hasn't been vacuumed in 6 months\n"
              "- 3 deprecated extensions in use (pg_trgm v1.4, hstore v1.6, ltree v1.1)\n"
              "- Monthly compute cost: $4,200\n"
              "- SLA: 99.95% uptime, max 4h planned downtime per quarter\n\n"
              "Urgency: PostgreSQL 12 reaches EOL in November 2024. Security team has "
              "flagged 3 unpatched CVEs.\n\n"
              "Constraints:\n"
              "- Zero data loss tolerance\n"
              "- Maximum 2h downtime window (approved for Sunday 2AM-4AM EST)\n"
              "- Must maintain backward compatibility for legacy Java microservices using JDBC\n"
              "- Finance reporting freeze period: no changes between 25th-5th of each month")

    c1, c2 = st.columns(2)
    with c1:
        platform = st.selectbox("Platform",
            ["AWS (RDS/Redshift)", "Azure (SQL/Synapse)", "GCP (CloudSQL/BigQuery)",
             "On-Premise", "Hybrid Cloud", "Multi-Cloud"],
            index=0)
        team_size = st.selectbox("Shared Platform Team Size",
            ["1-3 (Small)", "4-8 (Medium)", "9-15 (Large)", "15+ (Enterprise)"],
            index=1)
    with c2:
        environment = st.selectbox("Target Environment",
            ["Production", "Staging", "Development", "DR/Failover"],
            index=0)
        current_systems = st.multiselect("Current Systems Stack",
            ["PostgreSQL", "MySQL", "SQL Server", "Oracle", "MongoDB",
             "Airflow", "dbt", "Spark", "Kafka", "Tableau", "Power BI",
             "Looker", "Jenkins", "Terraform", "Kubernetes"],
            default=["PostgreSQL", "Airflow", "dbt", "Tableau", "Power BI", "Terraform"])
    compliance_reqs = st.multiselect("Compliance Requirements",
        ["SOX", "GDPR", "HIPAA", "SOC2", "PCI-DSS", "ISO 27001", "CCPA", "None"],
        default=["SOX", "GDPR", "SOC2"])

    submitted = st.form_submit_button("Analyse Request", type="primary",
                                       use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        ops_request=ops_request,
        platform=platform,
        team_size=team_size,
        environment=environment,
        current_systems=", ".join(current_systems),
        compliance_reqs=", ".join(compliance_reqs),
    )

    with st.spinner("Analysing operations request..."):
        try:
            result = analyze_operations(config, api_key)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    # Request Summary
    summary = result.get("request_summary", {})
    st.subheader("Request Summary")
    sm1, sm2, sm3, sm4 = st.columns(4)
    sm1.metric("Service Area", summary.get("service_area", ""))
    sm2.metric("Priority", summary.get("priority", ""))
    sm3.metric("Complexity", summary.get("complexity", ""))
    sm4.metric("Est. Effort", f"{summary.get('estimated_effort_hours', 0)}h")

    # Go / No-Go Recommendation
    rec = result.get("recommendation", {})
    verdict = rec.get("go_no_go", "Conditional Go")
    v_cls = ("go-box" if verdict == "Go" else "nogo-box" if verdict == "No-Go"
             else "conditional-box")
    st.markdown(f'<div class="{v_cls}"><span style="font-size:1.5rem;font-weight:bold">'
               f'{verdict}</span><br/>'
               f'{summary.get("title", "")}</div>', unsafe_allow_html=True)

    # Operations Plan Steps
    plan = result.get("operations_plan", {})
    steps = plan.get("steps", [])
    if steps:
        st.divider()
        st.subheader("Operations Plan")
        st.markdown(f"**Objective:** {plan.get('objective', '')}")
        if plan.get("prerequisites"):
            st.markdown("**Prerequisites:**")
            for p in plan["prerequisites"]:
                st.markdown(f"- {p}")
        for s in steps:
            risk_cls = f"risk-{s.get('risk_level', 'Low').lower()}"
            st.markdown(
                f'<div class="step-card {risk_cls}">'
                f'<strong>Step {s.get("step_number", "")}: {s.get("action", "")}</strong><br/>'
                f'Owner: {s.get("owner", "")} | Tool: {s.get("tool_or_system", "")} | '
                f'Duration: {s.get("duration_minutes", "")}min | Risk: {s.get("risk_level", "")}<br/>'
                f'<em>Rollback: {s.get("rollback_plan", "N/A")}</em></div>',
                unsafe_allow_html=True,
            )
        if plan.get("validation_checks"):
            st.markdown("**Validation Checks:**")
            for v in plan["validation_checks"]:
                st.markdown(f"- {v}")

    # Database & ETL Impact side by side
    dc1, dc2 = st.columns(2)
    db = result.get("database_impact", {})
    if db:
        with dc1:
            st.divider()
            st.subheader("Database Impact")
            st.markdown(f"**Affected DBs:** {', '.join(db.get('affected_databases', []))}")
            st.markdown(f"**Migration Required:** {'Yes' if db.get('migration_required') else 'No'}")
            st.markdown(f"**Data Volume:** {db.get('data_volume_estimate', '')}")
            st.markdown(f"**Backup Strategy:** {db.get('backup_strategy', '')}")
            st.markdown(f"**Downtime Required:** {'Yes' if db.get('downtime_required') else 'No'}")
            if db.get("downtime_window"):
                st.markdown(f"**Window:** {db['downtime_window']}")
            if db.get("schema_changes"):
                st.markdown("**Schema Changes:**")
                for sc in db["schema_changes"]:
                    st.markdown(f"- {sc}")

    etl = result.get("etl_pipeline_impact", {})
    if etl:
        with dc2:
            st.divider()
            st.subheader("ETL Pipeline Impact")
            if etl.get("affected_pipelines"):
                st.markdown(f"**Affected Pipelines:** {', '.join(etl['affected_pipelines'])}")
            if etl.get("new_pipelines_needed"):
                st.markdown("**New Pipelines:**")
                for np_ in etl["new_pipelines_needed"]:
                    st.markdown(f"- {np_}")
            if etl.get("data_quality_checks"):
                st.markdown("**Data Quality Checks:**")
                for dq in etl["data_quality_checks"]:
                    st.markdown(f"- {dq}")

    # Compliance & Cost side by side
    cc1, cc2 = st.columns(2)
    comp = result.get("compliance_assessment", {})
    if comp:
        with cc1:
            st.divider()
            st.subheader("Compliance Assessment")
            st.markdown(f"**Data Classification:** {comp.get('data_classification', '')}")
            st.markdown(f"**PII Involved:** {'Yes' if comp.get('pii_involved') else 'No'}")
            st.markdown(f"**Audit Trail:** {'Required' if comp.get('audit_trail_required') else 'Not Required'}")
            if comp.get("regulatory_frameworks"):
                st.markdown(f"**Frameworks:** {', '.join(comp['regulatory_frameworks'])}")
            if comp.get("approval_chain"):
                st.markdown("**Approval Chain:**")
                for a in comp["approval_chain"]:
                    st.markdown(f"- {a}")

    cost = result.get("cost_analysis", {})
    if cost:
        with cc2:
            st.divider()
            st.subheader("Cost Analysis")
            st.markdown(f"**Compute Delta:** {cost.get('compute_cost_delta', '')}")
            st.markdown(f"**Storage Delta:** {cost.get('storage_cost_delta', '')}")
            st.markdown(f"**Monthly Impact:** {cost.get('total_monthly_impact', '')}")
            if cost.get("cost_optimisation_tips"):
                st.markdown("**Optimisation Tips:**")
                for tip in cost["cost_optimisation_tips"]:
                    st.markdown(f"- {tip}")

    # Risk Matrix
    risks = result.get("risk_matrix", [])
    if risks:
        st.divider()
        st.subheader("Risk Matrix")
        risk_df = pd.DataFrame([{
            "Risk": r.get("risk", ""),
            "Likelihood": r.get("likelihood", ""),
            "Impact": r.get("impact", ""),
            "Mitigation": r.get("mitigation", ""),
        } for r in risks])
        st.dataframe(risk_df, use_container_width=True, hide_index=True)

        # Risk scatter plot
        level_map = {"Low": 1, "Medium": 2, "High": 3}
        fig = go.Figure()
        for r in risks:
            x = level_map.get(r.get("likelihood", "Medium"), 2)
            y = level_map.get(r.get("impact", "Medium"), 2)
            color = "#f44336" if x * y >= 6 else "#ff9800" if x * y >= 3 else "#4caf50"
            fig.add_trace(go.Scatter(
                x=[x], y=[y], mode="markers+text",
                marker=dict(size=18, color=color),
                text=[r.get("risk", "")[:30]],
                textposition="top center",
                showlegend=False,
            ))
        fig.update_layout(
            title="Risk Heat Map",
            xaxis=dict(title="Likelihood", tickvals=[1, 2, 3], ticktext=["Low", "Medium", "High"]),
            yaxis=dict(title="Impact", tickvals=[1, 2, 3], ticktext=["Low", "Medium", "High"]),
            height=350,
        )
        st.plotly_chart(fig, use_container_width=True)

    # Automation Opportunities
    autos = result.get("automation_opportunities", [])
    if autos:
        st.divider()
        st.subheader("Automation Opportunities")
        auto_df = pd.DataFrame([{
            "Task": a.get("task", ""),
            "Current Effort (h)": a.get("current_effort_hours", 0),
            "Approach": a.get("automation_approach", ""),
            "Savings (h/mo)": a.get("savings_hours_per_month", 0),
            "Complexity": a.get("implementation_complexity", ""),
        } for a in autos])
        st.dataframe(auto_df, use_container_width=True, hide_index=True)

        total_savings = sum(a.get("savings_hours_per_month", 0) for a in autos)
        st.success(f"Total potential savings: **{total_savings} hours/month** through automation")

    # Reporting Impact
    reporting = result.get("reporting_impact", {})
    if reporting:
        st.divider()
        st.subheader("Reporting Impact")
        if reporting.get("affected_reports"):
            st.markdown(f"**Affected Reports:** {', '.join(reporting['affected_reports'])}")
        if reporting.get("new_reports_needed"):
            st.markdown("**New Reports Needed:**")
            for nr in reporting["new_reports_needed"]:
                st.markdown(f"- {nr}")
        st.markdown(f"**Data Freshness SLA:** {reporting.get('data_freshness_sla', '')}")

    # Communication Plan
    comms = result.get("communication_plan", {})
    if comms:
        st.divider()
        st.subheader("Communication Plan")
        if comms.get("stakeholders"):
            st.markdown(f"**Stakeholders:** {', '.join(comms['stakeholders'])}")
        st.markdown(f"**CAB Required:** {'Yes' if comms.get('change_advisory_board') else 'No'}")
        st.markdown(f"**Pre-Change Notice:** {comms.get('pre_change_notice', '')}")
        st.markdown(f"**Post-Change Validation:** {comms.get('post_change_validation', '')}")

    # Recommendation
    if rec:
        st.divider()
        st.subheader("Recommendation")
        st.info(rec.get("rationale", ""))
        if rec.get("conditions"):
            st.markdown("**Conditions for Go:**")
            for c in rec["conditions"]:
                st.markdown(f"- {c}")
        if rec.get("alternative_approaches"):
            st.markdown("**Alternative Approaches:**")
            for a in rec["alternative_approaches"]:
                st.markdown(f"- {a}")

    st.divider()
    st.download_button("Download Operations Plan (JSON)", json.dumps(result, indent=2),
                       "ops_plan.json", "application/json")
