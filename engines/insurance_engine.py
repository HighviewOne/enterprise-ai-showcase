"""AI-nsurance engine - AI-powered insurance claims processing and analysis."""

import json
import anthropic

INSURANCE_PROMPT = """\
You are an expert insurance claims adjuster and underwriting analyst. Analyze the \
insurance claim and generate a comprehensive claims processing report.

Return a JSON object:

{{
  "claim_classification": {{
    "type": "Auto | Health | Property | Life | Liability | Workers Comp",
    "sub_type": "Specific sub-category",
    "complexity": "Simple | Moderate | Complex | Highly Complex",
    "priority": "Low | Medium | High | Urgent"
  }},

  "document_checklist": [
    {{"document": "Document name", "required": true, "status": "Received | Pending | Not Applicable",
      "notes": "Additional context"}}
  ],

  "coverage_analysis": {{
    "covered_items": ["Items/events covered under the policy"],
    "excluded_items": ["Items/events NOT covered"],
    "coverage_limit": "Maximum coverage amount",
    "deductible": "Applicable deductible",
    "co_insurance": "Co-insurance percentage if applicable",
    "policy_status": "Active | Lapsed | Under Review",
    "coverage_notes": "Additional coverage details"
  }},

  "liability_assessment": {{
    "liability_determination": "Description of liability findings",
    "fault_percentage": "Percentage of fault assigned to claimant",
    "third_party_involvement": "Details of third party liability if any",
    "subrogation_potential": "Yes | No | Possible",
    "notes": "Additional liability context"
  }},

  "damage_estimate": {{
    "itemized_costs": [
      {{"item": "Description", "category": "Medical | Repair | Replacement | Labor | Other",
        "estimated_cost": 0.00, "notes": "Details"}}
    ],
    "total_estimate": 0.00,
    "depreciation": 0.00,
    "net_claim_value": 0.00
  }},

  "fraud_indicators": {{
    "risk_level": "Low | Medium | High",
    "flags": ["Any red flags identified"],
    "recommendation": "Proceed | Investigate Further | Refer to SIU",
    "notes": "Explanation of fraud assessment"
  }},

  "processing_recommendation": {{
    "track": "Fast-Track | Standard | Escalate",
    "reason": "Reason for recommendation",
    "assigned_complexity_tier": "Tier 1 | Tier 2 | Tier 3",
    "requires_independent_adjuster": false,
    "requires_medical_review": false
  }},

  "settlement_estimate": {{
    "low_range": 0.00,
    "high_range": 0.00,
    "recommended_settlement": 0.00,
    "rationale": "Basis for settlement range"
  }},

  "next_steps_for_claimant": [
    "Actionable next steps for the claimant"
  ],

  "compliance_check": {{
    "regulatory_requirements_met": true,
    "state_specific_requirements": ["Applicable state regulations"],
    "filing_deadlines": "Relevant deadlines",
    "documentation_compliance": "Compliant | Needs Attention",
    "notes": "Compliance details"
  }},

  "timeline_to_resolution": {{
    "estimated_days": 0,
    "phases": [
      {{"phase": "Phase name", "duration_days": 0, "status": "Pending | In Progress | Complete"}}
    ],
    "bottlenecks": ["Potential delays"],
    "expedite_options": ["Ways to speed up resolution"]
  }}
}}

Be thorough, fair, and data-driven. Identify both valid claim elements and potential concerns.

IMPORTANT: Return ONLY the JSON object.

---

CLAIM DESCRIPTION:
{claim_description}

POLICY DETAILS:
- Coverage Type: {coverage_type}
- Policy Limits: {policy_limits}
- Deductible: {deductible}
- Policy Period: {policy_period}

CLAIMANT PROFILE:
{claimant_profile}
"""


def process_claim(config: dict, api_key: str) -> dict:
    """Process an insurance claim and generate analysis report."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = INSURANCE_PROMPT.format(**config)
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
