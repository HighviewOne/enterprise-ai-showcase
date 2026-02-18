"""Mental Health Support Companion - Streamlit Application."""

import os
import json
import streamlit as st
from dotenv import load_dotenv

from engines.companion import get_companion_response

load_dotenv()


st.markdown("""
<style>
    .hero { background: linear-gradient(135deg, #7b1fa2 0%, #ab47bc 100%);
        padding: 1.5rem; border-radius: 12px; color: white; text-align: center; margin-bottom: 1.5rem; }
    .hero h1 { color: white; margin: 0; }
    .crisis-box { background: #ffebee; border: 2px solid #f44336; border-radius: 10px;
        padding: 1rem; margin: 0.5rem 0; }
    .technique-card { background: #f3e5f5; border-radius: 8px; padding: 0.8rem;
        border-left: 4px solid #7b1fa2; margin: 0.3rem 0; cursor: pointer; }
    .mood-card { background: #e8f5e9; border-radius: 8px; padding: 0.8rem;
        text-align: center; }
</style>
""", unsafe_allow_html=True)

api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input

    st.divider()
    st.markdown("""<div class="crisis-box">
        <strong>Crisis Resources</strong><br/>
        <strong>988</strong> Suicide & Crisis Lifeline (call/text)<br/>
        Text <strong>HOME</strong> to <strong>741741</strong> (Crisis Text Line)<br/>
        <strong>911</strong> for emergencies
    </div>""", unsafe_allow_html=True)

    st.divider()
    st.warning("**Important:** This is an AI companion for educational purposes. "
               "It is NOT a substitute for professional mental health care. "
               "If you are in crisis, please use the resources above.")

    st.divider()
    st.subheader("Quick Techniques")
    techniques = {
        "5-4-3-2-1 Grounding": "Notice 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste.",
        "Box Breathing": "Inhale 4 seconds, hold 4 seconds, exhale 4 seconds, hold 4 seconds. Repeat 4 times.",
        "Thought Reframing": "Ask: What's the evidence for this thought? What would I tell a friend?",
        "Body Scan": "Starting from your toes, slowly move attention up through each body part, noticing sensations.",
    }
    for name, desc in techniques.items():
        st.markdown(f"""<div class="technique-card">
            <strong>{name}</strong><br/><small>{desc}</small>
        </div>""", unsafe_allow_html=True)

st.markdown("""<div class="hero"><h1>MindCare Companion</h1>
<p>A supportive AI companion using CBT & DBT techniques to help you navigate difficult moments</p></div>""",
unsafe_allow_html=True)

# Initialize chat
if "mh_messages" not in st.session_state:
    st.session_state.mh_messages = []
if "mood_log" not in st.session_state:
    st.session_state.mood_log = []

# Mood check-in
with st.expander("Daily Mood Check-in", expanded=len(st.session_state.mh_messages) == 0):
    mc1, mc2 = st.columns([2, 1])
    with mc1:
        mood_score = st.slider("How are you feeling right now? (1 = Very Low, 10 = Great)",
                                1, 10, 5)
        mood_note = st.text_input("Brief note about your mood (optional)",
                                   placeholder="e.g., Feeling anxious about work deadline")
    with mc2:
        feelings = st.multiselect("I'm feeling...",
            ["Anxious", "Sad", "Overwhelmed", "Angry", "Lonely",
             "Hopeful", "Calm", "Grateful", "Confused", "Tired",
             "Motivated", "Content"],
            default=["Anxious"])
    if st.button("Log Mood & Start Session"):
        entry = {"score": mood_score, "note": mood_note, "feelings": feelings}
        st.session_state.mood_log.append(entry)
        opening = (f"I'm feeling about a {mood_score}/10 right now. "
                   f"Emotions: {', '.join(feelings)}. "
                   f"{mood_note}" if mood_note else
                   f"I'm feeling about a {mood_score}/10 right now. Emotions: {', '.join(feelings)}.")
        st.session_state.mh_messages.append({"role": "user", "content": opening})
        with st.spinner("..."):
            reply = get_companion_response(st.session_state.mh_messages, api_key)
        st.session_state.mh_messages.append({"role": "assistant", "content": reply})
        st.rerun()

# Quick-start prompts
if not st.session_state.mh_messages:
    st.markdown("**Or start with a topic:**")
    qc1, qc2, qc3, qc4 = st.columns(4)
    starters = [
        ("I'm feeling stressed about work", qc1),
        ("I can't stop worrying", qc2),
        ("Help me with a breathing exercise", qc3),
        ("I want to build better habits", qc4),
    ]
    for text, col in starters:
        with col:
            if st.button(text, use_container_width=True):
                if not api_key:
                    st.error("API key required.")
                    st.stop()
                st.session_state.mh_messages.append({"role": "user", "content": text})
                with st.spinner("..."):
                    reply = get_companion_response(st.session_state.mh_messages, api_key)
                st.session_state.mh_messages.append({"role": "assistant", "content": reply})
                st.rerun()

# Chat display
for msg in st.session_state.mh_messages:
    with st.chat_message(msg["role"], avatar="🧠" if msg["role"] == "assistant" else None):
        st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Share what's on your mind..."):
    if not api_key:
        st.error("API key required.")
        st.stop()

    st.session_state.mh_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🧠"):
        with st.spinner("..."):
            reply = get_companion_response(st.session_state.mh_messages, api_key)
        st.markdown(reply)
    st.session_state.mh_messages.append({"role": "assistant", "content": reply})

# Sidebar actions
with st.sidebar:
    st.divider()
    if st.session_state.mh_messages:
        if st.button("Clear Conversation", use_container_width=True):
            st.session_state.mh_messages = []
            st.rerun()
        export = {
            "mood_log": st.session_state.mood_log,
            "conversation": st.session_state.mh_messages,
        }
        st.download_button("Export Session", json.dumps(export, indent=2),
                           "mindcare_session.json", "application/json",
                           use_container_width=True)
