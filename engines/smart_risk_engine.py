"""Smart AI Risk Shield engine - KYC/AML sanctions and PEP screening."""

import json
import anthropic

RISK_PROMPT = """\
You are an expert KYC/AML compliance analyst specialising in sanctions screening, \
Politically Exposed Persons (PEP) identification, and adverse media analysis. \
Analyse the customer profile against known sanctions lists, PEP databases, and \
risk indicators to produce a comprehensive risk classification with evidence.

Return a JSON object:

{{
  "customer_summary": {{
    "name": "Full name as provided",
    "entity_type": "Individual | Corporate | Trust | Foundation",
    "nationality": "Country of nationality/incorporation",
    "risk_classification": "Low | Medium | High | Prohibited",
    "confidence_score": <1-100>,
    "onboarding_recommendation": "Approve | Enhanced Due Diligence | Escalate | Reject",
    "one_liner": "One-sentence risk summary"
  }},

  "sanctions_screening": {{
    "ofac_sdn": {{"match": true/false, "details": "match details or 'No match found'"}},
    "eu_sanctions": {{"match": true/false, "details": "match details or 'No match found'"}},
    "un_sanctions": {{"match": true/false, "details": "match details or 'No match found'"}},
    "uk_sanctions": {{"match": true/false, "details": "match details or 'No match found'"}},
    "other_lists": [{{"list_name": "Name", "match": true/false, "details": "details"}}],
    "fuzzy_matches": [{{"name_variant": "Similar name found", "list": "Which list",
      "similarity_score": <0-100>, "assessment": "Likely match | Possible match | False positive"}}]
  }},

  "pep_screening": {{
    "is_pep": true/false,
    "pep_level": "None | Domestic PEP | Foreign PEP | International Org PEP",
    "position": "Current or former position if PEP",
    "country": "Country of political exposure",
    "relatives_and_associates": [{{"name": "Name", "relationship": "Relationship",
      "pep_status": "PEP | RCA (Relative/Close Associate)"}}],
    "risk_implications": "How PEP status affects risk rating"
  }},

  "adverse_media": [
    {{"source_type": "News | Regulatory Action | Court Filing | Leak",
      "headline": "Summary of adverse finding",
      "severity": "Critical | High | Medium | Low",
      "relevance": "Direct | Indirect | Tangential",
      "details": "Key details of the finding"}}
  ],

  "country_risk": {{
    "residence_country_risk": "Low | Medium | High | Very High",
    "nationality_risk": "Low | Medium | High | Very High",
    "fatf_status": "White List | Grey List | Black List | Not Listed",
    "cpi_score": "Transparency International CPI assessment",
    "high_risk_jurisdictions": ["any high-risk jurisdictions involved"],
    "tax_haven_flag": true/false
  }},

  "transaction_risk_indicators": [
    {{"indicator": "Risk signal identified",
      "category": "Source of Funds | Transaction Pattern | Geographic | Structural",
      "severity": "High | Medium | Low",
      "explanation": "Why this is a concern"}}
  ],

  "beneficial_ownership": {{
    "transparency": "Clear | Partially Opaque | Opaque",
    "ultimate_beneficial_owners": [{{"name": "Name", "ownership_pct": <number>,
      "risk_level": "Low | Medium | High", "notes": "Any concerns"}}],
    "complex_structures": true/false,
    "shell_company_risk": "Low | Medium | High",
    "nominee_arrangements": true/false
  }},

  "edd_requirements": [
    {{"requirement": "What additional due diligence is needed",
      "priority": "Critical | High | Medium",
      "responsible_party": "Who should perform this check",
      "deadline": "Recommended timeframe"}}
  ],

  "risk_scoring": {{
    "identity_risk": <1-10>,
    "geographic_risk": <1-10>,
    "product_service_risk": <1-10>,
    "transaction_risk": <1-10>,
    "pep_risk": <1-10>,
    "sanctions_risk": <1-10>,
    "adverse_media_risk": <1-10>,
    "overall_risk_score": <1-100>,
    "methodology": "Explanation of scoring approach"
  }},

  "recommendation": {{
    "decision": "Approve | Approve with EDD | Escalate to MLRO | Reject",
    "rationale": "Detailed reasoning for the decision",
    "conditions": ["conditions that must be met if approved"],
    "monitoring_level": "Standard | Enhanced | Intensive",
    "review_frequency": "Annual | Semi-Annual | Quarterly | Monthly",
    "sar_filing": "Required | Not Required | Consider"
  }}
}}

Be thorough, evidence-based, and conservative. When in doubt, escalate.

IMPORTANT: Return ONLY the JSON object.

---

CUSTOMER PROFILE:
{customer_profile}

SCREENING CONTEXT:
- Business Relationship: {business_relationship}
- Products/Services: {products_services}
- Expected Transaction Volume: {transaction_volume}
- Source of Funds: {source_of_funds}
- Jurisdiction: {jurisdiction}
"""


def screen_customer(config: dict, api_key: str) -> dict:
    """Screen a customer for KYC/AML compliance risks."""
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
