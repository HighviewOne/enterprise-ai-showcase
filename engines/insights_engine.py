"""Customer Insights Engine - Unified customer understanding from multiple sources."""

import json
import anthropic

INSIGHTS_PROMPT = """\
You are an expert customer insights analyst. Synthesise fragmented customer data from \
CRM records, support tickets, call transcripts, and survey responses into a unified, \
actionable customer intelligence report.

Return a JSON object:

{{
  "customer_overview": {{
    "total_data_points": <number>,
    "time_span": "Period covered",
    "key_insight": "Most important finding",
    "sentiment_trend": "Improving | Stable | Declining"
  }},

  "themes": [
    {{
      "theme": "Theme name",
      "frequency": <count or percentage>,
      "sentiment": "Positive | Neutral | Negative | Mixed",
      "evidence": ["direct quotes or data points"],
      "business_impact": "How this affects the business",
      "recommended_action": "What to do about it"
    }}
  ],

  "customer_segments": [
    {{
      "segment": "Segment name",
      "size": "Relative size or count",
      "characteristics": ["defining traits"],
      "needs": ["what they want"],
      "pain_points": ["what frustrates them"],
      "retention_risk": "High | Medium | Low",
      "opportunity": "Growth opportunity with this segment"
    }}
  ],

  "sentiment_analysis": {{
    "overall_score": <1-10>,
    "positive_drivers": ["what customers love"],
    "negative_drivers": ["what customers dislike"],
    "neutral_topics": ["areas of indifference"],
    "trending_topics": ["emerging themes"]
  }},

  "competitive_intelligence": {{
    "competitor_mentions": [
      {{"competitor": "Name", "context": "Why mentioned", "sentiment": "Positive | Negative"}}
    ],
    "switching_risk_factors": ["why customers might leave"],
    "loyalty_drivers": ["why customers stay"]
  }},

  "product_feedback": [
    {{"feature_area": "Product area", "feedback_type": "Request | Complaint | Praise",
      "frequency": <count>, "summary": "Consolidated feedback",
      "priority": "High | Medium | Low"}}
  ],

  "churn_signals": [
    {{"signal": "Warning sign", "affected_segment": "Who's at risk",
      "urgency": "Immediate | Near-term | Watch", "intervention": "Recommended action"}}
  ],

  "strategic_recommendations": [
    {{"recommendation": "What to do", "expected_impact": "Business outcome",
      "effort": "Low | Medium | High", "timeline": "When to implement",
      "supporting_data": "Evidence basis"}}
  ],

  "executive_brief": "3-4 sentence executive summary for leadership"
}}

Be data-driven and cite specific evidence. Distinguish between anecdotal and systemic issues.

IMPORTANT: Return ONLY the JSON object.

---

CUSTOMER DATA:
{customer_data}

ANALYSIS PARAMETERS:
- Company: {company}
- Product/Service: {product}
- Analysis Period: {period}
- Focus: {focus}
"""


def analyze_insights(config: dict, api_key: str) -> dict:
    """Analyse customer data and generate unified insights."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = INSIGHTS_PROMPT.format(**config)
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
