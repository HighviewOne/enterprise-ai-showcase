"""Venture Research engine - Investment research and deal screening."""

import json
import anthropic

VC_PROMPT = """\
You are an expert venture capital analyst. Screen the business plan / startup profile \
and generate a comprehensive investment research brief aligned with the firm's thesis.

Return a JSON object:

{{
  "deal_summary": {{
    "company": "Company name",
    "sector": "Industry sector",
    "stage": "Pre-seed | Seed | Series A | Series B | Growth",
    "ask": "Funding amount requested",
    "valuation": "Pre-money valuation",
    "thesis_alignment": <1-10>,
    "overall_rating": "Strong Pass | Pass | Borderline | Fail",
    "one_liner": "One-sentence investment thesis"
  }},

  "market_analysis": {{
    "tam": "Total Addressable Market",
    "sam": "Serviceable Addressable Market",
    "som": "Serviceable Obtainable Market",
    "growth_rate": "Market CAGR",
    "market_dynamics": ["key market trends"],
    "timing_assessment": "Why now is the right time"
  }},

  "team_assessment": {{
    "overall_score": <1-10>,
    "strengths": ["team strengths"],
    "gaps": ["missing capabilities"],
    "founder_market_fit": "Assessment of founder-market fit",
    "key_person_risk": "Assessment of key person dependency"
  }},

  "product_assessment": {{
    "stage": "Idea | MVP | Product-Market Fit | Scaling",
    "differentiation": "What makes this unique",
    "moat": "Defensibility assessment",
    "technology_risk": "High | Medium | Low",
    "scalability": "Assessment of ability to scale"
  }},

  "business_model": {{
    "revenue_model": "How they make money",
    "unit_economics": "Key unit metrics",
    "path_to_profitability": "When/how they become profitable",
    "capital_efficiency": "How efficiently they use capital"
  }},

  "competitive_landscape": [
    {{"competitor": "Name", "category": "Direct | Indirect | Adjacent",
      "relative_position": "Ahead | Even | Behind",
      "differentiation": "How target differs"}}
  ],

  "financial_projections_review": {{
    "revenue_reasonableness": "Assessment of projections",
    "key_assumptions": ["critical assumptions to validate"],
    "burn_rate_assessment": "Monthly burn analysis",
    "runway": "Expected runway with this raise"
  }},

  "risk_factors": [
    {{"risk": "Description", "severity": "High | Medium | Low",
      "mitigation": "How it could be mitigated"}}
  ],

  "due_diligence_questions": [
    "Critical questions to ask founders"
  ],

  "investment_recommendation": {{
    "verdict": "Invest | Pass | Further Diligence",
    "conviction_level": "High | Medium | Low",
    "suggested_terms": "Recommended deal terms",
    "value_add_opportunities": ["how the fund can help beyond capital"],
    "exit_scenarios": ["potential exit paths"],
    "rationale": "Detailed investment rationale"
  }}
}}

Be analytical, data-driven, and honest. Flag both opportunities and concerns.

IMPORTANT: Return ONLY the JSON object.

---

BUSINESS PLAN / STARTUP PROFILE:
{startup_profile}

INVESTMENT PARAMETERS:
- Fund Thesis: {fund_thesis}
- Stage Focus: {stage_focus}
- Check Size: {check_size}
- Sector Preferences: {sector_prefs}
"""


def screen_deal(config: dict, api_key: str) -> dict:
    """Screen a startup deal and generate investment brief."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = VC_PROMPT.format(**config)
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
