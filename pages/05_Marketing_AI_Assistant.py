"""Marketing AI Assistant for SMBs - Streamlit Application."""

import os
import json
import streamlit as st
from dotenv import load_dotenv

from engines.marketing_engine import (
    generate_social_posts,
    generate_email,
    generate_blog_outline,
    generate_campaign_plan,
    generate_personas,
)

load_dotenv()


st.markdown("""
<style>
    .hero {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem; border-radius: 12px; color: white;
        text-align: center; margin-bottom: 1.5rem;
    }
    .hero h1 { color: white; margin: 0; }
    .hero p { color: #f0e0e0; margin: 0.3rem 0 0 0; }
    .post-card {
        background: #f8f9fa; border-radius: 10px; padding: 1rem;
        margin-bottom: 0.8rem; border-left: 4px solid #f5576c;
    }
    .phase-card {
        background: #f0f7ff; border-radius: 8px; padding: 1rem;
        margin-bottom: 0.5rem; border-left: 4px solid #667eea;
    }
    .persona-card {
        background: #f8f9fa; border-radius: 10px; padding: 1.2rem;
        border-top: 4px solid #f5576c;
    }
    .tag {
        display: inline-block; background: #e9ecef; color: #495057;
        padding: 0.2rem 0.5rem; border-radius: 20px; margin: 0.1rem;
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar — Brand Config
api_key = os.getenv("ANTHROPIC_API_KEY", "")
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Anthropic API Key", value=api_key, type="password")
    if api_key_input:
        api_key = api_key_input

    st.divider()
    st.header("Brand Profile")
    business_name = st.text_input("Business Name", value="Bloom & Brew", placeholder="Your business name")
    industry = st.text_input("Industry", value="Coffee & Wellness", placeholder="e.g., E-commerce, SaaS, Retail")
    brand_voice = st.selectbox("Brand Voice", [
        "Professional & Trustworthy",
        "Friendly & Conversational",
        "Bold & Edgy",
        "Warm & Inspiring",
        "Fun & Playful",
        "Minimalist & Clean",
    ], index=1)
    target_audience = st.text_input("Target Audience", value="Health-conscious professionals aged 25-40",
                                     placeholder="Describe your ideal customer")

# Header
st.markdown("""
<div class="hero">
    <h1>Marketing AI Assistant</h1>
    <p>AI-powered content creation, campaign planning, and audience insights for SMBs</p>
</div>
""", unsafe_allow_html=True)

# Main tabs
tab_social, tab_email, tab_blog, tab_campaign, tab_persona = st.tabs([
    "Social Media", "Email Campaign", "Blog Content", "Campaign Planner", "Audience Personas"
])

# ── Social Media Tab ──
with tab_social:
    st.subheader("Social Media Post Generator")
    sc1, sc2 = st.columns(2)
    with sc1:
        platform = st.selectbox("Platform", ["Instagram", "LinkedIn", "Twitter/X", "Facebook", "TikTok"])
        topic = st.text_input("Topic or Product", value="New seasonal latte collection",
                               placeholder="What are you promoting?", key="social_topic")
    with sc2:
        goal = st.selectbox("Goal", ["Brand Awareness", "Drive Sales", "Engagement", "Traffic to Website", "Event Promotion"])
        count = st.slider("Number of Posts", 1, 5, 3)

    if st.button("Generate Posts", type="primary", key="gen_social"):
        if not api_key:
            st.error("API key required.")
        else:
            config = dict(platform=platform, topic=topic, goal=goal, count=count,
                         business_name=business_name, industry=industry,
                         brand_voice=brand_voice, target_audience=target_audience)
            with st.spinner(f"Creating {count} {platform} posts..."):
                try:
                    result = generate_social_posts(config, api_key)
                    if result.get("strategy_tip"):
                        st.info(f"Strategy Tip: {result['strategy_tip']}")
                    for i, post in enumerate(result.get("posts", []), 1):
                        st.markdown(f"""
                        <div class="post-card">
                            <strong>Post {i}</strong> ({post.get('content_type', 'Text')})<br/><br/>
                            {post.get('content', '')}<br/><br/>
                            <small>Hashtags: {' '.join('#' + h for h in post.get('hashtags', []))}</small><br/>
                            <small>Best time: {post.get('best_time', 'N/A')} | CTA: {post.get('cta', 'N/A')}</small>
                        </div>""", unsafe_allow_html=True)
                    st.download_button("Download Posts (JSON)", json.dumps(result, indent=2),
                                       "social_posts.json", "application/json")
                except Exception as e:
                    st.error(f"Generation failed: {e}")

# ── Email Tab ──
with tab_email:
    st.subheader("Email Campaign Generator")
    ec1, ec2 = st.columns(2)
    with ec1:
        campaign_type = st.selectbox("Campaign Type", [
            "Product Launch", "Newsletter", "Promotional Offer",
            "Re-engagement", "Welcome Series", "Event Invitation"])
        email_topic = st.text_input("Topic/Offer", value="20% off our new wellness teas",
                                     placeholder="What's the offer?", key="email_topic")
    with ec2:
        key_message = st.text_area("Key Message", value="Start your wellness journey with our curated tea collection.",
                                    height=100, placeholder="Core message...", key="email_msg")

    if st.button("Generate Email", type="primary", key="gen_email"):
        if not api_key:
            st.error("API key required.")
        else:
            config = dict(campaign_type=campaign_type, topic=email_topic, key_message=key_message,
                         business_name=business_name, industry=industry,
                         brand_voice=brand_voice, target_audience=target_audience)
            with st.spinner("Crafting your email..."):
                try:
                    result = generate_email(config, api_key)
                    st.markdown("**Subject Line Options:**")
                    for i, s in enumerate(result.get("subject_lines", []), 1):
                        st.markdown(f"{i}. {s}")
                    st.markdown(f"**Preview Text:** {result.get('preview_text', '')}")
                    st.markdown(f"**CTA:** {result.get('cta_text', '')}")
                    st.markdown(f"**Best Send Time:** {result.get('send_time_suggestion', '')}")
                    st.markdown(f"**A/B Test:** {result.get('a_b_test_suggestion', '')}")
                    st.divider()
                    st.markdown("**Email Preview:**")
                    st.markdown(result.get("body_html", ""), unsafe_allow_html=True)
                    with st.expander("Plain Text Version"):
                        st.text(result.get("body_plain", ""))
                    st.download_button("Download Email (JSON)", json.dumps(result, indent=2),
                                       "email_campaign.json", "application/json")
                except Exception as e:
                    st.error(f"Generation failed: {e}")

# ── Blog Tab ──
with tab_blog:
    st.subheader("Blog Content Generator")
    bc1, bc2 = st.columns(2)
    with bc1:
        blog_topic = st.text_input("Blog Topic", value="5 Morning Rituals to Boost Productivity",
                                    placeholder="What should the blog be about?", key="blog_topic")
    with bc2:
        keywords = st.text_input("Target Keywords", value="morning routine, productivity tips, wellness",
                                  placeholder="Comma-separated SEO keywords", key="blog_kw")

    if st.button("Generate Blog Outline", type="primary", key="gen_blog"):
        if not api_key:
            st.error("API key required.")
        else:
            config = dict(topic=blog_topic, keywords=keywords,
                         business_name=business_name, industry=industry,
                         brand_voice=brand_voice, target_audience=target_audience)
            with st.spinner("Building blog outline..."):
                try:
                    result = generate_blog_outline(config, api_key)
                    st.markdown(f"### {result.get('title', '')}")
                    st.markdown(f"**Meta Description:** {result.get('meta_description', '')}")
                    st.markdown(f"**Target Word Count:** {result.get('target_word_count', 'N/A')}")
                    st.divider()
                    st.markdown("**Introduction Draft:**")
                    st.markdown(result.get("introduction", ""))
                    st.divider()
                    st.markdown("**Outline:**")
                    for section in result.get("outline", []):
                        st.markdown(f"**{section.get('heading', '')}** (~{section.get('word_count_target', '?')} words)")
                        for pt in section.get("key_points", []):
                            st.markdown(f"  - {pt}")
                    st.markdown(f"**CTA:** {result.get('cta', '')}")
                    if result.get("internal_link_suggestions"):
                        tags = "".join(f'<span class="tag">{t}</span>' for t in result["internal_link_suggestions"])
                        st.markdown(f"**Internal Link Topics:** {tags}", unsafe_allow_html=True)
                    st.download_button("Download Outline (JSON)", json.dumps(result, indent=2),
                                       "blog_outline.json", "application/json")
                except Exception as e:
                    st.error(f"Generation failed: {e}")

# ── Campaign Planner Tab ──
with tab_campaign:
    st.subheader("Campaign Planner")
    cp1, cp2 = st.columns(2)
    with cp1:
        camp_goal = st.selectbox("Campaign Goal", [
            "Launch a new product", "Increase brand awareness", "Drive seasonal sales",
            "Grow email list", "Re-engage lapsed customers", "Event promotion"])
        budget = st.text_input("Budget", value="$2,000", placeholder="e.g., $5,000")
        duration = st.selectbox("Duration", ["1 week", "2 weeks", "1 month", "3 months"])
    with cp2:
        channels = st.multiselect("Channels", [
            "Instagram", "Facebook", "LinkedIn", "Twitter/X", "TikTok",
            "Email", "Google Ads", "Blog/SEO", "Influencer"], default=["Instagram", "Email", "Blog/SEO"])
        camp_message = st.text_area("Key Message", value="Discover our new wellness collection this spring.",
                                     height=80, key="camp_msg")

    if st.button("Generate Campaign Plan", type="primary", key="gen_campaign"):
        if not api_key:
            st.error("API key required.")
        else:
            config = dict(goal=camp_goal, budget=budget, duration=duration,
                         channels=", ".join(channels), key_message=camp_message,
                         business_name=business_name, industry=industry,
                         brand_voice=brand_voice, target_audience=target_audience)
            with st.spinner("Building your campaign strategy..."):
                try:
                    result = generate_campaign_plan(config, api_key)
                    st.markdown(f"### {result.get('campaign_name', 'Campaign Plan')}")
                    st.markdown(result.get("executive_summary", ""))

                    st.divider()
                    st.markdown("**Campaign Phases:**")
                    for phase in result.get("phases", []):
                        st.markdown(f"""
                        <div class="phase-card">
                            <strong>{phase.get('name', '')}</strong> — {phase.get('duration', '')}<br/>
                            Budget: {phase.get('budget_allocation', 'N/A')}<br/>
                            <em>Activities:</em> {', '.join(phase.get('activities', []))}<br/>
                            <em>KPIs:</em> {', '.join(phase.get('kpis', []))}
                        </div>""", unsafe_allow_html=True)

                    if result.get("budget_breakdown"):
                        st.divider()
                        st.markdown("**Budget Breakdown:**")
                        for ch, amt in result["budget_breakdown"].items():
                            st.markdown(f"- **{ch}:** {amt}")

                    if result.get("content_calendar"):
                        st.divider()
                        st.markdown("**Content Calendar:**")
                        import pandas as pd
                        df = pd.DataFrame(result["content_calendar"])
                        st.dataframe(df, use_container_width=True, hide_index=True)

                    if result.get("success_metrics"):
                        st.divider()
                        st.markdown("**Success Metrics:**")
                        for m in result["success_metrics"]:
                            st.markdown(f"- {m}")

                    st.download_button("Download Plan (JSON)", json.dumps(result, indent=2),
                                       "campaign_plan.json", "application/json")
                except Exception as e:
                    st.error(f"Generation failed: {e}")

# ── Audience Personas Tab ──
with tab_persona:
    st.subheader("Audience Persona Builder")
    pp1, pp2 = st.columns(2)
    with pp1:
        product = st.text_input("Product/Service", value="Artisan coffee and wellness teas",
                                 placeholder="What do you sell?", key="persona_prod")
    with pp2:
        current_customers = st.text_area("Current Customer Description",
            value="Urban professionals who value quality and health-conscious choices.",
            height=80, placeholder="Describe your existing customers...", key="persona_cust")

    if st.button("Generate Personas", type="primary", key="gen_persona"):
        if not api_key:
            st.error("API key required.")
        else:
            config = dict(product=product, current_customers=current_customers,
                         business_name=business_name, industry=industry)
            with st.spinner("Building audience personas..."):
                try:
                    result = generate_personas(config, api_key)
                    cols = st.columns(len(result.get("personas", [])))
                    for col, persona in zip(cols, result.get("personas", [])):
                        with col:
                            demo = persona.get("demographics", {})
                            psych = persona.get("psychographics", {})
                            behav = persona.get("behavior", {})
                            st.markdown(f"""<div class="persona-card">
                                <h3 style="margin:0;">{persona.get('name', 'Persona')}</h3>
                                <p><strong>Age:</strong> {demo.get('age_range', '')} |
                                <strong>Income:</strong> {demo.get('income', '')} |
                                <strong>Occupation:</strong> {demo.get('occupation', '')}</p>
                            </div>""", unsafe_allow_html=True)

                            st.markdown("**Pain Points:**")
                            for p in psych.get("pain_points", []):
                                st.markdown(f"- {p}")
                            st.markdown("**Goals:**")
                            for g in psych.get("goals", []):
                                st.markdown(f"- {g}")
                            st.markdown("**Preferred Channels:**")
                            tags = "".join(f'<span class="tag">{c}</span>' for c in behav.get("preferred_channels", []))
                            st.markdown(tags, unsafe_allow_html=True)
                            st.markdown("**Messaging Tips:**")
                            for t in persona.get("messaging_tips", []):
                                st.markdown(f"- {t}")
                    st.download_button("Download Personas (JSON)", json.dumps(result, indent=2),
                                       "audience_personas.json", "application/json")
                except Exception as e:
                    st.error(f"Generation failed: {e}")
