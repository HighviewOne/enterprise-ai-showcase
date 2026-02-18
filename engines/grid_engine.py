"""GridFlow engine - Power grid interconnection analysis and assessment."""

import json
import anthropic

GRID_PROMPT = """\
You are an expert power grid interconnection engineer and energy analyst. Evaluate whether \
a new asset can safely connect to the power grid and provide a comprehensive interconnection assessment.

Return a JSON object:

{{
  "queue_position_analysis": {{
    "estimated_queue_depth": "Number of projects ahead in queue",
    "average_wait_time_months": 0,
    "queue_trend": "Growing | Stable | Shrinking",
    "withdrawal_rate": "Percentage of projects that drop out",
    "position_assessment": "Favorable | Moderate | Challenging",
    "notes": "Context about the interconnection queue"
  }},

  "grid_capacity_assessment": {{
    "available_capacity_mw": 0,
    "thermal_limit_mw": 0,
    "voltage_limit_mw": 0,
    "stability_limit_mw": 0,
    "congestion_level": "Low | Moderate | High | Critical",
    "headroom_percentage": 0,
    "assessment": "Sufficient | Constrained | Insufficient",
    "notes": "Detailed capacity analysis"
  }},

  "upgrade_requirements": [
    {{"upgrade": "Description of upgrade needed", "category": "Transmission | Substation | Protection | Communication",
      "estimated_cost_usd": 0, "timeline_months": 0, "responsible_party": "Developer | Utility | Shared",
      "criticality": "Required | Recommended | Optional"}}
  ],

  "cost_estimate": {{
    "interconnection_study_costs": 0,
    "network_upgrade_costs": 0,
    "interconnection_facilities_costs": 0,
    "engineering_and_permitting": 0,
    "contingency": 0,
    "total_estimated_cost_usd": 0,
    "cost_per_mw": 0,
    "cost_breakdown_notes": "Explanation of major cost drivers"
  }},

  "timeline_projection": {{
    "total_months": 0,
    "phases": [
      {{"phase": "Phase name", "duration_months": 0, "start_month": 0,
        "description": "What happens in this phase", "key_milestones": ["milestones"]}}
    ],
    "target_achievable": true,
    "earliest_possible_date": "YYYY-QN",
    "most_likely_date": "YYYY-QN",
    "notes": "Timeline assessment"
  }},

  "regulatory_requirements": [
    {{"requirement": "Description", "authority": "Regulatory body",
      "timeline_months": 0, "complexity": "Routine | Moderate | Complex",
      "status": "Not Started | In Progress | Complete"}}
  ],

  "risk_factors": [
    {{"risk": "Description", "severity": "High | Medium | Low",
      "probability": "High | Medium | Low", "impact": "Description of impact",
      "mitigation": "How to mitigate"}}
  ],

  "comparable_projects": [
    {{"project": "Name/description", "capacity_mw": 0, "region": "Region",
      "interconnection_cost_usd": 0, "timeline_months": 0, "outcome": "Completed | In Progress | Withdrawn",
      "lessons_learned": "Key takeaway"}}
  ],

  "optimization_recommendations": [
    {{"recommendation": "Description", "impact": "Cost Reduction | Timeline Acceleration | Risk Reduction",
      "estimated_savings": "Quantified benefit", "implementation_effort": "Low | Medium | High"}}
  ],

  "financial_impact": {{
    "estimated_annual_revenue_usd": 0,
    "interconnection_cost_as_pct_of_capex": 0,
    "payback_period_years": 0,
    "lcoe_impact": "Impact on levelized cost of energy",
    "project_viability": "Strong | Viable | Marginal | Challenging",
    "revenue_risk_factors": ["Factors that could affect revenue"],
    "notes": "Financial impact analysis"
  }}
}}

Be technically rigorous and data-driven. Provide realistic estimates based on current market conditions.

IMPORTANT: Return ONLY the JSON object.

---

ASSET DETAILS:
- Asset Type: {asset_type}
- Capacity: {capacity_mw} MW
- Location/Region: {location}
- Grid Operator (ISO): {grid_operator}
- Interconnection Voltage: {voltage} kV
- Expected Online Date: {online_date}

ADDITIONAL CONTEXT:
{additional_context}
"""


def analyze_interconnection(config: dict, api_key: str) -> dict:
    """Analyze grid interconnection feasibility for a new asset."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = GRID_PROMPT.format(**config)
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
