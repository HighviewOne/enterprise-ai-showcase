"""Sports Stats Q&A - Natural Language Sports Statistics - Streamlit Application."""

import os
import json
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv

from engines.stats_engine import ask_stats

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: #ffd54f; margin: 0; }
    .hero p { color: #e0e0e0; }
    .answer-card { background: #f8f9fa; border-radius: 10px; padding: 1.5rem; margin-bottom: 1rem;
        border-left: 4px solid #2e7d32; }
    .context-card { background: #fff8e1; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
        border-left: 4px solid #f9a825; }
    .fun-fact { background: #e3f2fd; border-radius: 8px; padding: 1rem; margin-bottom: 0.5rem;
        border-left: 4px solid #1565c0; }
    .related-q { background: #f3e5f5; border-radius: 20px; padding: 0.4rem 1rem;
        display: inline-block; margin: 0.2rem; cursor: pointer; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input
    st.divider()
    st.info("**SportsMuse** answers your sports statistics questions in natural language. "
            "Ask about records, comparisons, career stats, and more!")
    st.divider()
    st.markdown("**Sample Questions:**")
    st.caption("- Who has the most Test centuries in cricket?")
    st.caption("- Compare LeBron and Jordan's career stats")
    st.caption("- Most World Cup goals in football history?")
    st.caption("- Who has the most Grand Slam titles in tennis?")

st.markdown("""<div class="hero"><h1>SportsMuse</h1>
<p>Ask any sports statistics question in plain English — get data, charts, and historical context</p></div>""",
unsafe_allow_html=True)

with st.form("stats_form"):
    question = st.text_input("Ask a sports question",
        value="Who are the top 5 run scorers in cricket Test matches of all time? Compare their averages and centuries.")
    c1, c2 = st.columns(2)
    with c1:
        sport = st.selectbox("Sport",
            ["Auto-detect", "Cricket", "Baseball", "Basketball", "Football (Soccer)",
             "American Football", "Tennis", "Golf", "Formula 1", "Olympics"])
    with c2:
        context = st.text_input("Additional Context (optional)",
            value="Include their career span and country",
            placeholder="e.g., focus on a specific era, league, or player...")
    submitted = st.form_submit_button("Get Answer", type="primary", use_container_width=True)

if submitted:
    if not api_key:
        st.error("API key required.")
        st.stop()
    if not question.strip():
        st.error("Please enter a question.")
        st.stop()

    config = dict(sport=sport, question=question, context=context)

    with st.spinner("Looking up stats..."):
        try:
            result = ask_stats(config, api_key)
        except Exception as e:
            st.error(f"Query failed: {e}")
            st.stop()

    # Answer
    answer = result.get("answer", {})
    st.markdown(f'<div class="answer-card"><strong>Answer:</strong><br/>{answer.get("text", "")}</div>',
                unsafe_allow_html=True)
    conf = answer.get("confidence", "Medium")
    conf_color = "#4caf50" if conf == "High" else "#f44336" if conf == "Low" else "#ff9800"
    st.markdown(f'Confidence: <span style="color:{conf_color};font-weight:bold">{conf}</span>',
                unsafe_allow_html=True)

    # Stats Table
    stats = result.get("stats_table", [])
    if stats:
        st.divider()
        st.subheader("Statistics")
        df = pd.DataFrame(stats)
        st.dataframe(df, use_container_width=True, hide_index=True)

    # Visualisation
    viz = result.get("visualisation", {})
    if viz and viz.get("type") != "none" and viz.get("data"):
        st.divider()
        st.subheader(viz.get("title", "Chart"))
        data = viz["data"]
        labels = [d.get("label", "") for d in data]
        values = [d.get("value", 0) for d in data]

        chart_type = viz.get("type", "bar")
        if chart_type == "bar":
            fig = go.Figure(go.Bar(x=labels, y=values, marker_color="#2e7d32",
                                    text=values, textposition="outside"))
            fig.update_layout(xaxis_title=viz.get("x_label", ""),
                            yaxis_title=viz.get("y_label", ""), height=350)
        elif chart_type == "pie":
            fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.4))
            fig.update_layout(height=350)
        elif chart_type == "line":
            fig = go.Figure(go.Scatter(x=labels, y=values, mode="lines+markers",
                                       line_color="#1565c0"))
            fig.update_layout(xaxis_title=viz.get("x_label", ""),
                            yaxis_title=viz.get("y_label", ""), height=350)
        else:
            fig = go.Figure(go.Bar(x=labels, y=values, marker_color="#2e7d32"))
            fig.update_layout(height=350)

        st.plotly_chart(fig, use_container_width=True)

    # Context
    ctx = result.get("context", {})
    if ctx:
        st.divider()
        st.subheader("Context & Trivia")
        if ctx.get("historical_note"):
            st.markdown(f'<div class="context-card"><strong>Historical Note:</strong> '
                       f'{ctx["historical_note"]}</div>', unsafe_allow_html=True)
        if ctx.get("comparison"):
            st.markdown(f'<div class="context-card"><strong>Comparison:</strong> '
                       f'{ctx["comparison"]}</div>', unsafe_allow_html=True)
        if ctx.get("fun_fact"):
            st.markdown(f'<div class="fun-fact"><strong>Fun Fact:</strong> '
                       f'{ctx["fun_fact"]}</div>', unsafe_allow_html=True)

    # Related Questions
    related = result.get("related_questions", [])
    if related:
        st.divider()
        st.subheader("You Might Also Ask")
        for q in related:
            st.markdown(f'<span class="related-q">{q}</span>', unsafe_allow_html=True)

    # Source Note
    src = answer.get("data_source_note") or result.get("sources_note", "")
    if src:
        st.caption(f"Note: {src}")

    st.divider()
    st.download_button("Download Answer (JSON)", json.dumps(result, indent=2),
                       "sports_stats.json", "application/json")
