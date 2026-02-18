"""RegWatch engine - Compliance intelligence and regulation analysis."""

import json
import anthropic

REGTECH_PROMPT = """\
You are an expert regulatory compliance analyst and RegTech advisor. Analyze the given \
regulation against the organization's profile and current compliance posture, then generate \
a comprehensive compliance intelligence report.

Return a JSON object:

{{
  "regulation_summary": {{
    "regulation_name": "Official name of the regulation",
    "issuing_body": "Regulatory authority",
    "effective_date": "When it takes effect",
    "key_objectives": ["primary goals of the regulation"],
    "plain_language_summary": "Clear, non-legal explanation of what the regulation requires",
    "scope": "Who and what is covered",
    "key_definitions": [{{"term": "Term", "definition": "Plain-language definition"}}]
  }},

  "applicability_assessment": {{
    "applies": true,
    "applicability_level": "Full | Partial | Indirect | Not Applicable",
    "rationale": "Why this regulation applies or does not apply",
    "entity_classification": "How the organization is classified under this regulation",
    "in_scope_activities": ["specific business activities in scope"],
    "out_of_scope_activities": ["activities not covered"],
    "proportionality": "How requirements scale based on organization size/risk"
  }},

  "gap_analysis": [
    {{
      "section": "Regulation section or article",
      "requirement": "What is required",
      "current_state": "Organization's current compliance status",
      "gap_status": "Compliant | Partial | Non-Compliant | Not Assessed",
      "gap_description": "Specific gap details",
      "priority": "Critical | High | Medium | Low",
      "effort_estimate": "Low | Medium | High | Very High"
    }}
  ],

  "compliance_roadmap": [
    {{
      "phase": "Phase name",
      "timeline": "e.g. Q1 2025",
      "actions": ["specific actions to take"],
      "dependencies": ["what must happen first"],
      "responsible_party": "Who owns this",
      "milestone": "Key deliverable"
    }}
  ],

  "impact_assessment": {{
    "operational_impact": "How operations will change",
    "technical_impact": "Technology changes required",
    "financial_impact": {{
      "estimated_compliance_cost": "Cost range to achieve compliance",
      "ongoing_annual_cost": "Annual cost to maintain compliance",
      "cost_breakdown": [{{"category": "Category", "estimate": "Cost range"}}]
    }},
    "staffing_impact": "People and skills needed",
    "timeline_impact": "How long full compliance will take"
  }},

  "cross_regulation_mapping": [
    {{
      "framework": "Existing framework (e.g. GDPR, SOC2)",
      "overlap_percentage": "Estimated overlap",
      "overlapping_areas": ["specific overlapping requirements"],
      "unique_requirements": ["requirements not covered by existing compliance"],
      "leverage_opportunity": "How existing compliance work can be reused"
    }}
  ],

  "risk_of_non_compliance": {{
    "maximum_penalty": "Maximum financial penalty",
    "penalty_calculation": "How penalties are determined",
    "enforcement_body": "Who enforces this",
    "enforcement_trends": "Recent enforcement actions and trends",
    "reputational_risk": "Reputational impact of non-compliance",
    "business_continuity_risk": "Risk to ongoing operations",
    "liability_exposure": "Personal liability for executives/board"
  }},

  "implementation_requirements": {{
    "people": ["roles and skills needed"],
    "process": ["process changes required"],
    "technology": ["technology solutions needed"],
    "governance": ["governance structures to establish"],
    "documentation": ["documentation and policies to create"],
    "training": ["training programs required"]
  }},

  "monitoring_plan": {{
    "kpis": [{{"metric": "KPI name", "target": "Target value", "frequency": "How often measured"}}],
    "reporting_requirements": ["mandatory reporting obligations"],
    "audit_schedule": "Recommended audit frequency and approach",
    "continuous_monitoring": ["areas requiring ongoing automated monitoring"],
    "incident_response": "How compliance incidents should be handled",
    "review_cycle": "How often to review and update compliance program"
  }},

  "board_reporting": {{
    "executive_summary": "2-3 sentence summary for leadership",
    "compliance_score": <0-100>,
    "risk_rating": "Critical | High | Medium | Low",
    "key_decisions_needed": ["decisions the board needs to make"],
    "budget_request": "Funding needed for compliance program",
    "timeline_to_compliance": "Expected time to full compliance",
    "recommended_actions": ["top 3-5 actions for leadership to approve"]
  }}
}}

Be thorough, practical, and actionable. Provide realistic cost estimates and timelines. \
Reference real regulatory precedents and enforcement trends where possible.

IMPORTANT: Return ONLY the JSON object.

---

ORGANIZATION PROFILE:
{org_profile}

REGULATION TO ANALYZE:
{regulation_text}

CURRENT COMPLIANCE POSTURE:
{compliance_posture}

ANALYSIS PARAMETERS:
- Industry: {industry}
- Jurisdiction: {jurisdiction}
- Current Frameworks: {current_frameworks}
"""


def analyze_regulation(config: dict, api_key: str) -> dict:
    """Analyze a regulation against an organization's compliance posture."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = REGTECH_PROMPT.format(**config)
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
