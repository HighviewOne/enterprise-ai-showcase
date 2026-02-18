"""Achieve AI - Your Habit Coach - Streamlit Application."""

import os
import json
from engines.datetime import datetime
import streamlit as st
from dotenv import load_dotenv

from engines.coach import get_coach_response

load_dotenv()


st.markdown("""
<style>
    .coach-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .coach-header h1 { color: white; margin: 0; }
    .coach-header p { color: #e0e0e0; margin: 0.3rem 0 0 0; }
    .framework-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 0.8rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid;
    }
    .fw-atomic { border-left-color: #28a745; }
    .fw-tiny { border-left-color: #17a2b8; }
    .fw-power { border-left-color: #fd7e14; }
    .habit-log {
        background: #f0f7ff;
        border-radius: 8px;
        padding: 0.8rem;
        margin-bottom: 0.3rem;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input

    st.divider()
    st.markdown("### Habit-Building Frameworks")
    st.markdown("""
    <div class="framework-card fw-atomic">
        <strong>Atomic Habits</strong><br/>
        <small>Small 1% daily improvements that compound. Four Laws of Behavior Change.</small>
    </div>
    <div class="framework-card fw-tiny">
        <strong>Tiny Habits</strong><br/>
        <small>Start ridiculously small. Anchor to existing routines. Celebrate immediately.</small>
    </div>
    <div class="framework-card fw-power">
        <strong>Power of Habit</strong><br/>
        <small>Cue-Routine-Reward loops. Change routines while keeping triggers and rewards.</small>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Habit tracker
    st.markdown("### Daily Check-In")
    if "habit_log" not in st.session_state:
        st.session_state["habit_log"] = []

    today = datetime.now().strftime("%Y-%m-%d")
    checked_today = any(e["date"] == today for e in st.session_state["habit_log"])

    if not checked_today:
        mood = st.select_slider("How are you feeling?", ["Struggling", "Okay", "Good", "Great", "Unstoppable"], value="Good")
        if st.button("Log Check-In"):
            st.session_state["habit_log"].append({"date": today, "mood": mood})
            # Add check-in as a chat message
            checkin_msg = f"Daily check-in: I'm feeling {mood.lower()} today."
            st.session_state["messages"].append({"role": "user", "content": checkin_msg})
            st.rerun()
    else:
        st.success(f"Checked in today!")

    # Show streak
    if st.session_state["habit_log"]:
        st.markdown(f"**Total check-ins:** {len(st.session_state['habit_log'])}")

    st.divider()
    if st.button("New Conversation", use_container_width=True):
        st.session_state["messages"] = []
        st.session_state["started"] = False
        st.rerun()

    # Export
    if st.session_state.get("messages"):
        export = json.dumps(st.session_state["messages"], indent=2)
        st.download_button("Export Chat", export, "habit_coach_chat.json", "application/json")


# Main area
st.markdown("""
<div class="coach-header">
    <h1>Achieve AI</h1>
    <p>Your personal habit coach powered by behavioral science</p>
</div>
""", unsafe_allow_html=True)

# Init session
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "started" not in st.session_state:
    st.session_state["started"] = False

# Welcome + goal selection
if not st.session_state["started"]:
    st.markdown("**Welcome!** Tell me about a habit you'd like to build (or break), and I'll create a personalized plan grounded in behavioral science.")
    st.markdown("")

    # Quick-start goal buttons
    cols = st.columns(4)
    goals = [
        ("Exercise regularly", cols[0]),
        ("Read more books", cols[1]),
        ("Better sleep routine", cols[2]),
        ("Build a morning routine", cols[3]),
    ]
    selected_goal = None
    for label, col in goals:
        if col.button(label, use_container_width=True):
            selected_goal = f"I want to {label.lower()}."

    custom_goal = st.chat_input("Or describe your habit goal...")

    goal = selected_goal or custom_goal
    if goal:
        if not api_key:
            st.error("Please add your Anthropic API key in the sidebar.")
            st.stop()
        st.session_state["started"] = True
        st.session_state["messages"].append({"role": "user", "content": goal})
        with st.spinner("Your coach is thinking..."):
            response = get_coach_response(st.session_state["messages"], api_key)
        st.session_state["messages"].append({"role": "assistant", "content": response})
        st.rerun()

else:
    # Display conversation
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"], avatar="🎯" if msg["role"] == "assistant" else None):
            st.markdown(msg["content"])

    # Chat input
    if user_input := st.chat_input("Type your message..."):
        if not api_key:
            st.error("API key required.")
            st.stop()

        st.session_state["messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar="🎯"):
            with st.spinner("Thinking..."):
                response = get_coach_response(st.session_state["messages"], api_key)
            st.markdown(response)
        st.session_state["messages"].append({"role": "assistant", "content": response})
