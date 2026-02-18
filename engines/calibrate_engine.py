"""Calibrate engine - AI-powered job search leverage and career positioning."""

import json
import anthropic

CALIBRATE_PROMPT = """\
You are an expert career strategist and executive recruiter. Analyze the professional profile \
and generate a comprehensive career positioning strategy that helps them find roles where they \
are the obvious choice, not the long shot.

Return a JSON object:

{{
  "professional_identity": {{
    "value_proposition": "One compelling sentence summarizing their unique value",
    "career_narrative": "The story their career tells",
    "differentiators": ["What sets them apart from other candidates"],
    "personal_brand_keywords": ["Keywords that define their brand"],
    "elevator_pitch": "30-second pitch for networking"
  }},

  "strength_mapping": {{
    "core_competencies": [
      {{"skill": "Skill name", "proficiency": <1-10>, "evidence": "How this is demonstrated",
        "market_demand": "High | Medium | Low"}}
    ],
    "hidden_strengths": ["Strengths they may undervalue"],
    "transferable_skills": ["Skills that apply across industries"]
  }},

  "market_positioning": {{
    "current_market_tier": "Senior | Staff | Principal | Director | VP | C-Level",
    "optimal_positioning": "Where they should aim",
    "market_demand_level": "High | Medium | Low",
    "supply_assessment": "How many similar candidates exist",
    "geographic_considerations": "Location-based insights",
    "timing_assessment": "Current market conditions for their profile"
  }},

  "target_role_analysis": [
    {{"role_title": "Title", "fit_score": <1-100>, "why_good_fit": "Explanation",
      "typical_company_size": "Startup | Mid-size | Enterprise",
      "compensation_range": "Expected salary range",
      "growth_trajectory": "Where this role leads in 3-5 years",
      "competition_level": "Low | Medium | High"}}
  ],

  "company_archetypes": [
    {{"archetype": "Type of company", "why_match": "Why this type needs them",
      "example_companies": ["Company names"], "approach_strategy": "How to get in"}}
  ],

  "narrative_strategy": {{
    "resume_headline": "Compelling resume headline",
    "linkedin_summary_hook": "Opening line for LinkedIn",
    "story_themes": ["Key themes to weave into interviews"],
    "achievement_framing": ["How to frame key achievements for maximum impact"],
    "gap_explanations": ["How to address any career gaps or transitions"]
  }},

  "application_priorities": [
    {{"priority": <1-5>, "category": "Role category", "effort_level": "Low | Medium | High",
      "expected_response_rate": "Percentage", "strategy": "Approach for this category"}}
  ],

  "networking_targets": [
    {{"target_type": "Type of person or community", "why_valuable": "How they help",
      "where_to_find": "Platforms or events", "approach": "How to reach out"}}
  ],

  "skills_gaps": [
    {{"gap": "Skill or credential", "importance": "Critical | Important | Nice-to-Have",
      "investment": "Time and cost to acquire", "roi": "Expected career impact",
      "resources": ["Where to learn"]}}
  ],

  "salary_benchmarking": {{
    "current_market_rate": "Range for their current level",
    "target_role_range": "Range for target roles",
    "negotiation_leverage": ["Factors that strengthen their negotiating position"],
    "total_comp_considerations": ["Equity, benefits, bonuses to factor in"],
    "geographic_adjustments": "Location-based salary notes"
  }},

  "action_plan": {{
    "week_1_2": ["Immediate actions"],
    "week_3_4": ["Short-term actions"],
    "month_2": ["Medium-term actions"],
    "month_3_plus": ["Ongoing actions"],
    "daily_habits": ["Daily job search habits to maintain"],
    "metrics_to_track": ["How to measure progress"]
  }}
}}

Be encouraging but honest. Focus on leverage points and strategic advantages. Avoid generic advice.

IMPORTANT: Return ONLY the JSON object.

---

PROFESSIONAL PROFILE:
{professional_profile}

CAREER ASPIRATIONS:
{aspirations}

TARGET ROLES:
{target_roles}

CONSTRAINTS:
- Location: {location}
- Salary Range: {salary_range}
- Remote Preference: {remote_preference}

WHAT MAKES THEM UNIQUE:
{unique_factors}
"""


def analyze_career(config: dict, api_key: str) -> dict:
    """Analyze professional profile and generate career positioning strategy."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = CALIBRATE_PROMPT.format(**config)
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
