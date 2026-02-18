"""Patient Advocate engine - Health advocacy, cost optimization, and care coordination."""

import json
import anthropic

ADVOCATE_PROMPT = """\
You are an expert patient health advocate with deep knowledge of medications, insurance \
optimization, patient assistance programs, and care coordination. Analyze the patient scenario \
and provide comprehensive advocacy guidance to reduce costs and improve care.

Return a JSON object:

{{
  "medication_review": [
    {{
      "medication": "Drug name",
      "dosage": "Current dosage",
      "purpose": "What it treats in plain language",
      "how_it_works": "Simple explanation of mechanism",
      "common_side_effects": ["side effects to watch for"],
      "interactions": ["interactions with other listed meds or foods"],
      "importance": "Critical | Important | Supportive"
    }}
  ],

  "cost_analysis": [
    {{
      "medication": "Drug name",
      "current_monthly_cost": <number>,
      "generic_alternative": "Generic name if available",
      "generic_monthly_cost": <number or null>,
      "therapeutic_alternatives": ["other drugs in same class that may be cheaper"],
      "patient_assistance_programs": ["available programs with eligibility notes"],
      "pharmacy_comparison": {{
        "retail": <number>,
        "mail_order": <number or null>,
        "costco": <number or null>,
        "goodrx_estimate": <number or null>
      }},
      "potential_monthly_savings": <number>
    }}
  ],

  "insurance_optimization": {{
    "formulary_tips": ["tips for working within insurance formulary"],
    "prior_auth_guidance": ["medications that may need prior authorization and how to get it"],
    "tier_optimization": ["ways to move to lower-cost tiers"],
    "appeal_strategies": ["how to appeal denials if applicable"],
    "total_potential_monthly_savings": <number>
  }},

  "care_coordination": {{
    "specialist_recommendations": [
      {{"specialist": "Type", "reason": "Why needed", "frequency": "How often"}}
    ],
    "screening_schedule": [
      {{"screening": "Test name", "frequency": "How often", "next_due": "When", "purpose": "Why important"}}
    ],
    "lab_schedule": [
      {{"lab_test": "Test name", "frequency": "How often", "what_it_monitors": "What we're tracking"}}
    ]
  }},

  "disease_education": [
    {{
      "condition": "Condition name",
      "plain_explanation": "What it is in simple terms",
      "lifestyle_modifications": ["actionable lifestyle changes"],
      "warning_signs": ["symptoms that need immediate attention"],
      "long_term_outlook": "Prognosis with proper management",
      "reliable_resources": ["trusted websites or organizations"]
    }}
  ],

  "questions_for_doctor": [
    {{
      "question": "The question to ask",
      "why_important": "Why this matters",
      "context": "Background for the patient"
    }}
  ],

  "savings_opportunities": {{
    "medication_savings": <number>,
    "insurance_optimization_savings": <number>,
    "pharmacy_savings": <number>,
    "assistance_program_savings": <number>,
    "total_potential_monthly_savings": <number>,
    "total_potential_annual_savings": <number>
  }},

  "resource_directory": [
    {{
      "resource": "Program or resource name",
      "type": "Patient Assistance | Discount Card | Support Group | Education | Financial Aid",
      "description": "What it offers",
      "eligibility": "Who qualifies",
      "contact": "How to access"
    }}
  ]
}}

Be empathetic, thorough, and practical. Use plain language the patient can understand. \
Always emphasize that medication changes should be discussed with their doctor.

IMPORTANT: Return ONLY the JSON object.

---

PATIENT SCENARIO:
{patient_scenario}

MEDICATIONS:
{medications}

DIAGNOSES:
{diagnoses}

INSURANCE TYPE:
{insurance_type}

CURRENT MONTHLY COSTS:
{current_costs}

SPECIFIC CONCERNS:
{concerns}
"""


def analyze_patient(config: dict, api_key: str) -> dict:
    """Analyze patient scenario and generate advocacy recommendations."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = ADVOCATE_PROMPT.format(**config)
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
