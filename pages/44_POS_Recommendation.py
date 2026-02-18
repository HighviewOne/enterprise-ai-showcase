"""POS Recommendation - Payment System Guidance for SMBs - Streamlit Application."""

import os
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from engines.pos_engine import recommend_pos

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #1b5e20 0%, #388e3c 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .rec-card { background: #f8f9fa; border-radius: 10px; padding: 1.2rem; margin-bottom: 0.8rem; }
    .rec-1 { border-left: 4px solid #ffd700; }
    .rec-2 { border-left: 4px solid #c0c0c0; }
    .rec-3 { border-left: 4px solid #cd7f32; }
    .rec-other { border-left: 4px solid #9e9e9e; }
    .step-card { background: #e3f2fd; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
        border-left: 4px solid #1565c0; }
    .glossary-card { background: #fff3e0; border-radius: 8px; padding: 0.6rem; margin-bottom: 0.3rem; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**PosPal** helps small businesses understand payment systems and choose "
            "the right POS solution — in plain, simple language.")

st.markdown("""<div class="hero"><h1>PosPal - POS Recommendation Engine</h1>
<p>Find the perfect payment system for your business — clear costs, honest comparisons, no jargon</p></div>""",
unsafe_allow_html=True)

with st.form("pos_form"):
    merchant_details = st.text_area("Tell Us About Your Business", height=150,
        value="Family-owned Italian restaurant in Brooklyn, NY. Been open 8 years.\n"
              "20 tables for dine-in, plus takeout and a growing delivery business.\n"
              "We currently use an old cash register and a separate credit card terminal.\n"
              "We want to modernise — need table-side ordering, online ordering, inventory\n"
              "tracking, and tip management. Staff of 12 (mix of servers and kitchen).\n"
              "Not very tech-savvy but willing to learn. Budget-conscious.")
    c1, c2 = st.columns(2)
    with c1:
        business_type = st.selectbox("Business Type",
            ["Restaurant (Full Service)", "Restaurant (Quick Service/Fast Food)",
             "Cafe/Coffee Shop", "Retail Store", "Food Truck/Cart",
             "Salon/Spa", "Professional Services", "Bar/Nightclub"])
        monthly_volume = st.text_input("Estimated Monthly Sales", value="$45,000")
    with c2:
        avg_transaction = st.text_input("Average Transaction Size", value="$35")
        priorities = st.multiselect("Top Priorities",
            ["Low Cost", "Easy to Use", "Online Ordering", "Inventory Management",
             "Employee Management", "Delivery Integration", "Loyalty Program",
             "Multi-location Support", "Tableside Ordering", "Tip Management"],
            default=["Easy to Use", "Online Ordering", "Tableside Ordering", "Tip Management"])
    current_setup = st.text_input("Current Payment Setup",
        value="Cash register + standalone Verifone credit card terminal (processing through Chase)")

    submitted = st.form_submit_button("Get Recommendations", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        merchant_details=merchant_details, business_type=business_type,
        monthly_volume=monthly_volume, avg_transaction=avg_transaction,
        priorities=", ".join(priorities), current_setup=current_setup,
    )

    with st.spinner("Finding the best POS systems for you..."):
        try:
            result = recommend_pos(config, api_key)
        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()

    # Merchant Profile
    profile = result.get("merchant_profile", {})
    st.subheader("Your Business Profile")
    pm1, pm2, pm3 = st.columns(3)
    pm1.metric("Business Type", profile.get("business_type", ""))
    pm2.metric("Size", profile.get("size_category", ""))
    pm3.metric("Complexity", profile.get("complexity_level", ""))

    # Recommendations
    recs = result.get("recommendations", [])
    if recs:
        st.divider()
        st.subheader("Top Recommendations")
        for r in recs:
            rank = r.get("rank", 99)
            cls = f"rec-{rank}" if rank <= 3 else "rec-other"
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")
            st.markdown(f'<div class="rec-card {cls}">'
                       f'{medal} <strong>{r.get("system", "")}</strong> — '
                       f'Score: {r.get("best_fit_score", 0)}/100<br/>'
                       f'{r.get("best_for", "")}<br/>'
                       f'Monthly: {r.get("monthly_cost", "")} | Fees: {r.get("transaction_fees", "")} | '
                       f'First Year: ~{r.get("total_first_year_estimate", "")}</div>',
                       unsafe_allow_html=True)
            with st.expander(f"Details: {r.get('system', '')}"):
                dc1, dc2 = st.columns(2)
                with dc1:
                    st.markdown("**Pros:**")
                    for p in r.get("pros", []):
                        st.markdown(f"- {p}")
                with dc2:
                    st.markdown("**Cons:**")
                    for c in r.get("cons", []):
                        st.markdown(f"- {c}")
                st.markdown(f"**Hardware:** {r.get('hardware_cost', '')}")
                st.markdown(f"**Contract:** {r.get('contract_terms', '')}")
                st.markdown(f"**Setup:** {r.get('setup_difficulty', '')}")

    # Feature Comparison
    features = result.get("feature_comparison", [])
    if features:
        st.divider()
        st.subheader("Feature Comparison")
        feat_df = pd.DataFrame(features)
        st.dataframe(feat_df, use_container_width=True, hide_index=True)

    # Cost Analysis
    costs = result.get("cost_analysis", {})
    if costs:
        st.divider()
        st.subheader("Cost Analysis")
        st.markdown(f"**Based on monthly volume:** {costs.get('monthly_volume_estimate', '')}")
        comp = costs.get("cost_comparison", [])
        if comp:
            cost_df = pd.DataFrame(comp)
            st.dataframe(cost_df, use_container_width=True, hide_index=True)
        hidden = costs.get("hidden_costs_warning", [])
        if hidden:
            st.markdown("**Watch Out For:**")
            for h in hidden:
                st.warning(h)

    # Implementation Guide
    guide = result.get("implementation_guide", [])
    if guide:
        st.divider()
        st.subheader("Setup Guide")
        for s in guide:
            st.markdown(f'<div class="step-card"><strong>Step {s.get("step", "")}:</strong> '
                       f'{s.get("action", "")} ({s.get("timeline", "")})</div>',
                       unsafe_allow_html=True)
            if s.get("tips"):
                st.caption(f"Tip: {s['tips']}")

    # Glossary
    glossary = result.get("glossary", [])
    if glossary:
        st.divider()
        with st.expander("Payment Terms Glossary"):
            for g in glossary:
                st.markdown(f'<div class="glossary-card"><strong>{g.get("term", "")}</strong>: '
                           f'{g.get("definition", "")}</div>', unsafe_allow_html=True)

    # Final Recommendation
    final = result.get("final_recommendation", "")
    if final:
        st.divider()
        st.success(f"**Our Recommendation:** {final}")

    st.divider()
    st.download_button("Download Report (JSON)", json.dumps(result, indent=2),
                       "pos_recommendation.json", "application/json")
