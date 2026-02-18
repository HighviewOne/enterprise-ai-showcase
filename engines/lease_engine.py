"""Lease Management engine - Automated lease data extraction and analysis."""

import json
import anthropic

LEASE_PROMPT = """\
You are an expert lease analyst specialising in commercial and real estate lease \
abstraction, compliance, and portfolio management. Extract key data from the lease \
documents and provide structured analysis for ERP integration.

Return a JSON object:

{{
  "portfolio_summary": {{
    "total_leases": <number>,
    "total_annual_obligation": "$X",
    "upcoming_expirations": <count within 12 months>,
    "key_finding": "One-line portfolio insight"
  }},

  "lease_abstractions": [
    {{
      "lease_id": "Reference number",
      "tenant_lessee": "Lessee name",
      "landlord_lessor": "Lessor name",
      "property_address": "Address",
      "lease_type": "Office | Retail | Industrial | Equipment | Vehicle",
      "classification": "Operating | Finance (IFRS 16 / ASC 842)",
      "commencement_date": "Date",
      "expiration_date": "Date",
      "term_months": <number>,
      "base_rent": "$X/month",
      "annual_rent": "$X",
      "escalation_clause": "Rent increase terms",
      "security_deposit": "$X",
      "renewal_options": "Renewal terms",
      "termination_clause": "Early termination terms",
      "key_obligations": ["maintenance, insurance, taxes, etc."],
      "critical_dates": [
        {{"date": "Date", "event": "What happens", "action_needed": "What to do"}}
      ],
      "risks": ["identified risks"],
      "compliance_notes": "IFRS 16 / ASC 842 implications"
    }}
  ],

  "financial_analysis": {{
    "total_commitment": "$X",
    "annual_breakdown": [
      {{"year": "YYYY", "obligation": "$X"}}
    ],
    "lease_liability_estimate": "$X (present value)",
    "right_of_use_asset": "$X"
  }},

  "compliance_checklist": [
    {{"requirement": "What needs to be done", "standard": "IFRS 16 / ASC 842 / Local",
      "status": "Compliant | Gap | Review Needed", "action": "Remediation step"}}
  ],

  "critical_dates_calendar": [
    {{"date": "Date", "lease_id": "Reference", "event": "Description", "priority": "High | Medium | Low"}}
  ],

  "recommendations": [
    {{"recommendation": "What to do", "impact": "Financial or operational impact",
      "priority": "High | Medium | Low"}}
  ]
}}

Be precise with dates, amounts, and obligations. Flag any missing or ambiguous terms \
that need clarification.

IMPORTANT: Return ONLY the JSON object.

---

LEASE DOCUMENTS:
{lease_data}

ANALYSIS PARAMETERS:
- Company: {company}
- Accounting Standard: {standard}
- Discount Rate: {discount_rate}%
- Analysis Focus: {focus}
"""


def analyze_leases(config: dict, api_key: str) -> dict:
    """Analyse lease documents and extract key data."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = LEASE_PROMPT.format(**config)
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
