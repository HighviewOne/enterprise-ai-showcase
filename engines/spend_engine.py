"""AI Spend Monitor engine - FinOps anomaly detection."""

import json
import anthropic

SPEND_PROMPT = """\
You are an expert FinOps analyst specialising in cloud and SaaS spend monitoring, \
anomaly detection, and cost optimisation. Analyse the spend data below, identify \
anomalies, and provide actionable recommendations for resolution.

Return a JSON object:

{{
  "spend_summary": {{
    "total_spend": "$X",
    "period": "Month Year",
    "baseline_budget": "$X",
    "variance_pct": <number>,
    "anomaly_count": <number>,
    "key_finding": "One-line summary"
  }},

  "anomalies": [
    {{
      "vendor": "Vendor name",
      "category": "Cloud | SaaS | Consulting | Hardware | Other",
      "amount": "$X",
      "expected_amount": "$X",
      "variance_pct": <number>,
      "severity": "Critical | High | Medium | Low",
      "anomaly_type": "Spike | New Vendor | Contract Breach | Duplicate | Unusual Pattern",
      "root_cause_hypothesis": "What likely caused this",
      "recommended_action": "What to do",
      "priority": "P0 | P1 | P2",
      "estimated_savings": "$X"
    }}
  ],

  "vendor_analysis": [
    {{
      "vendor": "Name",
      "total_spend": "$X",
      "trend": "Increasing | Stable | Decreasing",
      "contract_status": "Within contract | Over contract | No contract",
      "risk_level": "High | Medium | Low",
      "notes": "Analysis notes"
    }}
  ],

  "category_breakdown": [
    {{"category": "Category name", "spend": "$X", "budget": "$X", "variance_pct": <number>,
      "status": "Over Budget | On Track | Under Budget"}}
  ],

  "cost_optimization": [
    {{
      "opportunity": "Description",
      "estimated_savings": "$X/month",
      "effort": "Low | Medium | High",
      "recommendation": "Specific action"
    }}
  ],

  "resolution_actions": [
    {{
      "action": "What needs to happen",
      "owner": "Finance | Engineering | Procurement | Management",
      "priority": "P0 | P1 | P2",
      "status": "Open",
      "deadline": "Timeframe"
    }}
  ],

  "trend_analysis": {{
    "monthly_trend": [
      {{"month": "Mon YYYY", "spend": <number>}}
    ],
    "forecast_next_month": "$X",
    "yoy_comparison": "Year-over-year note"
  }},

  "executive_summary": {{
    "one_liner": "Executive-level summary",
    "risk_rating": "Critical | High | Medium | Low",
    "total_potential_savings": "$X/month",
    "top_actions": ["Top 3 actions to take immediately"]
  }}
}}

Be precise with numbers and prioritise findings by financial impact. Flag any \
policy/process violations (missing POs, unapproved vendors, duplicate payments).

IMPORTANT: Return ONLY the JSON object.

---

SPEND DATA:
{spend_data}

ANALYSIS PARAMETERS:
- Analysis Period: {period}
- Monthly Budget: ${budget}
- Department: {department}
- Alert Threshold: {threshold}% variance
- Focus Areas: {focus_areas}
- Additional Context: {context}
"""


def analyze_spend(config: dict, api_key: str) -> dict:
    """Analyse spend data and detect anomalies."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = SPEND_PROMPT.format(**config)
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
