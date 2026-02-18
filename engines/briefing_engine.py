"""Executive Briefing Writer engine - AI-enhanced executive briefs."""

import json
import anthropic

BRIEFING_PROMPT = """\
You are an expert executive communications specialist. Create a polished, data-driven \
executive briefing document from the provided data points, metrics, and context. The \
brief should be ready for C-suite review.

Return a JSON object:

{{
  "briefing_metadata": {{
    "title": "Briefing title",
    "date": "Date",
    "prepared_for": "Audience",
    "classification": "Confidential | Internal | General",
    "executive_summary": "2-3 sentence executive summary"
  }},

  "key_metrics": [
    {{"metric": "Metric name", "current_value": "Value", "previous_value": "Prior period",
      "change_pct": <number>, "trend": "Up | Down | Flat", "status": "On Track | At Risk | Off Track",
      "commentary": "Brief context"}}
  ],

  "strategic_highlights": [
    {{"topic": "Topic", "status": "Green | Yellow | Red",
      "summary": "What happened", "impact": "Business impact",
      "next_steps": "What's being done"}}
  ],

  "market_intelligence": {{
    "industry_trends": ["relevant market trends"],
    "competitive_moves": ["notable competitor actions"],
    "opportunities": ["identified opportunities"],
    "threats": ["emerging threats"]
  }},

  "team_highlights": [
    {{"team": "Department/team", "achievement": "Notable accomplishment",
      "challenge": "Current challenge", "outlook": "Forward-looking note"}}
  ],

  "risk_watch": [
    {{"risk": "Risk description", "likelihood": "High | Medium | Low",
      "impact": "High | Medium | Low", "owner": "Who's managing it",
      "mitigation": "What's being done"}}
  ],

  "decisions_needed": [
    {{"decision": "What needs to be decided", "context": "Background",
      "options": ["option 1", "option 2"], "recommendation": "Recommended path",
      "deadline": "When decision is needed"}}
  ],

  "action_items": [
    {{"action": "What needs to happen", "owner": "Responsible person/team",
      "deadline": "Due date", "priority": "High | Medium | Low"}}
  ],

  "closing_outlook": "Forward-looking closing paragraph"
}}

Write in a crisp, professional tone. Lead with insights, not data. Every metric \
should have context and a \"so what\" statement.

IMPORTANT: Return ONLY the JSON object.

---

INPUT DATA & CONTEXT:
{data}

BRIEFING PARAMETERS:
- Audience: {audience}
- Period: {period}
- Company/Division: {company}
- Focus Areas: {focus}
- Tone: {tone}
"""


def generate_briefing(config: dict, api_key: str) -> dict:
    """Generate executive briefing document."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = BRIEFING_PROMPT.format(**config)
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
