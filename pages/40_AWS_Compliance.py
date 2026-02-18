"""AWSentinel - AWS Compliance & Healing - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.compliance_engine import assess_compliance

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #ff6f00 0%, #ff8f00 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .finding-card { background: #f8f9fa; border-radius: 10px; padding: 1rem; margin-bottom: 0.6rem; }
    .sev-critical { border-left: 4px solid #b71c1c; background: #ffebee; }
    .sev-high { border-left: 4px solid #f44336; }
    .sev-medium { border-left: 4px solid #ff9800; }
    .sev-low { border-left: 4px solid #2196f3; }
    .sev-info { border-left: 4px solid #9e9e9e; }
    .fix-card { background: #e8f5e9; border-radius: 8px; padding: 1rem; margin-top: 0.5rem; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**AWSentinel** provides AI-powered compliance scoring and auto-remediation "
            "guidance for AWS environments.")

st.markdown("""<div class="hero"><h1>AWSentinel</h1>
<p>Smart compliance scoring & self-healing for AWS workloads — CIS, SOC2, HIPAA, PCI-DSS</p></div>""",
unsafe_allow_html=True)

with st.form("compliance_form"):
    config_data = st.text_area("AWS Environment Configuration", height=300,
        value="AWS Account: 123456789012 (Production)\nRegion: us-east-1\n\n"
              "=== IAM ===\n"
              "- Root account: MFA enabled, access keys ACTIVE (last used 2 weeks ago)\n"
              "- 12 IAM users, 3 without MFA enabled\n"
              "- 2 users have AdministratorAccess policy directly attached\n"
              "- Password policy: 8 char minimum, no rotation requirement\n"
              "- 5 unused IAM roles (no activity in 90+ days)\n\n"
              "=== NETWORKING ===\n"
              "- 1 VPC (10.0.0.0/16), 4 subnets (2 public, 2 private)\n"
              "- 3 Security Groups with 0.0.0.0/0 inbound on port 22 (SSH)\n"
              "- 1 Security Group with 0.0.0.0/0 inbound on all ports\n"
              "- VPC Flow Logs: DISABLED\n"
              "- No VPN or Direct Connect\n\n"
              "=== STORAGE ===\n"
              "- S3: 8 buckets, 2 with public access enabled\n"
              "- S3 bucket 'backup-data-prod': no versioning, no encryption\n"
              "- EBS: 15 volumes, 6 unencrypted\n\n"
              "=== COMPUTE ===\n"
              "- 12 EC2 instances (mix of t3.medium and m5.large)\n"
              "- 4 instances using default VPC security group\n"
              "- SSM Agent not installed on 3 instances\n"
              "- IMDSv2 not enforced on 8 instances\n\n"
              "=== DATABASE ===\n"
              "- RDS PostgreSQL: Multi-AZ enabled, encrypted, public access OFF\n"
              "- RDS MySQL: Single-AZ, NOT encrypted, public access ON\n\n"
              "=== LOGGING ===\n"
              "- CloudTrail: Enabled in us-east-1 only (not multi-region)\n"
              "- GuardDuty: Not enabled\n"
              "- Config: Not enabled\n"
              "- CloudWatch Alarms: Basic (CPU only)")

    c1, c2 = st.columns(2)
    with c1:
        account_type = st.selectbox("Account Type",
            ["Production", "Staging", "Development", "Shared Services"])
        frameworks = st.multiselect("Target Frameworks",
            ["CIS AWS Benchmark v1.5", "SOC 2", "HIPAA", "PCI-DSS", "NIST 800-53"],
            default=["CIS AWS Benchmark v1.5", "SOC 2"])
    with c2:
        environment = st.selectbox("Environment Classification",
            ["Production - Critical", "Production - Standard", "Non-Production"])
        context = st.text_input("Additional Context",
            value="Preparing for SOC2 Type II audit in Q2. Need to remediate critical gaps.")

    submitted = st.form_submit_button("Run Compliance Scan", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        config_data=config_data, account_type=account_type,
        frameworks=", ".join(frameworks), environment=environment, context=context,
    )

    with st.spinner("Scanning AWS environment..."):
        try:
            result = assess_compliance(config, api_key)
        except Exception as e:
            st.error(f"Scan failed: {e}")
            st.stop()

    # Overall Assessment
    overall = result.get("overall_assessment", {})
    score = overall.get("compliance_score", 50)

    st.subheader("Compliance Overview")
    oc1, oc2 = st.columns([1, 2])
    with oc1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=score,
            title={"text": "Compliance Score"},
            gauge={"axis": {"range": [0, 100]},
                   "bar": {"color": "#4caf50" if score >= 80 else "#ff9800" if score >= 50 else "#f44336"},
                   "steps": [{"range": [0, 50], "color": "#ffebee"},
                             {"range": [50, 80], "color": "#fff3e0"},
                             {"range": [80, 100], "color": "#e8f5e9"}]},
        ))
        fig.update_layout(height=250, margin=dict(t=40, b=0, l=30, r=30))
        st.plotly_chart(fig, use_container_width=True)

    with oc2:
        om1, om2, om3, om4 = st.columns(4)
        om1.metric("Total Checks", overall.get("total_checks", 0))
        om2.metric("Passed", overall.get("passed", 0))
        om3.metric("Failed", overall.get("failed", 0))
        om4.metric("Warnings", overall.get("warnings", 0))
        st.info(overall.get("headline", ""))

    # Category Scores
    cats = result.get("category_scores", [])
    if cats:
        st.divider()
        st.subheader("Category Scores")
        fig_cats = go.Figure(go.Bar(
            x=[c.get("category", "")[:20] for c in cats],
            y=[c.get("score", 0) for c in cats],
            marker_color=[
                "#4caf50" if c.get("score", 0) >= 80
                else "#ff9800" if c.get("score", 0) >= 50
                else "#f44336" for c in cats],
            text=[f"{c.get('score', 0)}%" for c in cats],
            textposition="outside",
        ))
        fig_cats.update_layout(title="Compliance by Category", height=300, yaxis_range=[0, 100])
        st.plotly_chart(fig_cats, use_container_width=True)

    # Findings
    findings = result.get("findings", [])
    if findings:
        st.divider()
        st.subheader(f"Findings ({len(findings)})")

        sev_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Informational": 4}
        for f in sorted(findings, key=lambda x: sev_order.get(x.get("severity", "Medium"), 2)):
            sev = f.get("severity", "Medium").lower()
            cls = f"sev-{sev}" if sev in ("critical", "high", "medium", "low") else "sev-info"
            status = f.get("status", "FAIL")
            st.markdown(f'<div class="finding-card {cls}">'
                       f'<strong>[{status}] {f.get("finding_id", "")}: {f.get("title", "")}</strong> '
                       f'({f.get("severity", "")})<br/>'
                       f'Resource: {f.get("resource", "")}</div>', unsafe_allow_html=True)

            if status != "PASS":
                with st.expander(f"Remediation: {f.get('finding_id', '')}"):
                    st.markdown(f"**Description:** {f.get('description', '')}")
                    st.markdown(f"**Impact:** {f.get('impact', '')}")
                    rem = f.get("remediation", {})
                    st.markdown(f"**Fix:** {rem.get('description', '')}")
                    if rem.get("cli_command"):
                        st.code(rem["cli_command"], language="bash")
                    if rem.get("terraform_fix"):
                        st.code(rem["terraform_fix"], language="hcl")
                    if f.get("compliance_mapping"):
                        st.caption(f"Maps to: {', '.join(f['compliance_mapping'])}")

    # Framework Coverage
    fworks = result.get("compliance_frameworks", [])
    if fworks:
        st.divider()
        st.subheader("Framework Coverage")
        fw_df = pd.DataFrame([{
            "Framework": fw.get("framework", ""),
            "Coverage": f"{fw.get('coverage', 0)}%",
            "Gaps": fw.get("gaps", 0),
        } for fw in fworks])
        st.dataframe(fw_df, use_container_width=True, hide_index=True)
        for fw in fworks:
            if fw.get("critical_gaps"):
                with st.expander(f"Critical Gaps: {fw.get('framework', '')}"):
                    for g in fw["critical_gaps"]:
                        st.error(g)

    # Remediation Priority
    priority = result.get("remediation_priority", [])
    if priority:
        st.divider()
        st.subheader("Remediation Priority")
        for p in priority[:10]:
            effort = p.get("effort", "Medium")
            eff_icon = "⚡" if effort == "Quick Win" else "🔧" if effort == "Medium" else "🏗️"
            st.markdown(f"**#{p.get('priority', '')}** {eff_icon} {p.get('action', '')} "
                       f"— Risk Reduction: {p.get('risk_reduction', '')}")

    # Recommendations
    recs = result.get("recommendations", [])
    if recs:
        st.divider()
        st.subheader("Strategic Recommendations")
        for r in recs:
            st.markdown(f"- {r}")

    st.divider()
    st.download_button("Download Compliance Report (JSON)", json.dumps(result, indent=2),
                       "aws_compliance.json", "application/json")
