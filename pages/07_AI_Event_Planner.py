"""AI Event Planner - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.planner import generate_event_plan

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .venue-card { background: #f8f9fa; border-radius: 10px; padding: 1rem;
        border-top: 4px solid #a18cd1; margin-bottom: 0.5rem; }
    .vendor-card { background: #f0f7ff; border-radius: 8px; padding: 0.8rem;
        margin-bottom: 0.4rem; border-left: 4px solid #fbc2eb; }
    .timeline-item { background: #f8f9fa; border-radius: 8px; padding: 0.6rem 1rem;
        margin-bottom: 0.3rem; border-left: 4px solid #a18cd1; }
    .tip-card { background: #fff3cd; border-radius: 8px; padding: 0.8rem;
        margin-bottom: 0.4rem; border-left: 4px solid #ffc107; }
    .color-swatch { display: inline-block; width: 30px; height: 30px; border-radius: 50%;
        margin: 0.2rem; border: 2px solid #ddd; vertical-align: middle; }
    .tag { display: inline-block; background: #e9ecef; color: #495057;
        padding: 0.2rem 0.5rem; border-radius: 20px; margin: 0.1rem; font-size: 0.8rem; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input

st.markdown("""<div class="hero"><h1>AI Event Planner</h1>
<p>Turn your vision into a complete, actionable event plan in seconds</p></div>""",
unsafe_allow_html=True)

# ── Input Form ──
with st.form("event_form"):
    st.subheader("Event Details")
    e1, e2 = st.columns(2)
    with e1:
        event_type = st.selectbox("Event Type", [
            "Wedding", "Birthday Party", "Corporate Event", "Baby Shower",
            "Anniversary Celebration", "Graduation Party", "Holiday Party",
            "Fundraiser/Gala", "Conference", "Retirement Party", "Other"])
        location = st.text_input("City / Location", value="Austin, TX", placeholder="e.g., San Francisco, CA")
        event_date = st.date_input("Event Date")
        start_time = st.time_input("Start Time")
    with e2:
        style = st.selectbox("Style / Vibe", [
            "Elegant & Formal", "Casual & Relaxed", "Modern & Chic",
            "Rustic & Outdoor", "Fun & Playful", "Romantic & Intimate",
            "Glamorous & Luxurious", "Minimalist & Clean", "Themed/Costume"])
        st.markdown("**Guest Count**")
        gc1, gc2 = st.columns(2)
        with gc1:
            guest_min = st.number_input("Min", min_value=1, value=40, step=10)
        with gc2:
            guest_max = st.number_input("Max", min_value=1, value=60, step=10)
        st.markdown("**Budget Range ($)**")
        bc1, bc2 = st.columns(2)
        with bc1:
            budget_min = st.number_input("Min Budget", min_value=100, value=3_000, step=500)
        with bc2:
            budget_max = st.number_input("Max Budget", min_value=100, value=8_000, step=500)

    st.divider()
    st.subheader("Preferences")
    p1, p2, p3 = st.columns(3)
    with p1:
        must_haves = st.text_area("Must-Haves", value="Photographer, live music, custom cake",
                                   height=80, placeholder="e.g., DJ, photo booth, open bar")
    with p2:
        nice_to_haves = st.text_area("Nice-to-Haves", value="Photo booth, sparklers for send-off",
                                      height=80, placeholder="e.g., live band, themed decor")
    with p3:
        things_to_avoid = st.text_area("Things to Avoid", value="Buffet style food, overly loud music",
                                        height=80, placeholder="e.g., formal sit-down, no kids")

    d1, d2 = st.columns(2)
    with d1:
        dietary = st.text_input("Dietary Requirements", value="3 vegetarian, 1 gluten-free",
                                 placeholder="e.g., 5 vegan, 2 nut-free")
    with d2:
        additional_notes = st.text_area("Additional Notes", value="This is a surprise 30th birthday for my partner. Theme should be subtle gold and black.",
                                         height=80, placeholder="Any extra details...")

    submitted = st.form_submit_button("Plan My Event", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(
        event_type=event_type, location=location,
        event_date=str(event_date), start_time=str(start_time),
        guest_count_min=guest_min, guest_count_max=guest_max,
        budget_min=budget_min, budget_max=budget_max,
        style=style, must_haves=must_haves, nice_to_haves=nice_to_haves,
        things_to_avoid=things_to_avoid, dietary=dietary,
        additional_notes=additional_notes,
    )

    with st.spinner("Planning your perfect event..."):
        try:
            plan = generate_event_plan(config, api_key)
        except Exception as e:
            st.error(f"Planning failed: {e}")
            st.stop()

    # ── Results ──
    st.divider()
    st.header(f"🎉 {plan.get('event_name', 'Your Event Plan')}")
    if plan.get("theme_suggestion"):
        st.markdown(f"**Theme:** {plan['theme_suggestion']}")
    st.markdown(plan.get("executive_summary", ""))

    # Budget breakdown
    st.divider()
    st.subheader("Budget Breakdown")
    budget_items = plan.get("budget_breakdown", [])
    if budget_items:
        total = plan.get("total_estimated_cost", sum(b["estimated_cost"] for b in budget_items))
        st.metric("Total Estimated Cost", f"${total:,.0f}",
                   delta=f"Buffer: {plan.get('budget_buffer_pct', 10)}% recommended")

        fig = go.Figure(go.Pie(
            labels=[b["category"] for b in budget_items],
            values=[b["estimated_cost"] for b in budget_items],
            hole=0.4, textinfo="label+percent",
        ))
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

        df_budget = pd.DataFrame([{
            "Category": b["category"],
            "Cost": f"${b['estimated_cost']:,.0f}",
            "% of Budget": f"{b.get('percentage', 0)}%",
            "Notes": b.get("notes", ""),
        } for b in budget_items])
        st.dataframe(df_budget, use_container_width=True, hide_index=True)

    # Venue suggestions
    st.divider()
    st.subheader("Venue Suggestions")
    venues = plan.get("venue_suggestions", [])
    cols = st.columns(min(len(venues), 3)) if venues else []
    for i, venue in enumerate(venues):
        with cols[i % len(cols)]:
            pros = "".join(f'<span class="tag">{p}</span>' for p in venue.get("pros", []))
            st.markdown(f"""<div class="venue-card">
                <h4 style="margin:0;">{venue.get('name', '')}</h4>
                <small>{venue.get('type', '')} | {venue.get('capacity', '')} |
                ~${venue.get('estimated_cost', 0):,.0f}</small><br/>
                {pros}<br/>
                <small><em>{venue.get('best_for', '')}</em></small>
            </div>""", unsafe_allow_html=True)

    # Vendor recommendations
    st.divider()
    st.subheader("Vendor Guide")
    for v in plan.get("vendor_recommendations", []):
        st.markdown(f"""<div class="vendor-card">
            <strong>{v.get('category', '')}</strong> — {v.get('estimated_cost_range', '')}<br/>
            <em>Look for:</em> {v.get('what_to_look_for', '')}<br/>
            <small>Book: {v.get('booking_timeline', '')} | Tip: {v.get('tips', '')}</small>
        </div>""", unsafe_allow_html=True)

    # Menu
    st.divider()
    st.subheader("Menu Suggestions")
    for course in plan.get("menu_suggestions", []):
        with st.expander(f"{course.get('course', 'Course')}"):
            for opt in course.get("options", []):
                st.markdown(f"- {opt}")
            if course.get("dietary_notes"):
                st.info(course["dietary_notes"])

    # Decor
    decor = plan.get("decor_and_ambiance", {})
    if decor:
        st.divider()
        st.subheader("Decor & Ambiance")
        dc1, dc2 = st.columns(2)
        with dc1:
            if decor.get("color_palette"):
                st.markdown("**Color Palette:** " + ", ".join(decor["color_palette"]))
            if decor.get("key_elements"):
                for el in decor["key_elements"]:
                    st.markdown(f"- {el}")
        with dc2:
            if decor.get("lighting"):
                st.markdown(f"**Lighting:** {decor['lighting']}")
            if decor.get("music_vibe"):
                st.markdown(f"**Music/Entertainment:** {decor['music_vibe']}")

    # Timeline
    st.divider()
    st.subheader("Planning Timeline")
    timeline = plan.get("timeline", {})
    milestones = timeline.get("planning_milestones", [])
    if milestones:
        st.markdown("**Planning Milestones:**")
        for m in milestones:
            priority_color = {"Critical": "#dc3545", "High": "#fd7e14", "Medium": "#ffc107", "Low": "#28a745"}
            color = priority_color.get(m.get("priority", ""), "#6c757d")
            st.markdown(f"""<div class="timeline-item">
                <strong style="color:{color};">{m.get('weeks_before', '?')} weeks before</strong> —
                {m.get('task', '')} <small>[{m.get('priority', '')}]</small>
            </div>""", unsafe_allow_html=True)

    day_of = timeline.get("day_of_schedule", [])
    if day_of:
        st.markdown("**Day-Of Schedule:**")
        df_schedule = pd.DataFrame([{
            "Time": d.get("time", ""),
            "Activity": d.get("activity", ""),
            "Responsible": d.get("responsible", ""),
        } for d in day_of])
        st.dataframe(df_schedule, use_container_width=True, hide_index=True)

    # Guest experience
    guest_exp = plan.get("guest_experience", [])
    if guest_exp:
        st.divider()
        st.subheader("Guest Experience Journey")
        for i, touch in enumerate(guest_exp, 1):
            st.markdown(f"**{i}.** {touch}")

    # Checklist
    checklist = plan.get("checklist", [])
    if checklist:
        st.divider()
        st.subheader("Master Checklist")
        df_check = pd.DataFrame([{
            "Task": c.get("item", ""),
            "Category": c.get("category", ""),
            "Status": c.get("status", "To Do"),
        } for c in checklist])
        st.dataframe(df_check, use_container_width=True, hide_index=True)

    # Contingency
    contingency = plan.get("contingency_plans", [])
    if contingency:
        st.divider()
        st.subheader("Contingency Plans")
        for c in contingency:
            st.markdown(f"- **{c.get('risk', '')}** → {c.get('plan', '')}")

    # Pro tips
    tips = plan.get("pro_tips", [])
    if tips:
        st.divider()
        st.subheader("Pro Tips")
        for tip in tips:
            st.markdown(f"""<div class="tip-card">{tip}</div>""", unsafe_allow_html=True)

    # Export
    st.divider()
    col_ex1, col_ex2 = st.columns(2)
    with col_ex1:
        st.download_button("Download Full Plan (JSON)", json.dumps(plan, indent=2),
                           "event_plan.json", "application/json")
    with col_ex2:
        if checklist:
            csv = df_check.to_csv(index=False)
            st.download_button("Download Checklist (CSV)", csv, "event_checklist.csv", "text/csv")
