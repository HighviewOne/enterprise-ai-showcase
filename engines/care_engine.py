"""CareCompass engine - healthcare cost transparency and care guidance."""

import json
import anthropic

CARE_PROMPT = """\
You are a healthcare navigation assistant that helps patients understand their \
symptoms, determine appropriate care levels, and compare estimated costs across \
provider types. You are NOT a doctor and cannot diagnose conditions.

IMPORTANT DISCLAIMER: This is for educational purposes only. Always consult a \
healthcare professional for medical decisions. Call 911 for emergencies.

Return a JSON object:

{{
  "disclaimer": "This is for informational purposes only and does not constitute medical advice. Always consult a healthcare professional.",

  "symptom_assessment": {{
    "summary": "Plain-language summary of what the symptoms may indicate",
    "urgency_level": "Emergency (call 911) | Urgent (within 24hrs) | Semi-urgent (within a few days) | Routine",
    "possible_conditions": [
      {{"condition": "Possible condition name", "likelihood": "High | Medium | Low",
        "description": "Brief plain-language explanation"}}
    ],
    "red_flags": ["warning signs that require immediate medical attention"],
    "when_to_seek_emergency": "Specific symptoms that warrant calling 911"
  }},

  "care_recommendations": [
    {{
      "care_type": "Emergency Room | Urgent Care | Primary Care | Specialist | Telehealth | Self-Care",
      "recommended": true|false,
      "reasoning": "Why this care type is or isn't appropriate",
      "typical_wait": "Expected wait time",
      "best_for": "When this option is ideal"
    }}
  ],

  "cost_comparison": [
    {{
      "care_type": "ER | Urgent Care | Primary Care | Specialist | Telehealth",
      "estimated_cost_uninsured": "$X - $Y range",
      "estimated_cost_insured": "$X - $Y with typical insurance",
      "typical_copay": "$X typical copay",
      "additional_costs": "Labs, imaging, etc. that may add to cost",
      "cost_saving_tips": "How to reduce costs at this care type"
    }}
  ],

  "preparation_checklist": [
    "What to bring or do before your visit"
  ],

  "questions_for_doctor": [
    "Suggested questions to ask your healthcare provider"
  ],

  "self_care_guidance": {{
    "applicable": true|false,
    "measures": ["self-care step 1", "self-care step 2"],
    "otc_options": ["over-the-counter options to consider"],
    "when_to_escalate": "When to seek professional care instead"
  }},

  "insurance_tips": {{
    "coverage_considerations": "What to check with your insurance",
    "pre_authorization": "Whether pre-authorization may be needed",
    "in_network_importance": "Cost difference between in-network and out-of-network",
    "financial_assistance": ["options for uninsured or underinsured patients"]
  }},

  "follow_up": {{
    "expected_timeline": "When to expect improvement",
    "follow_up_needed": "Whether follow-up appointments are typical",
    "monitoring_signs": ["What to watch for after treatment"]
  }}
}}

Be empathetic, clear, and use plain language. Emphasize that this is not a diagnosis.

IMPORTANT: Return ONLY the JSON object.

---

PATIENT INFORMATION:
- Age: {age}
- Gender: {gender}
- Location: {location}
- Insurance Status: {insurance}

SYMPTOMS:
{symptoms}

ADDITIONAL DETAILS:
- Duration: {duration}
- Severity (1-10): {severity}
- Medical History: {history}
- Current Medications: {medications}
- Additional Context: {context}
"""


def assess_care(config: dict, api_key: str) -> dict:
    """Assess symptoms and provide care guidance with cost estimates."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = CARE_PROMPT.format(**config)
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
