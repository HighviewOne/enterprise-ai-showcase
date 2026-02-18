"""Executive Briefing Writer - AI-Enhanced Executive Briefs - Streamlit Application."""

import os
import json
import streamlit as st
from dotenv import load_dotenv

from engines.briefing_engine import generate_briefing

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #1a237e 0%, #311b92 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .metric-up { color: #4caf50; font-weight: bold; }
    .metric-down { color: #f44336; font-weight: bold; }
    .metric-flat { color: #757575; font-weight: bold; }
    .highlight-card { background: #f8f9fa; border-radius: 10px; padding: 1.2rem; margin-bottom: 0.8rem; }
    .status-green { border-left: 4px solid #4caf50; }
    .status-yellow { border-left: 4px solid #ff9800; }
    .status-red { border-left: 4px solid #f44336; }
    .decision-card { background: #fff3e0; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
        border-left: 4px solid #e65100; }
    .action-card { background: #e3f2fd; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.4rem;
        border-left: 4px solid #1565c0; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**Executive Briefing Writer** transforms raw data and updates into polished, "
            "C-suite-ready briefing documents.")

st.markdown("""<div class="hero"><h1>Executive Briefing Writer</h1>
<p>Transform data, metrics, and updates into polished executive briefs ready for the boardroom</p></div>""",
unsafe_allow_html=True)

with st.form("brief_form"):
    data = st.text_area("Input Data & Updates", height=300,
        value="Q4 2024 Performance Data - NovaStar Technologies\n\n"
              "REVENUE: $28.4M (up 22% YoY, target was $27M)\n"
              "ARR: $112M (up from $94M last quarter)\n"
              "Gross Margin: 72% (down from 74% due to new infrastructure costs)\n"
              "Net Revenue Retention: 118%\n"
              "New Logos: 34 enterprise customers (target: 30)\n"
              "Churn: 2 mid-market accounts ($180K ARR lost)\n"
              "CAC Payback: 14 months (improved from 16)\n\n"
              "PRODUCT: Launched AI Analytics module in November - 60% adoption in first 6 weeks.\n"
              "Enterprise API v3 delayed to Q1 due to security audit findings.\n"
              "Customer satisfaction (NPS): 62 (up from 58).\n\n"
              "TEAM: Engineering headcount at 85 (hired 12 in Q4). VP Sales resigned Dec 15.\n"
              "Opened Singapore office with 8 initial hires.\n\n"
              "MARKET: Competitor DataPulse raised $80M Series C. Gartner included us in MQ.\n"
              "RISKS: AWS costs up 35% QoQ. Key customer Acme Corp exploring alternatives.\n"
              "DECISION NEEDED: Whether to pursue $5M strategic acquisition of WidgetML (AI startup).")

    c1, c2 = st.columns(2)
    with c1:
        audience = st.selectbox("Audience",
            ["CEO / Board", "C-Suite Leadership", "VP / Director Level",
             "All-Hands / Company-Wide", "Investors / Board of Directors"])
        company = st.text_input("Company / Division", value="NovaStar Technologies")
    with c2:
        period = st.text_input("Period", value="Q4 2024")
        tone = st.selectbox("Tone",
            ["Strategic & Forward-Looking", "Data-Driven & Analytical",
             "Concise & Action-Oriented", "Narrative & Contextual"])
    focus = st.text_input("Focus Areas",
        value="Revenue performance, product momentum, team changes, competitive landscape")

    submitted = st.form_submit_button("Generate Briefing", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()

    config = dict(data=data, audience=audience, period=period,
                  company=company, focus=focus, tone=tone)

    with st.spinner("Drafting executive briefing..."):
        try:
            result = generate_briefing(config, api_key)
        except Exception as e:
            st.error(f"Briefing generation failed: {e}")
            st.stop()

    # Metadata
    meta = result.get("briefing_metadata", {})
    st.subheader(meta.get("title", "Executive Briefing"))
    st.caption(f"{meta.get('date', '')} | {meta.get('prepared_for', '')} | {meta.get('classification', '')}")
    st.info(meta.get("executive_summary", ""))

    # Key Metrics
    metrics = result.get("key_metrics", [])
    if metrics:
        st.divider()
        st.subheader("Key Metrics")
        cols = st.columns(min(len(metrics), 4))
        for i, m in enumerate(metrics[:4]):
            with cols[i]:
                trend = m.get("trend", "Flat")
                change = m.get("change_pct", 0)
                arrow = "+" if change > 0 else ""
                st.metric(m.get("metric", ""), m.get("current_value", ""),
                         f"{arrow}{change}%" if isinstance(change, (int, float)) else str(change))
                status = m.get("status", "On Track")
                s_color = "#4caf50" if status == "On Track" else "#f44336" if status == "Off Track" else "#ff9800"
                st.markdown(f'<span style="color:{s_color};font-size:0.85rem">{status}</span>',
                           unsafe_allow_html=True)
        # Remaining metrics
        if len(metrics) > 4:
            cols2 = st.columns(min(len(metrics) - 4, 4))
            for i, m in enumerate(metrics[4:8]):
                with cols2[i]:
                    change = m.get("change_pct", 0)
                    arrow = "+" if isinstance(change, (int, float)) and change > 0 else ""
                    st.metric(m.get("metric", ""), m.get("current_value", ""),
                             f"{arrow}{change}%")
        for m in metrics:
            if m.get("commentary"):
                st.caption(f"**{m.get('metric', '')}:** {m['commentary']}")

    # Strategic Highlights
    highlights = result.get("strategic_highlights", [])
    if highlights:
        st.divider()
        st.subheader("Strategic Highlights")
        for h in highlights:
            status = h.get("status", "Yellow").lower()
            cls = f"status-{status}" if status in ("green", "yellow", "red") else "status-yellow"
            st.markdown(f'<div class="highlight-card {cls}"><strong>{h.get("topic", "")}</strong> '
                       f'[{h.get("status", "")}]<br/>{h.get("summary", "")}<br/>'
                       f'<em>Impact: {h.get("impact", "")}</em></div>', unsafe_allow_html=True)
            if h.get("next_steps"):
                st.caption(f"Next Steps: {h['next_steps']}")

    # Market Intelligence
    market = result.get("market_intelligence", {})
    if market:
        st.divider()
        st.subheader("Market Intelligence")
        mc1, mc2 = st.columns(2)
        with mc1:
            if market.get("industry_trends"):
                st.markdown("**Industry Trends:**")
                for t in market["industry_trends"]:
                    st.markdown(f"- {t}")
            if market.get("opportunities"):
                st.markdown("**Opportunities:**")
                for o in market["opportunities"]:
                    st.success(o)
        with mc2:
            if market.get("competitive_moves"):
                st.markdown("**Competitive Moves:**")
                for c in market["competitive_moves"]:
                    st.markdown(f"- {c}")
            if market.get("threats"):
                st.markdown("**Threats:**")
                for t in market["threats"]:
                    st.warning(t)

    # Team Highlights
    teams = result.get("team_highlights", [])
    if teams:
        st.divider()
        st.subheader("Team Highlights")
        for t in teams:
            with st.expander(t.get("team", "")):
                st.markdown(f"**Achievement:** {t.get('achievement', '')}")
                st.markdown(f"**Challenge:** {t.get('challenge', '')}")
                st.markdown(f"**Outlook:** {t.get('outlook', '')}")

    # Risk Watch
    risks = result.get("risk_watch", [])
    if risks:
        st.divider()
        st.subheader("Risk Watch")
        for r in risks:
            imp = r.get("impact", "Medium")
            icon = "🔴" if imp == "High" else "🟡" if imp == "Medium" else "🟢"
            st.markdown(f"{icon} **{r.get('risk', '')}** (Likelihood: {r.get('likelihood', '')}, "
                       f"Impact: {imp})")
            st.caption(f"Owner: {r.get('owner', '')} | Mitigation: {r.get('mitigation', '')}")

    # Decisions Needed
    decisions = result.get("decisions_needed", [])
    if decisions:
        st.divider()
        st.subheader("Decisions Needed")
        for d in decisions:
            st.markdown(f'<div class="decision-card"><strong>{d.get("decision", "")}</strong><br/>'
                       f'{d.get("context", "")}<br/>'
                       f'<strong>Recommendation:</strong> {d.get("recommendation", "")}<br/>'
                       f'<em>Deadline: {d.get("deadline", "")}</em></div>', unsafe_allow_html=True)
            if d.get("options"):
                for i, opt in enumerate(d["options"], 1):
                    st.markdown(f"  {i}. {opt}")

    # Action Items
    actions = result.get("action_items", [])
    if actions:
        st.divider()
        st.subheader("Action Items")
        for a in actions:
            pri = a.get("priority", "Medium")
            icon = "🔴" if pri == "High" else "🟡" if pri == "Medium" else "🟢"
            st.markdown(f'<div class="action-card">{icon} <strong>{a.get("action", "")}</strong><br/>'
                       f'Owner: {a.get("owner", "")} | Deadline: {a.get("deadline", "")}</div>',
                       unsafe_allow_html=True)

    # Closing
    outlook = result.get("closing_outlook", "")
    if outlook:
        st.divider()
        st.success(f"**Outlook:** {outlook}")

    st.divider()
    st.download_button("Download Briefing (JSON)", json.dumps(result, indent=2),
                       "executive_briefing.json", "application/json")
