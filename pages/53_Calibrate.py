"""Calibrate - AI-Powered Job Search Leverage - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.calibrate_engine import analyze_career

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #4a148c 0%, #1a237e 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: #b388ff; margin: 0; }
    .fit-high { background: #e8f5e9; border: 2px solid #2e7d32; border-radius: 10px;
        padding: 1rem; margin-bottom: 0.5rem; }
    .fit-medium { background: #fff3e0; border: 2px solid #e65100; border-radius: 10px;
        padding: 1rem; margin-bottom: 0.5rem; }
    .fit-low { background: #ffebee; border: 2px solid #c62828; border-radius: 10px;
        padding: 1rem; margin-bottom: 0.5rem; }
    .identity-card { background: linear-gradient(135deg, #ede7f6 0%, #e8eaf6 100%);
        border-radius: 12px; padding: 1.5rem; text-align: center; margin-bottom: 1rem;
        border: 2px solid #7c4dff; }
    .gap-card { background: #f8f9fa; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem; }
    .gap-critical { border-left: 4px solid #f44336; }
    .gap-important { border-left: 4px solid #ff9800; }
    .gap-nice-to-have { border-left: 4px solid #4caf50; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**Calibrate** helps qualified professionals find roles where they're the obvious "
            "choice. Maps your strengths and aspirations to optimal opportunities.")

st.markdown("""<div class="hero"><h1>Calibrate</h1>
<p>Find the roles where you're the obvious choice, not the long shot</p></div>""",
unsafe_allow_html=True)

