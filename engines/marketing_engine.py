"""Marketing AI engine - content generation, campaign planning, audience analysis."""

import json
import anthropic


def _call_claude(system: str, prompt: str, api_key: str, max_tokens: int = 2048) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


def _parse_json(text: str) -> dict:
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return json.loads(text)


# ── Content Creation ──

CONTENT_SYSTEM = """\
You are an expert marketing content creator for small and medium businesses.
You write compelling, on-brand content that drives engagement and conversions.
Always match the requested brand voice and target audience.
Keep content practical and ready to use with minimal editing."""

SOCIAL_PROMPT = """\
Create {count} social media posts for {platform}.

Business: {business_name}
Industry: {industry}
Brand Voice: {brand_voice}
Target Audience: {target_audience}
Topic/Product: {topic}
Goal: {goal}

Return a JSON object:
{{
  "posts": [
    {{
      "content": "The post text with emojis where appropriate",
      "hashtags": ["relevant", "hashtags"],
      "best_time": "Suggested posting time",
      "content_type": "Text | Image suggestion | Video suggestion | Carousel",
      "cta": "Call to action"
    }}
  ],
  "strategy_tip": "One sentence tip for maximizing engagement with these posts."
}}

Return ONLY JSON."""

EMAIL_PROMPT = """\
Write a marketing email campaign.

Business: {business_name}
Industry: {industry}
Brand Voice: {brand_voice}
Target Audience: {target_audience}
Campaign Type: {campaign_type}
Topic/Offer: {topic}
Key Message: {key_message}

Return a JSON object:
{{
  "subject_lines": ["Option 1", "Option 2", "Option 3"],
  "preview_text": "Preview text for email client",
  "body_html": "The full email body in clean HTML with inline styles",
  "body_plain": "Plain text version of the email",
  "cta_text": "Primary call-to-action button text",
  "send_time_suggestion": "Best time to send",
  "a_b_test_suggestion": "What to A/B test"
}}

Return ONLY JSON."""

BLOG_PROMPT = """\
Create a blog post outline with a draft introduction.

Business: {business_name}
Industry: {industry}
Brand Voice: {brand_voice}
Target Audience: {target_audience}
Topic: {topic}
Target Keywords: {keywords}

Return a JSON object:
{{
  "title": "SEO-optimized blog title",
  "meta_description": "155-character meta description",
  "outline": [
    {{"heading": "H2 heading", "key_points": ["point 1", "point 2"], "word_count_target": 200}}
  ],
  "introduction": "A compelling 150-word draft introduction",
  "target_word_count": 1200,
  "internal_link_suggestions": ["Topic areas to link to"],
  "cta": "End-of-post call to action"
}}

Return ONLY JSON."""


def generate_social_posts(config: dict, api_key: str) -> dict:
    prompt = SOCIAL_PROMPT.format(**config)
    response = _call_claude(CONTENT_SYSTEM, prompt, api_key)
    return _parse_json(response)


def generate_email(config: dict, api_key: str) -> dict:
    prompt = EMAIL_PROMPT.format(**config)
    response = _call_claude(CONTENT_SYSTEM, prompt, api_key)
    return _parse_json(response)


def generate_blog_outline(config: dict, api_key: str) -> dict:
    prompt = BLOG_PROMPT.format(**config)
    response = _call_claude(CONTENT_SYSTEM, prompt, api_key)
    return _parse_json(response)


# ── Campaign Planning ──

CAMPAIGN_PROMPT = """\
You are a marketing strategist for small businesses. Create a detailed campaign plan.

Business: {business_name}
Industry: {industry}
Budget: {budget}
Duration: {duration}
Goal: {goal}
Target Audience: {target_audience}
Channels: {channels}
Key Message: {key_message}

Return a JSON object:
{{
  "campaign_name": "Creative campaign name",
  "executive_summary": "2-3 sentence summary",
  "phases": [
    {{
      "name": "Phase name",
      "duration": "e.g., Week 1-2",
      "activities": ["Activity 1", "Activity 2"],
      "channels": ["Channel 1"],
      "budget_allocation": "e.g., 30%",
      "kpis": ["KPI 1", "KPI 2"]
    }}
  ],
  "content_calendar": [
    {{"week": 1, "channel": "Instagram", "content_type": "Post", "topic": "Topic", "goal": "Awareness"}}
  ],
  "budget_breakdown": {{"channel": "amount or percentage"}},
  "success_metrics": ["Metric 1 with target", "Metric 2 with target"],
  "risks_and_mitigations": [
    {{"risk": "Description", "mitigation": "How to handle"}}
  ]
}}

Return ONLY JSON."""


def generate_campaign_plan(config: dict, api_key: str) -> dict:
    prompt = CAMPAIGN_PROMPT.format(**config)
    response = _call_claude(CONTENT_SYSTEM, prompt, api_key, max_tokens=3000)
    return _parse_json(response)


# ── Audience Persona ──

PERSONA_PROMPT = """\
You are a marketing research expert. Build a detailed audience persona.

Business: {business_name}
Industry: {industry}
Product/Service: {product}
Current Customer Description: {current_customers}

Return a JSON object:
{{
  "personas": [
    {{
      "name": "Persona Name (e.g., 'Busy Beth')",
      "demographics": {{
        "age_range": "25-34",
        "gender": "Any",
        "location": "Urban areas",
        "income": "$50K-$80K",
        "education": "Bachelor's degree",
        "occupation": "Marketing manager"
      }},
      "psychographics": {{
        "values": ["value 1", "value 2"],
        "interests": ["interest 1", "interest 2"],
        "pain_points": ["pain 1", "pain 2"],
        "goals": ["goal 1", "goal 2"]
      }},
      "behavior": {{
        "preferred_channels": ["Instagram", "Email"],
        "content_preferences": ["Short-form video", "How-to guides"],
        "buying_triggers": ["trigger 1"],
        "objections": ["objection 1"]
      }},
      "messaging_tips": ["Tip 1 for reaching this persona", "Tip 2"]
    }}
  ]
}}

Generate 2-3 distinct personas. Return ONLY JSON."""


def generate_personas(config: dict, api_key: str) -> dict:
    prompt = PERSONA_PROMPT.format(**config)
    response = _call_claude(CONTENT_SYSTEM, prompt, api_key, max_tokens=3000)
    return _parse_json(response)
