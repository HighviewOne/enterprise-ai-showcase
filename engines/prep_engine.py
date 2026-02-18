"""Medical Procedure Prep engine - Pre-procedure patient guidance."""

import json
import anthropic

PREP_PROMPT = """\
You are a compassionate, expert medical procedure preparation assistant. Help the \
patient understand their upcoming procedure, reduce anxiety, and provide clear \
preparation guidance. Use plain language and be reassuring while being thorough.

Return a JSON object:

{{
  "procedure_overview": {{
    "procedure_name": "Full name",
    "common_name": "What patients call it",
    "purpose": "Why this procedure is done",
    "duration": "Expected duration",
    "anesthesia_type": "Type of anesthesia",
    "setting": "Outpatient | Inpatient | Day Surgery",
    "what_to_expect": "Plain-English step-by-step of what happens"
  }},

  "preparation_timeline": [
    {{
      "timeframe": "e.g. 1 week before, Day before, Morning of",
      "tasks": ["specific preparation steps"],
      "important_notes": "Key reminders"
    }}
  ],

  "dietary_instructions": {{
    "fasting_required": true|false,
    "fasting_start": "When to stop eating/drinking",
    "allowed_before": ["what's OK to consume"],
    "restricted": ["what to avoid"],
    "day_of_instructions": "Morning-of food/drink rules"
  }},

  "medication_guidance": {{
    "general_advice": "Overall medication guidance",
    "usually_continue": ["medications typically OK to take"],
    "usually_stop": ["medications typically stopped before procedure"],
    "important_warning": "Reminder to confirm with their doctor"
  }},

  "what_to_bring": ["list of items to bring"],

  "anxiety_management": {{
    "common_concerns": [
      {{"concern": "Patient worry", "reassurance": "Helpful response", "tip": "Coping strategy"}}
    ],
    "relaxation_techniques": ["breathing exercises, visualization, etc."],
    "questions_for_doctor": ["good questions to ask the care team"]
  }},

  "recovery_expectations": {{
    "immediate_after": "What happens right after",
    "first_24_hours": "Day 1 expectations",
    "first_week": "Week 1 recovery",
    "full_recovery": "Timeline to full recovery",
    "activity_restrictions": ["things to avoid during recovery"],
    "warning_signs": ["symptoms that need immediate medical attention"]
  }},

  "logistics": {{
    "arrival_time": "When to arrive",
    "companion_needed": true|false,
    "driving_restriction": "Can they drive after?",
    "time_off_work": "Recommended time off",
    "follow_up": "When to expect follow-up appointment"
  }},

  "checklist": [
    {{"item": "Checklist item", "category": "Before | Day-of | After", "done": false}}
  ],

  "reassuring_note": "Final encouraging message for the patient"
}}

Be warm, supportive, and clear. Use simple language. Always remind patients to \
confirm specific instructions with their healthcare provider.

IMPORTANT: Return ONLY the JSON object.

---

PATIENT INFORMATION:
Procedure: {procedure}
Patient Age: {age}
Date Scheduled: {date}
Doctor/Facility: {facility}
Medical Conditions: {conditions}
Current Medications: {medications}
Allergies: {allergies}
First Time Having This Procedure: {first_time}
Specific Concerns: {concerns}
"""


def prepare_guidance(config: dict, api_key: str) -> dict:
    """Generate pre-procedure patient guidance."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = PREP_PROMPT.format(**config)
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
