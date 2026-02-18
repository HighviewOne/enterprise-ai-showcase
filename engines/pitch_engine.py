"""VC Pitch Generator engine - creates personalized investor pitch materials."""

import json
import anthropic

PITCH_PROMPT = """\
You are an expert venture capital pitch consultant who has helped hundreds of \
startups raise funding. Generate a comprehensive, personalized pitch deck outline \
and investor-specific talking points.

Return a JSON object:

{{
  "pitch_overview": {{
    "elevator_pitch": "2-3 sentence compelling elevator pitch",
    "tagline": "One catchy line that captures the company",
    "pitch_duration": "Recommended pitch duration based on stage",
    "key_narrative": "The core story arc for this pitch"
  }},

  "deck_slides": [
    {{
      "slide_number": <num>,
      "title": "Slide title",
      "key_points": ["bullet point 1", "bullet point 2", "bullet point 3"],
      "speaker_notes": "What to say while presenting this slide",
      "visual_suggestion": "Suggested graphic, chart, or visual for this slide",
      "time_allocation": "Seconds to spend on this slide"
    }}
  ],

  "investor_personalization": {{
    "thesis_alignment": "How the company aligns with the target investor's thesis",
    "portfolio_synergies": ["potential synergies with investor's other portfolio companies"],
    "tailored_hooks": ["specific angle that would resonate with this investor type"],
    "anticipated_concerns": [
      {{"concern": "What the investor might worry about", "response": "Prepared response"}}
    ]
  }},

  "financial_narrative": {{
    "revenue_story": "How to frame current/projected revenue",
    "unit_economics": "Key unit economics to highlight",
    "funding_ask_framing": "How to frame the ask and use of funds",
    "milestone_roadmap": [
      {{"milestone": "Key milestone", "timeline": "When", "impact": "Why it matters"}}
    ]
  }},

  "competitive_positioning": {{
    "market_map": "How to describe the competitive landscape",
    "differentiation_framework": "2x2 or positioning framework suggestion",
    "moat_narrative": "How to articulate the competitive moat",
    "why_now": "Why this is the right time for this company"
  }},

  "qa_prep": [
    {{
      "likely_question": "A question investors will likely ask",
      "strong_answer": "A compelling answer",
      "trap_to_avoid": "Common mistake founders make answering this"
    }}
  ],

  "pitch_tips": {{
    "opening_hook": "How to open the pitch memorably",
    "storytelling_elements": ["story or anecdote to weave in"],
    "closing_strategy": "How to end with a strong call to action",
    "body_language_tips": ["presentation delivery tips"],
    "common_mistakes": ["mistakes to avoid for this stage/type of pitch"]
  }}
}}

Generate a complete, professional pitch framework. Be specific and actionable.

IMPORTANT: Return ONLY the JSON object.

---

COMPANY PROFILE:
- Company Name: {company_name}
- Industry: {industry}
- Stage: {stage}
- Founded: {founded}
- Location: {location}
- Team Size: {team_size}
- Problem Statement: {problem}
- Solution: {solution}
- Traction: {traction}
- Revenue: {revenue}
- Funding Ask: {funding_ask}
- Use of Funds: {use_of_funds}
- Previous Funding: {previous_funding}

TARGET INVESTOR:
- Investor Type: {investor_type}
- Investment Thesis/Focus: {investor_focus}
- Typical Check Size: {check_size}

ADDITIONAL CONTEXT: {context}
"""


def generate_pitch(config: dict, api_key: str) -> dict:
    """Generate personalized investor pitch materials."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = PITCH_PROMPT.format(**config)
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    text = message.content[0].text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return json.loads(text)
