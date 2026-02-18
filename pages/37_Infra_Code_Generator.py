"""Infrastructure Code Generator - AI-Powered IaC - Streamlit Application."""

import os
import json
import streamlit as st
from dotenv import load_dotenv

from engines.infra_engine import generate_infra

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #e65100 0%, #f57c00 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .code-card { background: #263238; border-radius: 10px; padding: 1.2rem; margin-bottom: 0.8rem;
        color: #e0e0e0; font-family: monospace; }
    .step-card { background: #e3f2fd; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
        border-left: 4px solid #1565c0; }
    .security-pass { color: #4caf50; }
    .security-warn { color: #ff9800; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**InfraAgent** generates production-ready Infrastructure as Code from "
            "natural language requirements, following cloud best practices.")

st.markdown("""<div class="hero"><h1>InfraAgent</h1>
<p>AI-powered Infrastructure as Code generation — describe what you need, get production-ready Terraform/CloudFormation</p></div>""",
unsafe_allow_html=True)

with st.form("infra_form"):
    requirements = st.text_area("Infrastructure Requirements", height=200,
        value="I need a highly available web application infrastructure:\n"
              "- VPC with public and private subnets across 2 AZs\n"
              "- Application Load Balancer (ALB) in public subnets\n"
              "- Auto Scaling Group with 2-6 EC2 instances (t3.medium) in private subnets\n"
              "- RDS PostgreSQL (db.t3.medium) with Multi-AZ standby\n"
              "- ElastiCache Redis cluster for session management\n"
              "- S3 bucket for static assets with CloudFront CDN\n"
              "- All data encrypted at rest and in transit\n"
              "- VPC Flow Logs enabled\n"
              "- WAF on the ALB")

    c1, c2 = st.columns(2)
    with c1:
        provider = st.selectbox("Cloud Provider", ["AWS", "Azure", "GCP"])
        iac_tool = st.selectbox("IaC Tool", ["Terraform", "CloudFormation", "Pulumi", "Bicep"])
        environment = st.selectbox("Environment", ["Production", "Staging", "Development", "DR"])
    with c2:
        region = st.text_input("Region", value="us-east-1")
        naming = st.text_input("Naming Convention", value="myapp-{env}-{resource}")
        security_level = st.selectbox("Security Level",
            ["Standard", "Enhanced (SOC2/HIPAA)", "Maximum (FedRAMP/PCI)"], index=1)
    constraints = st.text_input("Additional Constraints",
        value="Budget target: under $2000/month. Must use latest AMI. Tag everything with Environment and Team.")

    submitted = st.form_submit_button("Generate Infrastructure Code", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        requirements=requirements, provider=provider, iac_tool=iac_tool,
        environment=environment, region=region, naming=naming,
        security_level=security_level, constraints=constraints,
    )

    with st.spinner("Generating infrastructure code..."):
        try:
            result = generate_infra(config, api_key)
        except Exception as e:
            st.error(f"Generation failed: {e}")
            st.stop()

    # Architecture Summary
    arch = result.get("architecture_summary", {})
    st.subheader("Architecture Overview")
    am1, am2, am3 = st.columns(3)
    am1.metric("Provider", arch.get("cloud_provider", provider))
    am2.metric("IaC Tool", arch.get("iac_tool", iac_tool))
    am3.metric("Est. Monthly Cost", arch.get("estimated_monthly_cost", "N/A"))
    st.info(arch.get("description", ""))

    if arch.get("components"):
        st.markdown("**Components:**")
        for comp in arch["components"]:
            st.markdown(f"- {comp}")

    # Generated Code
    code_files = result.get("generated_code", [])
    if code_files:
        st.divider()
        st.subheader(f"Generated Code ({len(code_files)} files)")
        for f in code_files:
            with st.expander(f"📄 {f.get('filename', '')} — {f.get('description', '')}"):
                st.code(f.get("code", ""), language="hcl" if "tf" in f.get("filename", "") else "yaml")
                if f.get("notes"):
                    st.caption(f.get("notes"))

    # Variables
    variables = result.get("variables_and_inputs", [])
    if variables:
        st.divider()
        st.subheader("Variables & Inputs")
        for v in variables:
            sensitive = " 🔒" if v.get("sensitive") else ""
            st.markdown(f"**`{v.get('variable', '')}`** ({v.get('type', 'string')}){sensitive} — "
                       f"{v.get('description', '')}")
            if v.get("default"):
                st.caption(f"Default: `{v['default']}`")

    # Security Review
    sec = result.get("security_review", {})
    if sec:
        st.divider()
        st.subheader("Security Review")
        sc1, sc2 = st.columns(2)
        with sc1:
            st.markdown("**Security Features Included:**")
            for s in sec.get("security_features", []):
                st.markdown(f'- <span class="security-pass">{s}</span>', unsafe_allow_html=True)
            if sec.get("compliance_alignment"):
                st.markdown(f"**Compliance:** {', '.join(sec['compliance_alignment'])}")
        with sc2:
            if sec.get("remaining_considerations"):
                st.markdown("**Review Manually:**")
                for r in sec["remaining_considerations"]:
                    st.markdown(f'- <span class="security-warn">{r}</span>', unsafe_allow_html=True)

    # Deployment Steps
    steps = result.get("deployment_steps", [])
    if steps:
        st.divider()
        st.subheader("Deployment Steps")
        for s in steps:
            st.markdown(f'<div class="step-card"><strong>Step {s.get("step", "")}:</strong> '
                       f'{s.get("description", "")}<br/>'
                       f'<code>{s.get("command", "")}</code></div>', unsafe_allow_html=True)
            if s.get("prerequisites"):
                st.caption(f"Prerequisites: {s['prerequisites']}")

    # Cost Breakdown
    costs = result.get("cost_breakdown", [])
    if costs:
        st.divider()
        st.subheader("Cost Breakdown")
        for c in costs:
            st.markdown(f"- **{c.get('service', '')}** ({c.get('configuration', '')}): "
                       f"{c.get('estimated_monthly', '')} — {c.get('notes', '')}")

    # Best Practices & Warnings
    bp = result.get("best_practices_applied", [])
    warns = result.get("warnings", [])
    if bp or warns:
        st.divider()
        bc1, bc2 = st.columns(2)
        with bc1:
            if bp:
                st.markdown("**Best Practices Applied:**")
                for b in bp:
                    st.markdown(f"- {b}")
        with bc2:
            if warns:
                st.markdown("**Warnings:**")
                for w in warns:
                    st.warning(w)

    st.divider()
    st.download_button("Download IaC Package (JSON)", json.dumps(result, indent=2),
                       "infra_code.json", "application/json")
