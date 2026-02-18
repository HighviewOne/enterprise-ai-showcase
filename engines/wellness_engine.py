"""AI Wellness & Nutrition engine - biomarker analysis and supplement recommendations."""

import json
import anthropic

WELLNESS_PROMPT = """\
You are an expert nutritionist and wellness consultant. Analyze the provided lab \
results and health profile to identify nutritional deficiencies and recommend \
personalized supplements, dietary changes, and wellness strategies.

IMPORTANT: This is for educational purposes only. Not medical advice. Always \
consult a healthcare provider before starting supplements.

Return a JSON object:

{{
  "disclaimer": "For educational purposes only. Consult your healthcare provider before making changes.",

  "health_overview": {{
    "wellness_score": <1-100>,
    "overall_status": "Optimal | Good | Needs Attention | Concerning",
    "summary": "One-paragraph health overview based on biomarkers",
    "top_priorities": ["priority 1", "priority 2", "priority 3"]
  }},

  "biomarker_analysis": [
    {{
      "biomarker": "Biomarker name",
      "value": "Reported value with units",
      "normal_range": "Reference range",
      "status": "Optimal | Normal | Borderline Low | Low | Borderline High | High",
      "significance": "What this marker means for health",
      "related_symptoms": ["symptom this could cause"],
      "dietary_connection": "How diet affects this marker"
    }}
  ],

  "deficiencies_detected": [
    {{
      "nutrient": "Nutrient name",
      "severity": "Mild | Moderate | Severe",
      "evidence": "What in the labs suggests this",
      "health_impact": "How this deficiency affects health",
      "food_sources": ["food rich in this nutrient"],
      "supplement_recommendation": {{
        "product_type": "Supplement name/type",
        "suggested_dose": "Dosage",
        "form": "Best form (e.g., methylfolate vs folic acid)",
        "timing": "When to take it",
        "duration": "How long to supplement",
        "interactions": ["drug or nutrient interactions to watch"]
      }}
    }}
  ],

  "nutrition_plan": {{
    "dietary_pattern": "Recommended eating pattern",
    "foods_to_increase": [
      {{"food": "Food name", "benefit": "Why it helps", "serving": "Recommended amount"}}
    ],
    "foods_to_limit": [
      {{"food": "Food name", "reason": "Why to limit", "alternative": "Better option"}}
    ],
    "hydration": "Water intake recommendation",
    "meal_timing": "Eating schedule suggestion"
  }},

  "lifestyle_recommendations": [
    {{
      "category": "Exercise | Sleep | Stress | Gut Health | Detox",
      "recommendation": "What to do",
      "rationale": "Why it helps based on the labs",
      "priority": "High | Medium | Low"
    }}
  ],

  "supplement_stack": {{
    "morning": [
      {{"supplement": "Name", "dose": "Amount", "with_food": true|false, "notes": "Tips"}}
    ],
    "afternoon": [
      {{"supplement": "Name", "dose": "Amount", "with_food": true|false, "notes": "Tips"}}
    ],
    "evening": [
      {{"supplement": "Name", "dose": "Amount", "with_food": true|false, "notes": "Tips"}}
    ],
    "estimated_monthly_cost": "$X - $Y range",
    "priority_order": ["Most important supplement first"]
  }},

  "retest_plan": {{
    "recommended_retest": "When to retest labs",
    "markers_to_recheck": ["biomarker to monitor"],
    "expected_improvement_timeline": "When to expect changes"
  }}
}}

Be evidence-based and conservative with supplement recommendations.

IMPORTANT: Return ONLY the JSON object.

---

PATIENT PROFILE:
- Age: {age}, Gender: {gender}
- Height: {height}, Weight: {weight}
- Activity Level: {activity_level}
- Diet Type: {diet_type}
- Health Goals: {goals}
- Current Supplements: {current_supplements}
- Known Conditions: {conditions}
- Symptoms: {symptoms}

LAB RESULTS:
{lab_results}

ADDITIONAL CONTEXT: {context}
"""


def analyze_wellness(config: dict, api_key: str) -> dict:
    """Analyze lab results and generate wellness recommendations."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = WELLNESS_PROMPT.format(**config)
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
