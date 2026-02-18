"""Concept Mastery Grader engine - Process-based concept evaluation."""

import json
import anthropic

GRADER_PROMPT = """\
You are an expert educational assessor. Grade the student's work based on CONCEPTUAL \
MASTERY, not just the final answer. In the AI era, correct final answers don't prove \
understanding. Evaluate the reasoning process, concept application, and depth of thought.

Return a JSON object:

{{
  "overall_assessment": {{
    "grade": "A | B | C | D | F",
    "score": <1-100>,
    "mastery_level": "Expert | Proficient | Developing | Beginning | Not Demonstrated",
    "summary": "Overall assessment narrative",
    "ai_likelihood_score": <1-10 where 10 means likely AI-generated>
  }},

  "concept_evaluation": [
    {{
      "concept": "Concept being evaluated",
      "mastery": "Mastered | Developing | Not Demonstrated",
      "score": <1-10>,
      "evidence_of_understanding": ["what shows genuine understanding"],
      "evidence_of_gaps": ["what suggests gaps"],
      "feedback": "Specific feedback for this concept"
    }}
  ],

  "reasoning_analysis": {{
    "logical_flow": {{"score": <1-10>, "evidence": "How well ideas connect"}},
    "depth_of_analysis": {{"score": <1-10>, "evidence": "How deep the thinking goes"}},
    "original_thinking": {{"score": <1-10>, "evidence": "Unique perspectives or connections"}},
    "application_ability": {{"score": <1-10>, "evidence": "Can apply concepts to new situations"}},
    "misconceptions_detected": ["any conceptual errors found"]
  }},

  "rubric_scores": [
    {{
      "criterion": "Rubric criterion",
      "max_points": <number>,
      "points_earned": <number>,
      "justification": "Why this score"
    }}
  ],

  "inline_feedback": [
    {{
      "quote": "Excerpt from student work",
      "type": "Strength | Weakness | Misconception | Needs Clarification",
      "comment": "Specific feedback"
    }}
  ],

  "improvement_suggestions": [
    {{
      "area": "What to improve",
      "current_level": "Where student is now",
      "target_level": "Where they should aim",
      "specific_action": "Concrete step to improve"
    }}
  ],

  "follow_up_questions": [
    "Questions to ask the student to verify understanding"
  ],

  "instructor_notes": "Private notes for the instructor about this submission"
}}

Be constructive, specific, and evidence-based. Distinguish between surface-level \
correctness and genuine conceptual understanding.

IMPORTANT: Return ONLY the JSON object.

---

ASSIGNMENT:
Subject: {subject}
Topic: {topic}
Assignment Prompt: {prompt}
Grade Level: {grade_level}
Expected Concepts: {concepts}

STUDENT SUBMISSION:
{submission}

GRADING PARAMETERS:
- Grading Rubric Focus: {rubric_focus}
- Strictness: {strictness}
"""


def grade_submission(config: dict, api_key: str) -> dict:
    """Grade student submission for concept mastery."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = GRADER_PROMPT.format(**config)
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
