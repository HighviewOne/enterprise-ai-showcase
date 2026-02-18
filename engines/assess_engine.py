"""Conversational Assessment engine - AI-era critical thinking evaluation."""

import json
import anthropic

ASSESS_SYSTEM = """\
You are an expert educational assessor specialising in Socratic dialogue and process-based \
evaluation. Your role is to assess a student's understanding through conversation, focusing \
on HOW they think, not just WHAT they answer. Detect whether they truly understand concepts \
or are producing surface-level answers that could come from an LLM.

Probe for:
- Reasoning process and mental models
- Ability to connect concepts
- Capacity to apply knowledge to novel situations
- Self-awareness about gaps in understanding
- Original thinking vs. recitation

Always respond in JSON format:

{
  "response_to_student": "Your conversational response (Socratic questions, follow-ups, challenges)",
  "assessment_notes": {
    "understanding_signals": ["what suggests genuine understanding"],
    "concern_signals": ["what suggests surface-level knowledge"],
    "concepts_probed": ["concepts being tested"],
    "depth_level": "Surface | Developing | Solid | Expert",
    "next_probe": "What to explore next to deepen assessment"
  },
  "running_score": {
    "critical_thinking": <1-10>,
    "conceptual_depth": <1-10>,
    "application_ability": <1-10>,
    "self_awareness": <1-10>,
    "originality": <1-10>
  }
}

IMPORTANT: Return ONLY the JSON object."""

FINAL_PROMPT = """\
Based on the entire conversation, generate a final comprehensive assessment.

Return a JSON object:

{
  "final_assessment": {
    "overall_grade": "A | B | C | D | F",
    "overall_score": <1-100>,
    "understanding_level": "Expert | Proficient | Developing | Novice",
    "summary": "Overall assessment narrative",
    "strengths": ["demonstrated strengths"],
    "areas_for_growth": ["areas needing improvement"],
    "concept_mastery": [
      {"concept": "Concept name", "mastery": "Mastered | Developing | Not Demonstrated",
       "evidence": "Evidence from conversation"}
    ],
    "thinking_patterns": {
      "critical_thinking": {"score": <1-10>, "evidence": "observed examples"},
      "conceptual_depth": {"score": <1-10>, "evidence": "observed examples"},
      "application_ability": {"score": <1-10>, "evidence": "observed examples"},
      "self_awareness": {"score": <1-10>, "evidence": "observed examples"},
      "originality": {"score": <1-10>, "evidence": "observed examples"}
    },
    "recommendations": ["specific learning recommendations"],
    "educator_notes": "Notes for the instructor"
  }
}

IMPORTANT: Return ONLY the JSON object."""


def get_assessment_response(messages: list, subject: str, topic: str, api_key: str) -> dict:
    """Get conversational assessment response."""
    client = anthropic.Anthropic(api_key=api_key)
    system = (ASSESS_SYSTEM + f"\n\nSubject: {subject}\nTopic: {topic}\n"
              "Assess the student's understanding through Socratic dialogue.")
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2048,
        system=system,
        messages=messages,
    )
    text = message.content[0].text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return json.loads(text)


def get_final_assessment(messages: list, subject: str, topic: str, api_key: str) -> dict:
    """Generate final assessment report."""
    client = anthropic.Anthropic(api_key=api_key)
    system = ASSESS_SYSTEM + f"\n\nSubject: {subject}\nTopic: {topic}"
    final_messages = messages + [{"role": "user", "content": FINAL_PROMPT}]
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        system=system,
        messages=final_messages,
    )
    text = message.content[0].text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return json.loads(text)
