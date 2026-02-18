"""AI Property Search & Recommendation - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.search_engine import search_properties

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .listing-card { background: #f8f9fa; border-radius: 10px; padding: 1.2rem;
        border-top: 4px solid #00b894; margin-bottom: 0.8rem; }
    .match-badge { display: inline-block; padding: 0.3rem 0.8rem; border-radius: 20px;
        color: white; font-weight: bold; font-size: 0.9rem; }
    .hood-card { background: #f0faf8; border-radius: 8px; padding: 1rem;
        border-left: 4px solid #00cec9; margin-bottom: 0.5rem; }
    .tag { display: inline-block; background: #e9ecef; color: #495057;
        padding: 0.2rem 0.5rem; border-radius: 20px; margin: 0.1rem; font-size: 0.8rem; }
    .pro-tag { background: #d4edda; color: #155724; }
    .con-tag { background: #f8d7da; color: #721c24; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input

st.markdown("""<div class="hero"><h1>AI Property Search</h1>
<p>Tell us what you're looking for and get personalized property recommendations with market insights</p></div>""",
unsafe_allow_html=True)

with st.form("search_form"):
    c1, c2 = st.columns(2)
    with c1:
        location = st.text_input("Location", value="Austin, TX", placeholder="City, neighborhood, or zip code")
        search_type = st.selectbox("I want to...", ["Buy", "Rent"])
        st.markdown("**Budget Range**")
        b1, b2 = st.columns(2)
        with b1:
            budget_min = st.number_input("Min ($)", min_value=0,
                value=350_000 if search_type == "Buy" else 1_500, step=50_000 if search_type == "Buy" else 250)
        with b2:
            budget_max = st.number_input("Max ($)", min_value=0,
                value=550_000 if search_type == "Buy" else 3_000, step=50_000 if search_type == "Buy" else 250)
    with c2:
        bedrooms = st.selectbox("Bedrooms", ["1+", "2+", "3+", "4+", "5+"], index=1)
        bathrooms = st.selectbox("Bathrooms", ["1+", "1.5+", "2+", "2.5+", "3+"], index=2)
        min_sqft = st.number_input("Min Sq Ft", min_value=0, value=1200, step=200)
        property_types = st.multiselect("Property Types",
            ["House", "Condo", "Townhouse", "Apartment", "Multi-family"],
            default=["House", "Townhouse"])

    st.divider()
    p1, p2, p3 = st.columns(3)
    with p1:
        must_haves = st.text_area("Must-Haves", value="Garage, updated kitchen, good schools nearby",
                                   height=80, placeholder="e.g., pool, garage, yard")
    with p2:
        nice_to_haves = st.text_area("Nice-to-Haves", value="Home office, open floor plan, energy efficient",
                                      height=80, placeholder="e.g., view, fireplace")
    with p3:
        deal_breakers = st.text_area("Deal-Breakers", value="HOA over $400/month, flood zone",
                                      height=80, placeholder="e.g., busy road, no yard")

    lifestyle = st.multiselect("Lifestyle Priorities",
        ["Walkability", "Good Schools", "Nightlife & Dining", "Quiet & Suburban",
         "Public Transit", "Parks & Nature", "Short Commute", "Shopping & Amenities"],
        default=["Good Schools", "Quiet & Suburban", "Parks & Nature"])
    notes = st.text_area("Additional Notes", value="First-time homebuyer, working from home 3 days/week.",
                          height=60, placeholder="Any other details...")

    submitted = st.form_submit_button("Search Properties", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        location=location, search_type=search_type,
        budget_min=budget_min, budget_max=budget_max,
        bedrooms=bedrooms, bathrooms=bathrooms, min_sqft=min_sqft,
        property_types=", ".join(property_types),
        must_haves=must_haves, nice_to_haves=nice_to_haves,
        deal_breakers=deal_breakers, lifestyle=", ".join(lifestyle),
        notes=notes,
    )

    with st.spinner("Searching properties and analyzing the market..."):
        try:
            result = search_properties(config, api_key)
        except Exception as e:
            st.error(f"Search failed: {e}")
            st.stop()

    st.divider()
    st.markdown(f"**{result.get('search_summary', '')}**")

    # Market analysis
    market = result.get("market_analysis", {})
    if market:
        st.subheader("Market Snapshot")
        mk1, mk2, mk3, mk4 = st.columns(4)
        mk1.metric("Median Price", f"${market.get('median_price_area', 0):,.0f}")
        mk2.metric("Avg Days on Market", market.get("days_on_market_avg", "N/A"))
        mk3.metric("Market Type", market.get("market_type", "N/A"))
        mk4.metric("12-Month Trend", market.get("price_trend_12mo", "N/A"))
        st.info(f"**Agent Advice:** {market.get('advice', '')}")

    # Listings
    listings = result.get("listings", [])
    if listings:
        st.divider()
        st.subheader(f"Recommended Properties ({len(listings)})")
        sorted_listings = sorted(listings, key=lambda x: x.get("match_score", 0), reverse=True)

        for prop in sorted_listings:
            ms = prop.get("match_score", 0)
            badge_color = "#28a745" if ms >= 85 else "#ffc107" if ms >= 70 else "#17a2b8"
            features = "".join(f'<span class="tag">{f}</span>' for f in prop.get("features", []))
            pros = "".join(f'<span class="tag pro-tag">{p}</span>' for p in prop.get("pros", []))
            cons = "".join(f'<span class="tag con-tag">{c}</span>' for c in prop.get("cons", []))
            reasons = "".join(f'<span class="tag">{r}</span>' for r in prop.get("match_reasons", []))

            st.markdown(f"""<div class="listing-card">
                <span class="match-badge" style="background:{badge_color};">{ms}% Match</span>
                <h3 style="margin:0.5rem 0 0.2rem 0;">{prop.get('title', '')}</h3>
                <p style="margin:0; color:#666;">{prop.get('address', '')} — {prop.get('neighborhood', '')}</p>
                <h2 style="margin:0.3rem 0; color:#00b894;">${prop.get('price', 0):,.0f}</h2>
                <p style="margin:0;">{prop.get('bedrooms', 0)} bed | {prop.get('bathrooms', 0)} bath |
                    {prop.get('sqft', 0):,} sqft | Built {prop.get('year_built', 'N/A')} |
                    ${prop.get('price_per_sqft', 0):,.0f}/sqft |
                    Est. ${prop.get('estimated_monthly', 0):,.0f}/mo</p>
                <p>{features}</p>
                <p>Pros: {pros}</p>
                <p>Cons: {cons}</p>
                <small>Why it matches: {reasons}</small>
            </div>""", unsafe_allow_html=True)

        # Comparison table
        st.subheader("Property Comparison")
        df = pd.DataFrame([{
            "Property": p.get("title", "")[:40],
            "Price": f"${p.get('price', 0):,.0f}",
            "Bed": p.get("bedrooms"), "Bath": p.get("bathrooms"),
            "SqFt": f"{p.get('sqft', 0):,}",
            "$/SqFt": f"${p.get('price_per_sqft', 0):,.0f}",
            "Year": p.get("year_built"),
            "Monthly": f"${p.get('estimated_monthly', 0):,.0f}",
            "Match": f"{p.get('match_score', 0)}%",
        } for p in sorted_listings])
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Price comparison chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=[p.get("title", "")[:25] for p in sorted_listings],
            y=[p.get("price", 0) for p in sorted_listings],
            marker_color=[("#28a745" if p.get("match_score", 0) >= 85 else "#ffc107" if p.get("match_score", 0) >= 70 else "#17a2b8") for p in sorted_listings],
            text=[f"{p.get('match_score', 0)}%" for p in sorted_listings],
        ))
        fig.add_hline(y=budget_max, line_dash="dash", line_color="red", annotation_text="Max Budget")
        fig.update_layout(title="Price vs Match Score", height=350, yaxis_tickprefix="$")
        st.plotly_chart(fig, use_container_width=True)

    # Neighborhoods
    hoods = result.get("neighborhood_insights", [])
    if hoods:
        st.divider()
        st.subheader("Neighborhood Guide")
        for h in hoods:
            st.markdown(f"""<div class="hood-card">
                <strong>{h.get('name', '')}</strong> — <em>{h.get('vibe', '')}</em><br/>
                Walk Score: {h.get('walk_score', 'N/A')} | Transit: {h.get('transit_score', 'N/A')} |
                Schools: {h.get('school_rating', 'N/A')} | Median: ${h.get('median_price', 0):,.0f} |
                Trend: {h.get('price_trend', 'N/A')}<br/>
                <small>Best for: {h.get('best_for', '')}</small>
            </div>""", unsafe_allow_html=True)

    # Financial summary
    fin = result.get("financial_summary", {})
    if fin:
        st.divider()
        st.subheader("Financial Summary")
        st.markdown(f"**Budget Fit:** {fin.get('budget_fit', '')} | **Monthly Range:** {fin.get('monthly_range', '')}")
        if fin.get("down_payment_20pct"):
            st.markdown(f"**20% Down Payment:** ${fin['down_payment_20pct']:,.0f} | "
                       f"**Est. Closing Costs:** ${fin.get('closing_costs_est', 0):,.0f}")
        for tip in fin.get("tips", []):
            st.markdown(f"- {tip}")

    # Export
    st.divider()
    st.download_button("Download Results (JSON)", json.dumps(result, indent=2),
                       "property_search.json", "application/json")
