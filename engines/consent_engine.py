"""Clinical Consent engine - AI-powered consent form analysis for patients."""

import json
import anthropic

CONSENT_PROMPT = """\
You are an expert in health literacy, clinical trial informed consent, and patient advocacy. \
Analyze the clinical trial consent form and transform it into accessible, patient-friendly \
content tailored to the patient's profile.

Return a JSON object:

{{
  "consent_summary": {{
    "trial_name": "Name of the clinical trial",
    "trial_phase": "Phase I | Phase II | Phase III | Phase IV",
    "sponsor": "Trial sponsor organization",
    "purpose": "Plain-language explanation of why this trial exists",
    "what_is_being_tested": "Simple explanation of the treatment/drug",
    "duration": "How long participation lasts",
    "participant_count": "How many people are in this trial",
    "plain_language_summary": "2-3 paragraph summary a {education_level} educated person can understand"
  }},

  "key_risks": [
    {{
      "risk": "Risk description in plain language",
      "severity": "Serious | Moderate | Mild",
      "likelihood": "Common | Uncommon | Rare | Very Rare",
      "plain_explanation": "What this means in everyday terms",
      "what_doctors_will_do": "How the medical team monitors/manages this risk"
    }}
  ],

  "benefits_explained": {{
    "potential_benefits": ["Plain-language benefit descriptions"],
    "likelihood_of_benefit": "Honest assessment of benefit probability",
    "compared_to_standard_care": "How this compares to not joining the trial",
    "who_benefits_most": "Profile of patients most likely to benefit"
  }},

  "procedures_timeline": [
    {{
      "phase": "Screening | Treatment | Follow-up",
      "timeframe": "When this happens",
      "procedures": ["What happens during this phase"],
      "visits_required": "Number and frequency of visits",
      "time_commitment": "Hours per visit or total time"
    }}
  ],

  "rights_and_protections": {{
    "voluntary_participation": "Explanation that joining is completely voluntary",
    "right_to_withdraw": "Can leave at any time without penalty",
    "confidentiality": "How personal information is protected",
    "compensation": "Payment or reimbursement details",
    "injury_provisions": "What happens if you are harmed",
    "contact_information": "Who to call with questions or concerns",
    "irb_oversight": "Explanation of ethics board oversight"
  }},

  "faq": [
    {{
      "question": "Common patient question",
      "answer": "Clear, honest answer"
    }}
  ],

  "readability_assessment": {{
    "original_reading_level": "Estimated grade level of original consent",
    "recommended_reading_level": "What reading level it should be for this patient",
    "jargon_terms_found": ["Medical jargon in the original that needs explanation"],
    "complexity_score": <1-10>,
    "accessibility_grade": "A | B | C | D | F"
  }},

  "accessibility_notes": {{
    "language_considerations": "Notes on language accessibility for {language_preference} speakers",
    "cultural_sensitivity": "Cultural considerations for this patient",
    "visual_aids_recommended": ["Suggestions for diagrams or visual aids"],
    "simplified_version_needed": true or false,
    "interpreter_recommended": true or false
  }},

  "decision_support": {{
    "pros": ["Reasons to consider joining"],
    "cons": ["Reasons to consider not joining"],
    "questions_to_ask_doctor": ["Important questions for the patient to ask"],
    "things_to_discuss_with_family": ["Topics to discuss with loved ones"],
    "decision_timeline": "How long patient has to decide",
    "alternatives": ["Alternative options if patient does not join"]
  }},

  "red_flags": [
    {{
      "concern": "Issue found in the consent form",
      "severity": "High | Medium | Low",
      "explanation": "Why this is concerning",
      "recommendation": "What the patient should ask about"
    }}
  ]
}}

Prioritize clarity, honesty, and patient empowerment. Adjust language complexity to match \
the patient's education level ({education_level}) and health literacy ({health_literacy}).

IMPORTANT: Return ONLY the JSON object.

---

CLINICAL TRIAL CONSENT FORM:
{consent_text}

PATIENT PROFILE:
- Age: {patient_age}
- Education Level: {education_level}
- Language Preference: {language_preference}
- Health Literacy Level: {health_literacy}
"""


def analyze_consent(config: dict, api_key: str) -> dict:
    """Analyze a clinical trial consent form and generate patient-friendly content."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = CONSENT_PROMPT.format(**config)
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
