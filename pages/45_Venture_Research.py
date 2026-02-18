"""Venture Research - Investment Screening & Research - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.vc_engine import screen_deal

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: #ffd54f; margin: 0; }
    .verdict-invest { background: #e8f5e9; border: 2px solid #2e7d32; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .verdict-pass { background: #ffebee; border: 2px solid #c62828; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .verdict-dd { background: #fff3e0; border: 2px solid #e65100; border-radius: 10px;
        padding: 1.5rem; text-align: center; }
    .risk-card { background: #f8f9fa; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem; }
    .risk-high { border-left: 4px solid #f44336; }
    .risk-medium { border-left: 4px solid #ff9800; }
    .risk-low { border-left: 4px solid #4caf50; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**VentureScope** screens startup deals and generates investment research "
            "briefs aligned with your fund's thesis.")

st.markdown("""<div class="hero"><h1>VentureScope</h1>
<p>AI-powered deal screening and investment research for venture capital</p></div>""",
unsafe_allow_html=True)

with st.form("vc_form"):
    startup_profile = st.text_area("Startup Profile / Business Plan", height=250,
        value="Company: NeuralChef AI\n"
              "Founded: 2023 | HQ: San Francisco, CA\n"
              "Stage: Seed | Raising: $3M on $12M pre-money\n\n"
              "Product: AI-powered kitchen management platform for restaurants. Uses computer\n"
              "vision to track inventory in real-time, predict demand, auto-generate prep lists,\n"
              "and reduce food waste by 30-40%.\n\n"
              "Team:\n"
              "- CEO: Former VP Engineering at DoorDash (7 years), CS PhD from Stanford\n"
              "- CTO: Ex-Google Brain researcher, published 12 papers on computer vision\n"
              "- COO: 15 years restaurant operations (managed 200+ locations for Darden Restaurants)\n\n"
              "Traction:\n"
              "- 18 months post-MVP launch\n"
              "- 45 restaurant locations live (mix of independent and small chains)\n"
              "- $380K ARR, growing 25% MoM for last 6 months\n"
              "- Net Revenue Retention: 135%\n"
              "- CAC: $2,800 | LTV: $18,000 (6.4x LTV/CAC)\n"
              "- Avg food waste reduction: 34% across customers\n"
              "- Monthly burn: $120K\n\n"
              "Competition: Winnow (UK, larger but hardware-heavy), Leanpath (legacy),\n"
              "Shelf Engine (demand forecasting only)\n\n"
              "Use of funds: Engineering (40%), Sales (35%), Operations (15%), G&A (10%)")
    c1, c2 = st.columns(2)
    with c1:
        fund_thesis = st.text_area("Fund Investment Thesis", height=100,
            value="We invest in B2B SaaS companies applying AI to transform traditional industries. "
                  "Focus on companies with strong unit economics, technical moats, and experienced "
                  "founding teams. Target 10x returns in 7-10 years.")
        stage_focus = st.selectbox("Stage Focus",
            ["Pre-seed", "Seed", "Series A", "Series B", "Growth"], index=1)
    with c2:
        check_size = st.text_input("Typical Check Size", value="$500K - $2M")
        sector_prefs = st.multiselect("Sector Preferences",
            ["Enterprise SaaS", "AI/ML", "FinTech", "HealthTech", "FoodTech",
             "CleanTech", "EdTech", "Marketplace", "DevTools"],
            default=["Enterprise SaaS", "AI/ML", "FoodTech"])

    submitted = st.form_submit_button("Screen Deal", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(startup_profile=startup_profile, fund_thesis=fund_thesis,
                  stage_focus=stage_focus, check_size=check_size,
                  sector_prefs=", ".join(sector_prefs))

    with st.spinner("Screening deal..."):
        try:
            result = screen_deal(config, api_key)
        except Exception as e:
            st.error(f"Screening failed: {e}")
            st.stop()

    # Deal Summary
    deal = result.get("deal_summary", {})
    st.subheader("Deal Summary")
    dm1, dm2, dm3, dm4 = st.columns(4)
    dm1.metric("Company", deal.get("company", ""))
    dm2.metric("Stage", deal.get("stage", ""))
    dm3.metric("Ask", deal.get("ask", ""))
    dm4.metric("Thesis Alignment", f"{deal.get('thesis_alignment', 0)}/10")

    # Verdict
    rec = result.get("investment_recommendation", {})
    verdict = rec.get("verdict", "Further Diligence")
    v_cls = ("verdict-invest" if verdict == "Invest" else "verdict-pass" if verdict == "Pass"
             else "verdict-dd")
    st.markdown(f'<div class="{v_cls}"><span style="font-size:1.5rem;font-weight:bold">'
               f'{verdict}</span> (Conviction: {rec.get("conviction_level", "")})<br/>'
               f'{deal.get("one_liner", "")}</div>', unsafe_allow_html=True)

    # Market & Team side by side
    mc1, mc2 = st.columns(2)
    market = result.get("market_analysis", {})
    if market:
        with mc1:
            st.divider()
            st.subheader("Market")
            st.markdown(f"**TAM:** {market.get('tam', '')}")
            st.markdown(f"**SAM:** {market.get('sam', '')}")
            st.markdown(f"**Growth:** {market.get('growth_rate', '')}")
            st.markdown(f"**Timing:** {market.get('timing_assessment', '')}")

    team = result.get("team_assessment", {})
    if team:
        with mc2:
            st.divider()
            st.subheader(f"Team (Score: {team.get('overall_score', 0)}/10)")
            for s in team.get("strengths", []):
                st.markdown(f"- {s}")
            if team.get("gaps"):
                st.markdown("**Gaps:**")
                for g in team["gaps"]:
                    st.warning(g)

    # Product & Business Model
    pc1, pc2 = st.columns(2)
    product = result.get("product_assessment", {})
    if product:
        with pc1:
            st.divider()
            st.subheader("Product")
            st.markdown(f"**Stage:** {product.get('stage', '')}")
            st.markdown(f"**Moat:** {product.get('moat', '')}")
            st.markdown(f"**Tech Risk:** {product.get('technology_risk', '')}")
            st.markdown(f"**Differentiation:** {product.get('differentiation', '')}")

    biz = result.get("business_model", {})
    if biz:
        with pc2:
            st.divider()
            st.subheader("Business Model")
            st.markdown(f"**Revenue Model:** {biz.get('revenue_model', '')}")
            st.markdown(f"**Unit Economics:** {biz.get('unit_economics', '')}")
            st.markdown(f"**Path to Profit:** {biz.get('path_to_profitability', '')}")

    # Competition
    comp = result.get("competitive_landscape", [])
    if comp:
        st.divider()
        st.subheader("Competitive Landscape")
        comp_df = pd.DataFrame([{
            "Competitor": c.get("competitor", ""),
            "Category": c.get("category", ""),
            "Position": c.get("relative_position", ""),
            "Differentiation": c.get("differentiation", ""),
        } for c in comp])
        st.dataframe(comp_df, use_container_width=True, hide_index=True)

    # Risk Factors
    risks = result.get("risk_factors", [])
    if risks:
        st.divider()
        st.subheader("Risk Factors")
        for r in risks:
            sev = r.get("severity", "Medium").lower()
            cls = f"risk-{sev}"
            st.markdown(f'<div class="risk-card {cls}"><strong>{r.get("risk", "")}</strong> '
                       f'({r.get("severity", "")})<br/>'
                       f'Mitigation: {r.get("mitigation", "")}</div>', unsafe_allow_html=True)

    # DD Questions
    questions = result.get("due_diligence_questions", [])
    if questions:
        st.divider()
        st.subheader("Due Diligence Questions")
        for q in questions:
            st.markdown(f"- {q}")

    # Investment Recommendation
    if rec:
        st.divider()
        st.subheader("Investment Recommendation")
        st.info(rec.get("rationale", ""))
        if rec.get("suggested_terms"):
            st.markdown(f"**Suggested Terms:** {rec['suggested_terms']}")
        if rec.get("exit_scenarios"):
            st.markdown("**Exit Scenarios:**")
            for e in rec["exit_scenarios"]:
                st.markdown(f"- {e}")

    st.divider()
    st.download_button("Download Investment Brief (JSON)", json.dumps(result, indent=2),
                       "investment_brief.json", "application/json")
