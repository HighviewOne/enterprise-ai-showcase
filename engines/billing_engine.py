"""Billing Compliance engine - reviews billing logs against guidelines."""

from engines.llm import call_claude_json

REVIEW_PROMPT = """\
You are an expert legal billing compliance auditor. Review the billing log entries \
against the provided billing guidelines and identify violations, vague descriptions, \
and entries needing human review.

Return a JSON object:

{{
  "summary": {{
    "total_entries": <number>,
    "total_hours": <number>,
    "total_amount": <number>,
    "compliant_entries": <number>,
    "flagged_entries": <number>,
    "violation_rate_pct": <number>,
    "estimated_write_off": <number>
  }},

  "flagged_items": [
    {{
      "entry_ref": "Date - Attorney - Description snippet",
      "severity": "High | Medium | Low",
      "violation_type": "Vague Description | Excessive Hours | Block Billing | Prohibited Charge | Rate Violation | Minimum Increment",
      "original_description": "The original entry description",
      "issue": "What's wrong with this entry",
      "suggested_rewrite": "Improved description that would be compliant",
      "recommended_action": "Approve | Revise | Write-off | Reduce Hours",
      "amount_at_risk": <dollar amount of this entry>
    }}
  ],

  "attorney_summary": [
    {{
      "attorney": "Name",
      "total_hours": <number>,
      "total_billed": <number>,
      "violations": <count>,
      "compliance_score": <0-100>,
      "primary_issue": "Most common issue for this attorney",
      "recommendation": "Brief recommendation"
    }}
  ],

  "client_summary": [
    {{
      "client": "Client name",
      "total_hours": <number>,
      "total_billed": <number>,
      "flagged_amount": <amount at risk>,
      "risk_level": "Low | Medium | High"
    }}
  ],

  "top_recommendations": [
    "Overall recommendation 1",
    "Overall recommendation 2",
    "Overall recommendation 3"
  ],

  "compliance_trends": {{
    "most_common_violation": "The most frequent type of violation",
    "highest_risk_matter": "Which matter has the most risk",
    "training_needs": ["areas where attorneys need training"]
  }}
}}

Be thorough and check every entry against the guidelines. Flag anything questionable.

IMPORTANT: Return ONLY the JSON object.

---

BILLING GUIDELINES:
{guidelines}

BILLING LOG:
{billing_log}

REVIEW CONTEXT: {context}
"""


def review_billing(config: dict, api_key: str) -> dict:
    """Review billing log against guidelines."""
    prompt = REVIEW_PROMPT.format(**config)
    return call_claude_json(prompt, api_key, max_tokens=4096)
