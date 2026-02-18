"""Due Diligence Generator engine - M&A technology due diligence."""

import json
import anthropic

DD_PROMPT = """\
You are an expert technology due diligence analyst for M&A and investment deals. \
Analyse the target company profile and generate a comprehensive technology due \
diligence report with scoring, risk assessment, and recommendations.

Return a JSON object:

{{
  "executive_summary": {{
    "overall_score": <1-100>,
    "rating": "Strong | Adequate | Concerning | Critical",
    "headline": "One-sentence assessment",
    "deal_recommendation": "Proceed | Proceed with Conditions | Caution | Do Not Proceed",
    "key_findings": ["top 3-5 findings"]
  }},

  "technology_assessment": [
    {{
      "area": "Architecture | Code Quality | Scalability | Security | DevOps | Data Management | IP/Innovation | Tech Debt | Team & Talent | Documentation",
      "score": <1-10>,
      "rating": "Strong | Adequate | Weak | Critical",
      "findings": "Detailed findings",
      "risks": ["specific risks"],
      "recommendations": ["specific recommendations"]
    }}
  ],

  "questionnaire": [
    {{
      "category": "Category name",
      "questions": [
        {{"question": "Due diligence question", "priority": "Critical | Important | Nice-to-have",
          "expected_evidence": "What documentation to request"}}
      ]
    }}
  ],

  "risk_register": [
    {{
      "risk": "Risk description",
      "category": "Technical | Operational | Financial | Legal",
      "likelihood": "High | Medium | Low",
      "impact": "Critical | High | Medium | Low",
      "mitigation": "How to mitigate",
      "deal_impact": "How this affects deal valuation"
    }}
  ],

  "valuation_impact": {{
    "tech_premium_factors": ["factors that add value"],
    "tech_discount_factors": ["factors that reduce value"],
    "estimated_tech_debt_cost": "$X",
    "integration_complexity": "Low | Medium | High",
    "estimated_integration_cost": "$X"
  }},

  "benchmarking": {{
    "industry_comparison": "How target compares to industry standards",
    "strengths_vs_peers": ["competitive advantages"],
    "weaknesses_vs_peers": ["areas lagging behind"]
  }},

  "post_acquisition_roadmap": [
    {{"phase": "Phase name (30/60/90/180 days)", "actions": ["action items"],
      "estimated_cost": "$X", "priority": "Critical | Important | Enhancement"}}
  ],

  "red_flags": ["Any deal-breaking or serious concerns"],
  "green_flags": ["Positive indicators supporting the deal"]
}}

Be thorough, evidence-based, and highlight anything that could affect deal valuation \
or post-acquisition integration.

IMPORTANT: Return ONLY the JSON object.

---

TARGET COMPANY PROFILE:
{company_profile}

DEAL PARAMETERS:
- Deal Type: {deal_type}
- Acquirer Industry: {acquirer_industry}
- Deal Size Range: {deal_size}
- Strategic Rationale: {rationale}
- Due Diligence Focus: {focus}
"""


def generate_diligence(config: dict, api_key: str) -> dict:
    """Generate technology due diligence report."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = DD_PROMPT.format(**config)
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
