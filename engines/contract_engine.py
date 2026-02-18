"""Government Contract Assistant engine - Proposal analysis and guidance."""

import json
import anthropic

CONTRACT_PROMPT = """\
You are an expert government contracting advisor helping small and medium businesses \
navigate federal procurement. Analyse the solicitation and company profile to provide \
proposal guidance, compliance checks, and win strategy.

Return a JSON object:

{{
  "opportunity_analysis": {{
    "title": "Contract title",
    "agency": "Issuing agency",
    "contract_type": "FFP | T&M | CPFF | IDIQ | BPA",
    "naics_code": "NAICS code",
    "set_aside": "Small Business | 8(a) | WOSB | SDVOSB | HUBZone | Full & Open",
    "estimated_value": "$X",
    "period_of_performance": "Duration",
    "competition_level": "Low | Medium | High",
    "fit_score": <1-100>,
    "go_no_go_recommendation": "Go | Conditional Go | No-Go",
    "rationale": "Why this recommendation"
  }},

  "compliance_checklist": [
    {{"requirement": "Solicitation requirement", "status": "Met | Partially Met | Gap | N/A",
      "evidence": "How company meets this", "action_needed": "What to do if gap"}}
  ],

  "proposal_outline": [
    {{"section": "Section name (e.g., Technical Approach, Past Performance)",
      "page_limit": "If specified",
      "key_points": ["What to emphasise"],
      "discriminators": ["What sets you apart"],
      "warnings": ["What to avoid"]}}
  ],

  "win_themes": [
    {{"theme": "Win theme statement", "evidence": "Supporting evidence",
      "ghost_competitor": "How this differentiates from likely competitors"}}
  ],

  "past_performance_strategy": {{
    "relevant_contracts": ["contracts to highlight"],
    "storytelling_approach": "How to frame past work",
    "gap_mitigation": "How to handle experience gaps"
  }},

  "pricing_guidance": {{
    "strategy": "Pricing approach recommendation",
    "considerations": ["factors affecting pricing"],
    "competitive_range": "Expected range if known",
    "warnings": ["pricing pitfalls"]
  }},

  "teaming_recommendations": {{
    "needs_teaming": true|false,
    "partner_capabilities_needed": ["capabilities to seek in partners"],
    "teaming_structure": "Prime/Sub | JV | Mentor-Protege",
    "recommendations": ["specific teaming suggestions"]
  }},

  "timeline": [
    {{"milestone": "Proposal milestone", "deadline": "Date or relative time",
      "owner": "Who's responsible", "dependencies": "What needs to happen first"}}
  ],

  "risk_factors": [
    {{"risk": "Risk description", "impact": "High | Medium | Low",
      "mitigation": "How to address"}}
  ]
}}

Be practical and specific. Focus on actionable guidance that helps an SMB win.

IMPORTANT: Return ONLY the JSON object.

---

SOLICITATION DETAILS:
{solicitation}

COMPANY PROFILE:
{company_profile}

PARAMETERS:
- Primary NAICS: {naics}
- Business Certifications: {certifications}
- Target Award Date: {award_date}
- Additional Context: {context}
"""


def analyze_contract(config: dict, api_key: str) -> dict:
    """Analyse government contract opportunity and generate proposal guidance."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = CONTRACT_PROMPT.format(**config)
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
