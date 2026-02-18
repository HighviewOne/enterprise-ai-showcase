"""AI Medical Documentation engine - generates clinical notes from conversations."""

import json
import anthropic

CLINICAL_NOTE_PROMPT = """\
You are an expert medical documentation specialist and clinical scribe.
Given a doctor-patient conversation transcript, generate a comprehensive structured
clinical note.

IMPORTANT: This is for educational/demonstration purposes only. Not for actual clinical use.

Return a JSON object:

{{
  "disclaimer": "For educational purposes only. Not for clinical use.",
  "patient_summary": {{
    "chief_complaint": "Primary reason for visit in patient's words",
    "visit_type": "New Patient | Follow-up | Urgent | Telehealth | Annual Physical",
    "urgency": "Routine | Semi-urgent | Urgent | Emergency"
  }},

  "soap_note": {{
    "subjective": {{
      "history_of_present_illness": "Detailed narrative of current issue",
      "review_of_systems": [
        {{"system": "System name", "findings": "Positive/negative findings"}}
      ],
      "past_medical_history": ["condition 1", "condition 2"],
      "medications": ["medication 1 with dose", "medication 2 with dose"],
      "allergies": ["allergy 1"],
      "social_history": "Relevant social factors",
      "family_history": "Relevant family history"
    }},
    "objective": {{
      "vital_signs": "Any mentioned vitals or 'Not documented'",
      "physical_exam": [
        {{"area": "Exam area", "findings": "Findings"}}
      ],
      "lab_results": "Any mentioned labs or 'None ordered/documented'"
    }},
    "assessment": {{
      "diagnoses": [
        {{
          "condition": "Diagnosis name",
          "icd10_suggestion": "Suggested ICD-10 code",
          "status": "New | Chronic | Acute | Worsening | Improving",
          "confidence": "High | Medium | Low"
        }}
      ],
      "differential_diagnoses": ["differential 1", "differential 2"],
      "clinical_reasoning": "Brief reasoning for primary assessment"
    }},
    "plan": {{
      "treatments": [
        {{"action": "Treatment description", "details": "Specifics"}}
      ],
      "medications_prescribed": [
        {{"name": "Drug name", "dose": "Dosage", "frequency": "Frequency", "duration": "Duration"}}
      ],
      "labs_ordered": ["lab test 1"],
      "referrals": ["referral 1"],
      "follow_up": "Follow-up instructions",
      "patient_education": ["education point 1", "education point 2"]
    }}
  }},

  "coding_suggestions": {{
    "cpt_codes": [
      {{"code": "CPT code", "description": "What it covers", "rationale": "Why suggested"}}
    ],
    "icd10_codes": [
      {{"code": "ICD-10 code", "description": "Diagnosis", "rationale": "Supporting evidence"}}
    ],
    "visit_level": "E&M level suggestion (e.g., 99213, 99214)",
    "level_justification": "Why this E&M level"
  }},

  "quality_flags": {{
    "missing_information": ["info that should be documented but wasn't mentioned"],
    "safety_alerts": ["any medication interactions, allergy concerns, red flags"],
    "documentation_tips": ["suggestions to improve the note"]
  }}
}}

Use your medical knowledge to fill in reasonable suggestions. Be thorough but accurate.
If information is not in the transcript, note it as "Not documented" rather than fabricating.

IMPORTANT: Return ONLY the JSON object.

---

CONVERSATION TRANSCRIPT:
{transcript}

VISIT CONTEXT:
- Specialty: {specialty}
- Setting: {setting}
- Additional Notes: {notes}
"""


def generate_clinical_note(config: dict, api_key: str) -> dict:
    """Generate a structured clinical note from a conversation transcript."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = CLINICAL_NOTE_PROMPT.format(**config)
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