with st.form("calibrate_form"):
    professional_profile = st.text_area("Professional Profile", height=220,
        value="Senior Software Engineer with 9 years of experience\n\n"
              "Current: Senior Engineer at Stripe (3 years)\n"
              "- Tech lead for the Payments Infrastructure team (8 engineers)\n"
              "- Designed and shipped the real-time fraud detection pipeline processing 50M+ "
              "transactions/day\n"
              "- Reduced payment processing latency by 40% through architecture redesign\n"
              "- Mentored 5 engineers to promotion (3 to Senior, 2 to Staff)\n\n"
              "Previous: Software Engineer at Datadog (4 years)\n"
              "- Built core metrics aggregation engine handling 1T+ data points/day\n"
              "- Led migration from monolith to microservices (18 months, 0 downtime)\n"
              "- Open source contributor to OpenTelemetry\n\n"
              "Previous: Junior Engineer at a Series B startup (2 years)\n"
              "- Full-stack development, React + Python\n"
              "- Employee #12, experienced hyper-growth to 200 employees\n\n"
              "Education: BS Computer Science, UC Berkeley\n"
              "Skills: Go, Python, Rust, Kubernetes, AWS, distributed systems, "
              "system design, technical leadership\n"
              "Publications: 2 blog posts on distributed systems (10K+ reads each)")

    c1, c2 = st.columns(2)
    with c1:
        aspirations = st.text_area("Career Aspirations", height=100,
            value="I want to move into a Principal or Staff Engineer role where I can have "
                  "outsized technical impact. I'm passionate about building reliable, scalable "
                  "systems. Eventually interested in a VP of Engineering path but want 3-5 more "
                  "years of deep technical work first.")
        target_roles = st.text_input("Target Roles",
            value="Staff Engineer, Principal Engineer, Distinguished Engineer, Engineering Lead")
    with c2:
        location = st.text_input("Location Preference", value="San Francisco Bay Area (open to NYC)")
        salary_range = st.text_input("Target Salary Range", value="$280K - $400K total compensation")
        remote_preference = st.selectbox("Remote Preference",
            ["Fully Remote", "Hybrid (2-3 days)", "On-site Preferred", "Flexible"], index=1)

    unique_factors = st.text_area("What Makes You Unique?", height=100,
        value="I have a rare combination of deep infrastructure expertise AND startup experience. "
              "I've built systems at massive scale (Stripe, Datadog) but also know what it's like "
              "to wear many hats at a small company. I'm known for being the person who can take "
              "a vague, ambitious technical goal and turn it into a concrete plan that ships. "
              "I genuinely enjoy mentoring and have a track record of growing engineers.")

    submitted = st.form_submit_button("Calibrate My Career", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(professional_profile=professional_profile, aspirations=aspirations,
                  target_roles=target_roles, location=location, salary_range=salary_range,
                  remote_preference=remote_preference, unique_factors=unique_factors)

    with st.spinner("Calibrating your career positioning..."):
        try:
            result = analyze_career(config, api_key)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    # Professional Identity
    identity = result.get("professional_identity", {})
    if identity:
        st.markdown(f'<div class="identity-card"><span style="font-size:1.3rem;font-weight:bold">'
                   f'{identity.get("value_proposition", "")}</span><br/><br/>'
                   f'<em>{identity.get("career_narrative", "")}</em></div>', unsafe_allow_html=True)
        if identity.get("elevator_pitch"):
            st.info(f"**Elevator Pitch:** {identity['elevator_pitch']}")

    # Strength Mapping with Radar Chart
    strengths = result.get("strength_mapping", {})
    if strengths:
        st.divider()
        st.subheader("Strength Mapping")
        comps = strengths.get("core_competencies", [])
        if comps:
            # Plotly radar chart
            skills = [c.get("skill", "") for c in comps]
            scores = [c.get("proficiency", 5) for c in comps]
            if skills:
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=scores + [scores[0]],
                    theta=skills + [skills[0]],
                    fill="toself",
                    name="Your Profile",
                    line=dict(color="#7c4dff"),
                    fillcolor="rgba(124, 77, 255, 0.2)",
                ))
                # Add a reference line at 7 for "target role" benchmark
                fig.add_trace(go.Scatterpolar(
                    r=[7] * (len(skills) + 1),
                    theta=skills + [skills[0]],
                    name="Staff/Principal Benchmark",
                    line=dict(color="#ff9800", dash="dash"),
                ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                    title="Skills Radar: Your Profile vs Target Role",
                    height=450,
                )
                st.plotly_chart(fig, use_container_width=True)

            # Competencies table
            comp_df = pd.DataFrame([{
                "Skill": c.get("skill", ""),
                "Proficiency": f"{c.get('proficiency', 0)}/10",
                "Market Demand": c.get("market_demand", ""),
                "Evidence": c.get("evidence", ""),
            } for c in comps])
            st.dataframe(comp_df, use_container_width=True, hide_index=True)

        if strengths.get("hidden_strengths"):
            st.markdown("**Hidden Strengths (you may undervalue these):**")
            for h in strengths["hidden_strengths"]:
                st.success(h)

    # Market Positioning & Target Roles side by side
    mp1, mp2 = st.columns(2)
    market = result.get("market_positioning", {})
    if market:
        with mp1:
            st.divider()
            st.subheader("Market Positioning")
            st.markdown(f"**Current Tier:** {market.get('current_market_tier', '')}")
            st.markdown(f"**Optimal Positioning:** {market.get('optimal_positioning', '')}")
            st.markdown(f"**Market Demand:** {market.get('market_demand_level', '')}")
            st.markdown(f"**Supply:** {market.get('supply_assessment', '')}")
            st.markdown(f"**Timing:** {market.get('timing_assessment', '')}")
            if market.get("geographic_considerations"):
                st.info(market["geographic_considerations"])

    targets = result.get("target_role_analysis", [])
    if targets:
        with mp2:
            st.divider()
            st.subheader("Target Role Analysis")
            for t in targets:
                score = t.get("fit_score", 0)
                cls = "fit-high" if score >= 75 else "fit-medium" if score >= 50 else "fit-low"
                st.markdown(f'<div class="{cls}"><strong>{t.get("role_title", "")}</strong> '
                           f'(Fit: {score}/100)<br/>'
                           f'{t.get("why_good_fit", "")}<br/>'
                           f'<small>Comp: {t.get("compensation_range", "")} | '
                           f'Competition: {t.get("competition_level", "")}</small></div>',
                           unsafe_allow_html=True)

    # Company Archetypes
    archetypes = result.get("company_archetypes", [])
    if archetypes:
        st.divider()
        st.subheader("Company Archetypes That Need You")
        for a in archetypes:
            st.markdown(f"**{a.get('archetype', '')}** - {a.get('why_match', '')}")
            if a.get("example_companies"):
                st.markdown(f"Examples: {', '.join(a['example_companies'])}")
            if a.get("approach_strategy"):
                st.markdown(f"*Strategy: {a['approach_strategy']}*")

    # Narrative Strategy
    narrative = result.get("narrative_strategy", {})
    if narrative:
        st.divider()
        st.subheader("Narrative Strategy")
        if narrative.get("resume_headline"):
            st.markdown(f"**Resume Headline:** {narrative['resume_headline']}")
        if narrative.get("linkedin_summary_hook"):
            st.markdown(f"**LinkedIn Hook:** {narrative['linkedin_summary_hook']}")
        if narrative.get("story_themes"):
            st.markdown("**Interview Story Themes:**")
            for theme in narrative["story_themes"]:
                st.markdown(f"- {theme}")
        if narrative.get("achievement_framing"):
            st.markdown("**How to Frame Achievements:**")
            for frame in narrative["achievement_framing"]:
                st.markdown(f"- {frame}")

    # Application Priorities & Networking
    ap1, ap2 = st.columns(2)
    priorities = result.get("application_priorities", [])
    if priorities:
        with ap1:
            st.divider()
            st.subheader("Application Priorities")
            pri_df = pd.DataFrame([{
                "Priority": p.get("priority", ""),
                "Category": p.get("category", ""),
                "Effort": p.get("effort_level", ""),
                "Response Rate": p.get("expected_response_rate", ""),
                "Strategy": p.get("strategy", ""),
            } for p in priorities])
            st.dataframe(pri_df, use_container_width=True, hide_index=True)

    networking = result.get("networking_targets", [])
    if networking:
        with ap2:
            st.divider()
            st.subheader("Networking Targets")
            for n in networking:
                st.markdown(f"**{n.get('target_type', '')}**")
                st.markdown(f"{n.get('why_valuable', '')} | Find: {n.get('where_to_find', '')}")

    # Skills Gaps
    gaps = result.get("skills_gaps", [])
    if gaps:
        st.divider()
        st.subheader("Skills Gaps to Close")
        for g in gaps:
            imp = g.get("importance", "Important").lower().replace("-", "-")
            g_cls = f"gap-{imp}" if imp in ["critical", "important", "nice-to-have"] else "gap-important"
            st.markdown(f'<div class="gap-card {g_cls}"><strong>{g.get("gap", "")}</strong> '
                       f'({g.get("importance", "")})<br/>'
                       f'Investment: {g.get("investment", "")} | ROI: {g.get("roi", "")}</div>',
                       unsafe_allow_html=True)
            if g.get("resources"):
                st.markdown(f"Resources: {', '.join(g['resources'])}")

    # Salary Benchmarking
    salary = result.get("salary_benchmarking", {})
    if salary:
        st.divider()
        st.subheader("Salary Benchmarking")
        sa1, sa2 = st.columns(2)
        with sa1:
            st.markdown(f"**Current Market Rate:** {salary.get('current_market_rate', '')}")
            st.markdown(f"**Target Role Range:** {salary.get('target_role_range', '')}")
            if salary.get("geographic_adjustments"):
                st.info(salary["geographic_adjustments"])
        with sa2:
            if salary.get("negotiation_leverage"):
                st.markdown("**Negotiation Leverage:**")
                for lev in salary["negotiation_leverage"]:
                    st.markdown(f"- {lev}")
            if salary.get("total_comp_considerations"):
                st.markdown("**Total Comp Considerations:**")
                for tc in salary["total_comp_considerations"]:
                    st.markdown(f"- {tc}")

    # Action Plan
    plan = result.get("action_plan", {})
    if plan:
        st.divider()
        st.subheader("Action Plan")
        ap1, ap2 = st.columns(2)
        with ap1:
            if plan.get("week_1_2"):
                st.markdown("**Weeks 1-2:**")
                for a in plan["week_1_2"]:
                    st.markdown(f"- {a}")
            if plan.get("week_3_4"):
                st.markdown("**Weeks 3-4:**")
                for a in plan["week_3_4"]:
                    st.markdown(f"- {a}")
        with ap2:
            if plan.get("month_2"):
                st.markdown("**Month 2:**")
                for a in plan["month_2"]:
                    st.markdown(f"- {a}")
            if plan.get("month_3_plus"):
                st.markdown("**Month 3+:**")
                for a in plan["month_3_plus"]:
                    st.markdown(f"- {a}")
        if plan.get("daily_habits"):
            st.markdown("**Daily Habits:**")
            for h in plan["daily_habits"]:
                st.markdown(f"- {h}")

    st.divider()
    st.download_button("Download Career Strategy (JSON)", json.dumps(result, indent=2),
                       "career_strategy.json", "application/json")
