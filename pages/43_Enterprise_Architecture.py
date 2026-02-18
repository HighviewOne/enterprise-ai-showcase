"""Enterprise Architecture - AI-Powered Architecture Design - Streamlit Application."""

import os
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from engines.ea_engine import design_architecture

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #283593 0%, #3949ab 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .layer-card { border-radius: 10px; padding: 1.2rem; margin-bottom: 0.8rem; }
    .layer-biz { background: #e8f5e9; border-left: 4px solid #2e7d32; }
    .layer-app { background: #e3f2fd; border-left: 4px solid #1565c0; }
    .layer-data { background: #fff3e0; border-left: 4px solid #e65100; }
    .layer-tech { background: #f3e5f5; border-left: 4px solid #7b1fa2; }
    .decision-card { background: #fafafa; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
        border-left: 4px solid #37474f; }
    .road-card { background: #e8eaf6; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
        border-left: 4px solid #3f51b5; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**EA4All** generates enterprise architecture blueprints following TOGAF "
            "methodology — business, application, data, and technology layers.")

st.markdown("""<div class="hero"><h1>EA4All - Enterprise Architecture</h1>
<p>Transform business requirements into structured architecture blueprints with TOGAF methodology</p></div>""",
unsafe_allow_html=True)

with st.form("ea_form"):
    requirements = st.text_area("Business Requirements", height=200,
        value="We need to modernise our customer onboarding platform:\n"
              "- Current system is a monolithic Java application (10+ years old)\n"
              "- Onboarding takes 5-7 business days, target is under 1 day\n"
              "- Need real-time identity verification and KYC checks\n"
              "- Must integrate with 3 legacy core banking systems\n"
              "- Mobile-first customer experience required\n"
              "- Must support 10,000 new customers/day during peak\n"
              "- Regulatory requirement: all data stays in-region (EU)\n"
              "- Need event-driven architecture for real-time status updates\n"
              "- AI/ML pipeline for fraud detection during onboarding")
    c1, c2 = st.columns(2)
    with c1:
        organisation = st.text_input("Organisation", value="NorthStar Bank (mid-tier European bank)")
        industry = st.selectbox("Industry",
            ["Banking & Financial Services", "Insurance", "Healthcare",
             "Retail", "Manufacturing", "Government", "Technology"])
    with c2:
        scale = st.selectbox("Scale",
            ["Small (< 100 users)", "Medium (100-1000 users)",
             "Large (1000-10000 users)", "Enterprise (10000+ users)"], index=2)
        current_state = st.text_input("Current State",
            value="Monolithic Java/Oracle stack, batch processing, limited API layer")
    constraints = st.text_input("Constraints",
        value="€2M budget, 12-month timeline, must maintain backward compatibility with core banking.")

    submitted = st.form_submit_button("Generate Architecture Blueprint", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(requirements=requirements, organisation=organisation, industry=industry,
                  scale=scale, current_state=current_state, constraints=constraints)

    with st.spinner("Designing architecture..."):
        try:
            result = design_architecture(config, api_key)
        except Exception as e:
            st.error(f"Design failed: {e}")
            st.stop()

    overview = result.get("architecture_overview", {})
    st.subheader(overview.get("project_name", "Architecture Blueprint"))
    st.markdown(f"**Style:** {overview.get('architecture_style', '')} | "
               f"**Maturity:** {overview.get('maturity_assessment', '')}")
    st.info(overview.get("target_state", ""))

    # Business Architecture
    biz = result.get("business_architecture", {})
    if biz:
        st.divider()
        st.markdown('<div class="layer-card layer-biz"><h3>Business Architecture</h3></div>',
                   unsafe_allow_html=True)
        caps = biz.get("capabilities", [])
        if caps:
            with st.expander(f"Business Capabilities ({len(caps)})"):
                for c in caps:
                    st.markdown(f"- **{c.get('capability', '')}** ({c.get('priority', '')}) — {c.get('description', '')}")
        for vs in biz.get("value_streams", []):
            with st.expander(f"Value Stream: {vs.get('stream', '')}"):
                st.markdown(f"Stages: {' → '.join(vs.get('stages', []))}")
                st.caption(f"Stakeholders: {', '.join(vs.get('stakeholders', []))}")
        for bp in biz.get("business_processes", []):
            with st.expander(f"Process: {bp.get('process', '')} (Automation: {bp.get('automation_potential', '')})"):
                for i, s in enumerate(bp.get("steps", []), 1):
                    st.markdown(f"{i}. {s}")

    # Application Architecture
    app = result.get("application_architecture", {})
    if app:
        st.divider()
        st.markdown('<div class="layer-card layer-app"><h3>Application Architecture</h3></div>',
                   unsafe_allow_html=True)
        apps = app.get("applications", [])
        if apps:
            app_df = pd.DataFrame([{
                "Application": a.get("name", ""), "Type": a.get("type", ""),
                "Layer": a.get("layer", ""), "Description": a.get("description", ""),
            } for a in apps])
            st.dataframe(app_df, use_container_width=True, hide_index=True)
        integ = app.get("integration_patterns", [])
        if integ:
            with st.expander("Integration Patterns"):
                for i in integ:
                    st.markdown(f"- **{i.get('source', '')}** → **{i.get('target', '')}** "
                               f"({i.get('pattern', '')}) — {i.get('description', '')}")

    # Data Architecture
    data = result.get("data_architecture", {})
    if data:
        st.divider()
        st.markdown('<div class="layer-card layer-data"><h3>Data Architecture</h3></div>',
                   unsafe_allow_html=True)
        domains = data.get("data_domains", [])
        if domains:
            dom_df = pd.DataFrame([{
                "Domain": d.get("domain", ""), "Owner": d.get("owner", ""),
                "Classification": d.get("classification", ""), "Storage": d.get("storage", ""),
            } for d in domains])
            st.dataframe(dom_df, use_container_width=True, hide_index=True)
        flows = data.get("data_flows", [])
        if flows:
            with st.expander("Data Flows"):
                for f in flows:
                    st.markdown(f"- {f.get('from', '')} → {f.get('to', '')} "
                               f"({f.get('frequency', '')}) — {f.get('data', '')}")

    # Technology Architecture
    tech = result.get("technology_architecture", {})
    if tech:
        st.divider()
        st.markdown('<div class="layer-card layer-tech"><h3>Technology Architecture</h3></div>',
                   unsafe_allow_html=True)
        platforms = tech.get("platforms", [])
        if platforms:
            for p in platforms:
                st.markdown(f"- **{p.get('platform', '')}** ({p.get('provider', '')}) — {p.get('purpose', '')}")

    # Architecture Decisions
    decisions = result.get("architecture_decisions", [])
    if decisions:
        st.divider()
        st.subheader("Architecture Decisions")
        for d in decisions:
            with st.expander(f"{d.get('decision', '')}: {d.get('title', '')}"):
                st.markdown(f"**Context:** {d.get('context', '')}")
                st.markdown(f"**Chosen:** {d.get('chosen', '')}")
                st.markdown(f"**Rationale:** {d.get('rationale', '')}")
                st.caption(f"Trade-offs: {d.get('trade_offs', '')}")

    # Roadmap
    roadmap = result.get("roadmap", [])
    if roadmap:
        st.divider()
        st.subheader("Implementation Roadmap")
        for r in roadmap:
            st.markdown(f'<div class="road-card"><strong>{r.get("phase", "")}</strong> '
                       f'({r.get("duration", "")})</div>', unsafe_allow_html=True)
            for d in r.get("deliverables", []):
                st.markdown(f"  - {d}")

    st.divider()
    st.download_button("Download Architecture Blueprint (JSON)", json.dumps(result, indent=2),
                       "architecture_blueprint.json", "application/json")
