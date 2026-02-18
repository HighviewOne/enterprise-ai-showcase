"""AI Visa Application Agent engine - B1/B2 visa guidance."""

import json
import anthropic

VISA_PROMPT = """\
You are an expert US visa application consultant specialising in B1/B2 (business/tourist) \
visa applications. Analyse the applicant's profile and provide comprehensive guidance for \
their DS-160 application, interview preparation, and consulate process.

Return a JSON object:

{{
  "applicant_assessment": {{
    "eligibility_rating": "Strong | Moderate | Weak",
    "visa_type_recommendation": "B1 | B2 | B1/B2",
    "risk_level": "Low | Medium | High",
    "risk_factors": ["list of risk factors identified"],
    "strengths": ["factors supporting approval"],
    "overall_assessment": "Detailed eligibility narrative"
  }},

  "ds160_guidance": [
    {{
      "section": "DS-160 section name",
      "fields": [
        {{"field": "Field name", "guidance": "What to enter and why", "tip": "Helpful tip"}}
      ]
    }}
  ],

  "document_checklist": [
    {{"document": "Document name", "required": true|false, "status": "Required | Recommended | Optional",
      "notes": "Specific notes for this applicant"}}
  ],

  "interview_preparation": {{
    "common_questions": [
      {{"question": "Likely interview question", "recommended_approach": "How to answer",
        "sample_answer": "Example answer", "pitfalls": "What to avoid"}}
    ],
    "general_tips": ["overall interview tips"],
    "dress_code": "Recommendation",
    "timing": "When to arrive"
  }},

  "consulate_guidance": {{
    "recommended_consulate": "City",
    "appointment_tips": "How to get an appointment",
    "drop_off_eligibility": true|false,
    "drop_off_details": "Explanation of eligibility for interview waiver",
    "processing_time": "Expected wait",
    "emergency_appointment": "How to request if needed"
  }},

  "timeline": [
    {{"step": "Step description", "timeframe": "When to do it", "notes": "Details"}}
  ],

  "common_mistakes": [
    {{"mistake": "What people do wrong", "consequence": "What happens", "prevention": "How to avoid"}}
  ],

  "overall_recommendation": "Final summary and recommended next steps"
}}

Be thorough, practical, and supportive. Focus on maximising the applicant's chances of \
approval with honest, evidence-based advice.

IMPORTANT: Return ONLY the JSON object.

---

APPLICANT PROFILE:
Full Name: {full_name}
Date of Birth: {dob}
Nationality: {nationality}
Passport Number: {passport_number}
Purpose of Visit: {purpose}
US Sponsor/Host: {sponsor}
Employment Status: {employment_status}
Occupation: {occupation}
Employer: {employer}
Monthly Income (USD): {monthly_income}
Savings/Assets: {savings}
Previous US Visa: {previous_visa}
Travel History (5 years): {travel_history}
Intended Stay Duration: {duration}
Preferred Consulate: {consulate}
Additional Information: {additional_info}
"""


def analyze_application(config: dict, api_key: str) -> dict:
    """Analyse visa application and provide guidance."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = VISA_PROMPT.format(**config)
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
