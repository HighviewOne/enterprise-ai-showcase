"""Claims Processing Assistant engine - reviews insurance claims."""

import json
import anthropic

CLAIMS_PROMPT = """\
You are an expert insurance claims adjudicator and medical billing specialist. \
Review the submitted claims for completeness, accuracy, medical necessity, and \
policy compliance. Generate recommendations for approval, denial, or escalation.

Return a JSON object:

{{
  "batch_summary": {{
    "total_claims": <number>,
    "total_billed": <number>,
    "auto_approve": <count>,
    "needs_review": <count>,
    "likely_deny": <count>,
    "estimated_payout": <number>,
    "savings_identified": <number>
  }},

  "claim_reviews": [
    {{
      "claim_id": "Claim reference number",
      "claimant": "Patient name",
      "provider": "Provider name",
      "total_billed": <number>,
      "recommendation": "Approve | Approve with Adjustment | Pend for Review | Deny",
      "recommended_payout": <number>,
      "confidence": "High | Medium | Low",
      "risk_score": <1-10>,

      "completeness_check": {{
        "is_complete": true|false,
        "missing_items": ["missing item 1"],
        "documentation_quality": "Complete | Partial | Insufficient"
      }},

      "medical_necessity": {{
        "is_necessary": true|false,
        "justification": "Why treatment is or isn't medically necessary",
        "alternative_treatments": ["cheaper alternative if applicable"]
      }},

      "coding_review": {{
        "codes_accurate": true|false,
        "issues": ["coding issue if any"],
        "suggested_corrections": ["correction if needed"]
      }},

      "policy_compliance": {{
        "in_compliance": true|false,
        "violations": ["policy violation"],
        "pre_auth_status": "Obtained | Not Required | Missing | Exceeded"
      }},

      "flags": [
        {{"type": "Fraud Risk | Upcoding | Missing Auth | Out of Network | Duplicate | Exceeded Benefit",
          "severity": "High | Medium | Low",
          "detail": "Description of the flag"}}
      ],

      "adjuster_notes": "Detailed notes for the claims adjuster",
      "member_impact": "How this decision affects the member"
    }}
  ],

  "trend_analysis": {{
    "common_issues": ["recurring issue across claims"],
    "fraud_indicators": ["any patterns suggesting potential fraud"],
    "process_improvements": ["suggestions to improve claims processing"],
    "provider_notes": ["notes about specific providers"]
  }}
}}

Be thorough, fair, and follow standard claims adjudication principles.
Flag potential fraud but don't make accusations - note indicators.

IMPORTANT: Return ONLY the JSON object.

---

CLAIMS TO REVIEW:
{claims}

REVIEW GUIDELINES:
- Policy Type Context: {policy_context}
- Review Focus: {focus}
- Additional Context: {context}
"""


def review_claims(config: dict, api_key: str) -> dict:
    """Review insurance claims and generate adjudication recommendations."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = CLAIMS_PROMPT.format(**config)
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
