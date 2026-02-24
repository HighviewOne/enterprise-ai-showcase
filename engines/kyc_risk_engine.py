"""AI Risk Shield engine - KYC/AML risk classification."""

import json
import anthropic

RISK_PROMPT = """\
You are an expert financial crime compliance analyst specializing in KYC (Know Your \
Customer), AML (Anti-Money Laundering), and sanctions screening. Analyze the customer \
profiles and classify their risk levels with supporting evidence.

Return a JSON object:

{{
  "batch_summary": {{
    "total_customers": <number>,
    "high_risk": <count>,
    "medium_risk": <count>,
    "low_risk": <count>,
    "blocked": <count>,
    "key_findings": "One-line summary of batch risk profile"
  }},

  "customer_assessments": [
    {{
      "customer_id": "Name or reference",
      "entity_type": "Individual | Corporate | Trust",
      "risk_classification": "Low | Medium | High | Very High | Blocked/Rejected",
      "risk_score": <1-100>,
      "confidence": "High | Medium | Low",
      "recommendation": "Approve | Approve with EDD | Escalate | Reject",

      "kyc_checks": {{
        "identity_verification": "Pass | Incomplete | Fail",
        "address_verification": "Pass | Incomplete | Fail",
        "source_of_funds": "Verified | Partially Verified | Unverified | Suspicious",
        "beneficial_ownership": "Clear | Partially Clear | Opaque"
      }},

      "pep_screening": {{
        "is_pep": true|false,
        "pep_type": "None | Domestic PEP | Foreign PEP | Close Associate | Family Member",
        "details": "PEP details if applicable",
        "risk_implication": "How PEP status affects risk"
      }},

      "sanctions_screening": {{
        "sanctions_hit": true|false,
        "lists_checked": ["OFAC SDN", "UN Sanctions", "EU Sanctions", "UK Sanctions"],
        "matches_found": ["any matches or near-matches"],
        "status": "Clear | Potential Match | Confirmed Match"
      }},

      "adverse_media": {{
        "findings": "Summary of adverse media findings",
        "severity": "None | Low | Medium | High",
        "categories": ["Financial Crime | Fraud | Corruption | Terrorism | Tax Evasion"]
      }},

      "transaction_risk": {{
        "pattern_assessment": "Normal | Unusual | Suspicious",
        "red_flags": ["specific red flag identified"],
        "typology_match": "Which ML/TF typology this matches, if any"
      }},

      "risk_factors": [
        {{"factor": "Risk factor description", "weight": "High | Medium | Low",
          "evidence": "Supporting evidence"}}
      ],

      "edd_requirements": [
        "Enhanced due diligence step needed"
      ],

      "analyst_notes": "Detailed notes for the compliance analyst",
      "monitoring_recommendations": "Ongoing monitoring suggestions"
    }}
  ],

  "regulatory_considerations": {{
    "jurisdictional_risks": ["high-risk jurisdiction noted"],
    "regulatory_requirements": ["specific regulation to consider"],
    "reporting_obligations": ["SAR/STR or other reporting needed"]
  }}
}}

Be thorough, evidence-based, and follow FATF guidelines. Note: this is a risk \
assessment tool to ASSIST human analysts, not replace them.

IMPORTANT: Return ONLY the JSON object.

---

CUSTOMER PROFILES:
{customers}

SCREENING PARAMETERS:
- Risk Appetite: {risk_appetite}
- Industry Focus: {industry}
- Jurisdiction: {jurisdiction}
- Additional Context: {context}
"""


def assess_risk(config: dict, api_key: str) -> dict:
    """Assess customer risk profiles for KYC/AML compliance."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = RISK_PROMPT.format(**config)
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
