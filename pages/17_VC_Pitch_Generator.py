"""VC Pitch Generator (Pitch Perfect) - Streamlit Application."""

import os
import json
import streamlit as st
from dotenv import load_dotenv

from engines.pitch_engine import generate_pitch

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #1b5e20 0%, #43a047 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .slide-card { background: #f8f9fa; border-radius: 10px; padding: 1.2rem;
        border-left: 4px solid #1b5e20; margin-bottom: 0.8rem; }
    .qa-card { background: #e8f5e9; border-radius: 8px; padding: 1rem;
        margin-bottom: 0.5rem; }
    .concern-card { background: #fff3e0; border-radius: 8px; padding: 0.8rem;
        border-left: 4px solid #ff9800; margin-bottom: 0.4rem; }
    .tip-card { background: #e3f2fd; border-radius: 8px; padding: 0.8rem;
        border-left: 4px solid #1976d2; margin-bottom: 0.4rem; }
    .milestone-badge { display: inline-block; background: #e8f5e9; color: #1b5e20;
        padding: 0.2rem 0.6rem; border-radius: 20px; margin: 0.1rem; font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input

st.markdown("""<div class="hero"><h1>Pitch Perfect</h1>
<p>AI-powered personalized investor pitch generator — tailored to your company and target investor</p></div>""",
unsafe_allow_html=True)

with st.form("pitch_form"):
    st.subheader("Company Profile")
    c1, c2, c3 = st.columns(3)
    with c1:
        company_name = st.text_input("Company Name", value="NovaByte AI")
        industry = st.selectbox("Industry",
            ["AI / Machine Learning", "SaaS / B2B Software", "Fintech", "HealthTech",
             "EdTech", "E-Commerce", "CleanTech / Climate", "Cybersecurity",
             "Developer Tools", "Consumer App", "Biotech", "Other"])
        stage = st.selectbox("Funding Stage",
            ["Pre-Seed", "Seed", "Series A", "Series B", "Series C+"])
    with c2:
        founded = st.text_input("Founded", value="2023")
        location = st.text_input("HQ Location", value="San Francisco, CA")
        team_size = st.text_input("Team Size", value="12 (8 engineers, 2 sales, CEO, CTO)")
    with c3:
        revenue = st.text_input("Current Revenue", value="$800K ARR, growing 25% MoM")
        funding_ask = st.text_input("Funding Ask", value="$5M Series Seed")
        previous_funding = st.text_input("Previous Funding", value="$1.2M pre-seed from angels")

    st.divider()
    p1, p2 = st.columns(2)
    with p1:
        problem = st.text_area("Problem Statement",
            value="Enterprise teams spend 40% of engineering time on data pipeline maintenance. "
                  "Existing ETL tools are brittle, require constant manual intervention, and "
                  "can't adapt to schema changes automatically.",
            height=100)
        solution = st.text_area("Your Solution",
            value="NovaByte AI provides self-healing data pipelines powered by LLMs that "
                  "automatically detect schema drift, fix broken transformations, and "
                  "optimize query performance — reducing pipeline maintenance by 80%.",
            height=100)
    with p2:
        traction = st.text_area("Traction / Key Metrics",
            value="15 enterprise customers (Stripe, Databricks, 2 Fortune 500). "
                  "NPS of 72. 95% retention rate. Pipeline from $800K to $2M ARR.",
            height=100)
        use_of_funds = st.text_area("Use of Funds",
            value="50% Engineering (hire 5 senior engineers), 30% Go-to-Market "
                  "(sales team expansion, marketing), 20% Operations & runway.",
            height=100)

    st.divider()
    st.subheader("Target Investor")
    i1, i2, i3 = st.columns(3)
    with i1:
        investor_type = st.selectbox("Investor Type",
            ["Tier 1 VC (a16z, Sequoia, etc.)", "Seed-Stage VC", "Growth-Stage VC",
             "Corporate VC (CVC)", "Angel Investor / Syndicate"])
    with i2:
        investor_focus = st.text_input("Investor's Focus / Thesis",
            value="AI-first developer tools and infrastructure plays, B2B SaaS")
    with i3:
        check_size = st.selectbox("Typical Check Size",
            ["$100K-$500K", "$500K-$2M", "$2M-$10M", "$10M-$50M", "$50M+"], index=2)

    context = st.text_input("Additional Context",
        value="This is a first meeting. Investor was warm-intro'd by a mutual portfolio founder.")

    submitted = st.form_submit_button("Generate Pitch Materials", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        company_name=company_name, industry=industry, stage=stage, founded=founded,
        location=location, team_size=team_size, problem=problem, solution=solution,
        traction=traction, revenue=revenue, funding_ask=funding_ask,
        use_of_funds=use_of_funds, previous_funding=previous_funding,
        investor_type=investor_type, investor_focus=investor_focus,
        check_size=check_size, context=context,
    )

    with st.spinner("Crafting your pitch materials..."):
        try:
            result = generate_pitch(config, api_key)
        except Exception as e:
            st.error(f"Generation failed: {e}")
            st.stop()

    # Pitch Overview
    overview = result.get("pitch_overview", {})
    st.subheader("Elevator Pitch")
    st.markdown(f"### *\"{overview.get('tagline', '')}\"*")
    st.markdown(overview.get("elevator_pitch", ""))
    st.caption(f"Recommended duration: {overview.get('pitch_duration', 'N/A')} | "
               f"Narrative: {overview.get('key_narrative', '')}")

    # Deck Slides
    slides = result.get("deck_slides", [])
    if slides:
        st.divider()
        st.subheader(f"Pitch Deck ({len(slides)} slides)")
        for slide in slides:
            with st.expander(f"Slide {slide.get('slide_number', '')} — {slide.get('title', '')}"
                           f" ({slide.get('time_allocation', '')})", expanded=False):
                st.markdown("**Key Points:**")
                for pt in slide.get("key_points", []):
                    st.markdown(f"- {pt}")
                st.markdown(f"**Speaker Notes:** {slide.get('speaker_notes', '')}")
                st.caption(f"Visual: {slide.get('visual_suggestion', '')}")

    # Investor Personalization
    inv = result.get("investor_personalization", {})
    if inv:
        st.divider()
        st.subheader("Investor-Specific Angles")
        st.info(f"**Thesis Alignment:** {inv.get('thesis_alignment', '')}")
        synergies = inv.get("portfolio_synergies", [])
        if synergies:
            st.markdown("**Portfolio Synergies:** " + " | ".join(synergies))
        hooks = inv.get("tailored_hooks", [])
        if hooks:
            for h in hooks:
                st.markdown(f'<div class="tip-card">{h}</div>', unsafe_allow_html=True)

        concerns = inv.get("anticipated_concerns", [])
        if concerns:
            st.markdown("**Anticipated Concerns & Responses:**")
            for c in concerns:
                st.markdown(f"""<div class="concern-card">
                    <strong>Concern:</strong> {c.get('concern', '')}<br/>
                    <strong>Response:</strong> {c.get('response', '')}
                </div>""", unsafe_allow_html=True)

    # Financial Narrative + Competitive Positioning
    fl, cr = st.columns(2)

    fin = result.get("financial_narrative", {})
    if fin:
        with fl:
            st.divider()
            st.subheader("Financial Story")
            st.markdown(f"**Revenue Story:** {fin.get('revenue_story', '')}")
            st.markdown(f"**Unit Economics:** {fin.get('unit_economics', '')}")
            st.markdown(f"**Funding Ask Framing:** {fin.get('funding_ask_framing', '')}")
            milestones = fin.get("milestone_roadmap", [])
            if milestones:
                st.markdown("**Milestone Roadmap:**")
                for m in milestones:
                    st.markdown(f'<span class="milestone-badge">{m.get("timeline", "")}</span> '
                               f'**{m.get("milestone", "")}** — {m.get("impact", "")}',
                               unsafe_allow_html=True)

    comp = result.get("competitive_positioning", {})
    if comp:
        with cr:
            st.divider()
            st.subheader("Competitive Positioning")
            st.markdown(f"**Market Map:** {comp.get('market_map', '')}")
            st.markdown(f"**Differentiation:** {comp.get('differentiation_framework', '')}")
            st.markdown(f"**Moat:** {comp.get('moat_narrative', '')}")
            st.success(f"**Why Now:** {comp.get('why_now', '')}")

    # Q&A Prep
    qa = result.get("qa_prep", [])
    if qa:
        st.divider()
        st.subheader("Q&A Preparation")
        for item in qa:
            st.markdown(f"""<div class="qa-card">
                <strong>Q: {item.get('likely_question', '')}</strong><br/>
                <strong>A:</strong> {item.get('strong_answer', '')}<br/>
                <small style="color:#d32f2f;">Trap to avoid: {item.get('trap_to_avoid', '')}</small>
            </div>""", unsafe_allow_html=True)

    # Pitch Tips
    tips = result.get("pitch_tips", {})
    if tips:
        st.divider()
        st.subheader("Presentation Tips")
        tc1, tc2 = st.columns(2)
        with tc1:
            st.markdown(f"**Opening Hook:** {tips.get('opening_hook', '')}")
            st.markdown(f"**Closing Strategy:** {tips.get('closing_strategy', '')}")
            for story in tips.get("storytelling_elements", []):
                st.markdown(f"- Story: {story}")
        with tc2:
            st.markdown("**Delivery Tips:**")
            for tip in tips.get("body_language_tips", []):
                st.markdown(f"- {tip}")
            st.markdown("**Mistakes to Avoid:**")
            for m in tips.get("common_mistakes", []):
                st.markdown(f"- {m}")

    # Export
    st.divider()
    st.download_button("Download Pitch Materials (JSON)", json.dumps(result, indent=2),
                       "pitch_materials.json", "application/json")
