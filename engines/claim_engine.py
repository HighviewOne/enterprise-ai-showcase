"""Medical Claim Review engine - Claim evaluation and approval recommendations."""

import json
import anthropic

CLAIM_PROMPT = """\
You are an expert medical claim reviewer for a health insurance company. Evaluate the claim \
details, check for completeness, coding accuracy, medical necessity, and generate a preliminary \
recommendation. Apply clinical guidelines and payer policy rules.

Return a JSON object:

{{
  "claim_summary": {{
    "claim_id": "Claim identifier",
    "patient_name": "Patient name",
    "date_of_service": "Service date",
    "provider": "Provider name and credentials",
    "facility": "Facility name",
    "primary_diagnosis": "Primary diagnosis with code",
    "procedures": ["Procedure codes with descriptions"],
    "total_billed": <number>,
    "claim_type": "Professional | Institutional | Dental | Pharmacy"
  }},

  "medical_necessity_assessment": {{
    "is_medically_necessary": true,
    "justification": "Detailed assessment of medical necessity",
    "clinical_guidelines_referenced": ["relevant clinical guidelines"],
    "diagnosis_supports_procedure": true,
    "alternative_treatments_considered": ["less invasive or costly alternatives"],
    "necessity_score": <1-10>
  }},

  "coding_accuracy": {{
    "cpt_codes_valid": true,
    "icd10_codes_valid": true,
    "code_pairing_appropriate": true,
    "upcoding_risk": "High | Medium | Low | None",
    "unbundling_risk": "High | Medium | Low | None",
    "modifier_issues": ["any modifier concerns"],
    "coding_notes": ["specific coding observations"]
  }},

  "documentation_completeness": {{
    "overall_complete": false,
    "missing_items": [
      {{"item": "Document or info needed", "severity": "Critical | Important | Minor", "impact": "How it affects processing"}}
    ],
    "available_documentation": ["documents that were provided"],
    "completeness_score": <1-10>
  }},

  "policy_compliance": {{
    "within_policy_terms": true,
    "pre_authorization_required": true,
    "pre_authorization_obtained": false,
    "referral_required": false,
    "referral_obtained": false,
    "network_status": "In-Network | Out-of-Network | Out-of-Area",
    "policy_exclusions_applicable": ["any relevant exclusions"],
    "compliance_notes": ["specific policy observations"]
  }},

  "duplicate_check_indicators": {{
    "potential_duplicate": false,
    "duplicate_signals": ["any signals suggesting duplicate billing"],
    "recommendation": "Action to take"
  }},

  "fraud_risk_indicators": {{
    "overall_risk": "High | Medium | Low | Minimal",
    "red_flags": [
      {{"indicator": "Description", "severity": "High | Medium | Low", "explanation": "Why this is concerning"}}
    ],
    "fraud_score": <1-10>
  }},

  "comparable_claims": {{
    "typical_allowed_amount": <number>,
    "typical_range_low": <number>,
    "typical_range_high": <number>,
    "geographic_adjustment": "Regional cost factor",
    "percentile_of_billed": "Where this claim falls vs typical"
  }},

  "recommendation": {{
    "decision": "Approve | Deny | Pend for Review | Escalate to Medical Director",
    "confidence": "High | Medium | Low",
    "rationale": "Detailed reasoning for the recommendation",
    "conditions": ["any conditions for approval"]
  }},

  "pend_reasons": [
    {{"reason": "Why claim is pending", "information_needed": "What is required", "source": "Who should provide it", "deadline_days": <number>}}
  ],

  "payment_calculation": {{
    "billed_amount": <number>,
    "allowed_amount": <number>,
    "plan_payment": <number>,
    "member_responsibility": <number>,
    "copay": <number>,
    "coinsurance": <number>,
    "deductible_applied": <number>,
    "adjustments": ["line item adjustments"],
    "payment_notes": ["calculation notes"]
  }},

  "appeal_likelihood": {{
    "likelihood": "High | Medium | Low",
    "common_appeal_grounds": ["typical reasons for appeal"],
    "recommended_preparation": ["how to prepare if appealed"]
  }}
}}

Be thorough, objective, and cite clinical guidelines where applicable. Prioritize patient \
safety and accurate claim adjudication.

IMPORTANT: Return ONLY the JSON object.

---

CLAIM DETAILS:
{claim_details}

PROCEDURE CODES:
{procedure_codes}

DIAGNOSIS CODES:
{diagnosis_codes}

PROVIDER INFORMATION:
{provider_info}

BILLED AMOUNTS:
{billed_amounts}

PATIENT HISTORY SUMMARY:
{patient_history}

POLICY DETAILS:
{policy_details}
"""


def review_claim(config: dict, api_key: str) -> dict:
    """Review a medical claim and generate adjudication recommendation."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = CLAIM_PROMPT.format(**config)
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
