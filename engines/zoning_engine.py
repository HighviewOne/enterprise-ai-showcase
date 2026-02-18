"""CityPlanAI engine - Zoning compliance and land-use application analysis."""

import json
import anthropic

ZONING_PROMPT = """\
You are an expert urban planner, zoning attorney, and land-use analyst. Review the zoning \
application details against applicable zoning rules and generate a comprehensive compliance \
memo with recommendations.

Return a JSON object:

{{
  "application_summary": {{
    "parcel_id": "Parcel identifier",
    "applicant": "Applicant name",
    "application_type": "As-of-right | Special Permit | Variance | Rezoning | Other",
    "current_zoning": "Current zoning designation",
    "proposed_use": "Description of proposed use",
    "project_description": "Summary of the proposed development",
    "key_metrics": {{
      "lot_area_sf": "Total lot area in square feet",
      "proposed_far": "Proposed floor area ratio",
      "proposed_height": "Proposed building height",
      "proposed_units": "Number of residential units",
      "proposed_commercial_sf": "Commercial square footage",
      "parking_spaces": "Number of parking spaces proposed"
    }}
  }},

  "zoning_compliance": {{
    "overall_status": "Compliant | Non-Compliant | Partially Compliant",
    "zoning_district_description": "Description of the zoning district and its intent",
    "permitted_uses": ["uses allowed as-of-right in this zone"],
    "conditional_uses": ["uses allowed with special permit"],
    "prohibited_uses": ["uses not allowed in this zone"],
    "proposed_use_status": "Permitted | Conditional | Prohibited | Requires Variance",
    "zoning_text_references": ["relevant zoning code sections"]
  }},

  "bulk_regulations": [
    {{
      "regulation": "Regulation name (e.g. FAR, Height, Setbacks)",
      "allowed": "Maximum/minimum allowed value",
      "proposed": "What the application proposes",
      "status": "Compliant | Non-Compliant | Waiver Needed",
      "deviation": "Amount of deviation if non-compliant",
      "notes": "Additional context"
    }}
  ],

  "use_group_analysis": {{
    "proposed_use_groups": ["Use groups for proposed activities"],
    "permitted_use_groups": ["Use groups allowed in this zone"],
    "conflicts": ["any use group conflicts identified"],
    "mixed_use_compatibility": "Assessment of compatibility of proposed mixed uses",
    "accessory_uses": ["any accessory uses proposed and their compliance"]
  }},

  "variance_assessment": {{
    "variance_needed": true,
    "variance_type": "Area Variance | Use Variance | Both | None",
    "variances_required": [
      {{
        "item": "What requires a variance",
        "requested_relief": "Specific relief requested",
        "legal_standard": "Applicable legal standard for granting",
        "justification_strength": "Strong | Moderate | Weak",
        "analysis": "Detailed analysis of whether criteria are met"
      }}
    ],
    "hardship_argument": "Assessment of unique hardship or practical difficulty",
    "precedents": ["similar variance approvals or denials in the area"],
    "likelihood_of_approval": "High | Medium | Low"
  }},

  "environmental_review": {{
    "review_required": true,
    "review_type": "Type I | Type II | Unlisted (SEQRA) or similar",
    "triggers": ["what triggers environmental review"],
    "key_environmental_concerns": ["potential environmental issues"],
    "required_studies": ["environmental studies that may be needed"],
    "mitigation_measures": ["potential mitigation strategies"],
    "estimated_timeline": "Expected timeline for environmental review"
  }},

  "community_impact": {{
    "traffic_impact": "Assessment of traffic generation and parking demand",
    "shadow_analysis": "Impact of building shadows on surrounding properties",
    "infrastructure_capacity": "Assessment of water, sewer, utility capacity",
    "school_impact": "Impact on local school capacity if residential",
    "neighborhood_character": "Compatibility with surrounding neighborhood",
    "public_benefit": "Community benefits of the proposed development",
    "displacement_risk": "Risk of displacement of existing uses/residents"
  }},

  "landmark_considerations": {{
    "in_historic_district": false,
    "landmark_proximity": "Proximity to designated landmarks",
    "landmark_commission_review": "Whether landmarks commission review is required",
    "design_guidelines": "Applicable design guidelines or restrictions",
    "impact_on_historic_resources": "Assessment of impact on historic character"
  }},

  "recommendation": {{
    "decision": "Approve | Approve with Conditions | Deny | Further Review Required",
    "confidence": "High | Medium | Low",
    "rationale": "Detailed rationale for the recommendation",
    "key_strengths": ["strongest aspects of the application"],
    "key_concerns": ["most significant concerns"]
  }},

  "conditions": [
    {{
      "condition": "Specific condition for approval",
      "category": "Design | Environmental | Traffic | Community | Infrastructure | Other",
      "rationale": "Why this condition is necessary"
    }}
  ],

  "comparable_precedents": [
    {{
      "case": "Case name or reference",
      "location": "Where",
      "similarity": "How it is similar",
      "outcome": "Approved | Denied | Modified",
      "relevance": "How this precedent applies to current application"
    }}
  ],

  "public_hearing_preparation": {{
    "likely_objections": [
      {{
        "objection": "Expected community objection",
        "response_strategy": "Recommended response",
        "supporting_evidence": "Data or precedent to cite"
      }}
    ],
    "community_benefits_to_highlight": ["benefits to emphasize at hearing"],
    "presentation_recommendations": ["tips for effective presentation"],
    "stakeholder_engagement": "Recommended pre-hearing outreach strategy"
  }}
}}

Be thorough, cite specific zoning code sections where possible, and provide practical \
recommendations. Consider both legal and community perspectives.

IMPORTANT: Return ONLY the JSON object.

---

ZONING APPLICATION DETAILS:
{application_details}

CURRENT ZONING DESIGNATION:
{zoning_designation}

PROPOSED CHANGES:
{proposed_changes}

APPLICANT INFORMATION:
{applicant_info}

LOCATION CONTEXT:
{location_context}
"""


def analyze_zoning(config: dict, api_key: str) -> dict:
    """Analyze a zoning application against applicable regulations."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = ZONING_PROMPT.format(**config)
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
