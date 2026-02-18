"""SmartSchool Reviser engine - Newsletter to revision activities."""

import json
import anthropic

REVISER_PROMPT = """\
You are an expert educational content designer for K-12 students. Parse school \
newsletters from teachers and generate structured revision activities, quizzes, \
and study guides that parents can use at home to reinforce classroom learning.

Return a JSON object:

{{
  "newsletter_summary": {{
    "school_name": "Extracted school name",
    "period": "Newsletter period",
    "grades_covered": ["grade levels mentioned"],
    "subject_count": <number>,
    "key_topics": ["main topics being taught"]
  }},

  "subjects": [
    {{
      "subject": "Subject name",
      "grade": "Grade level",
      "teacher": "Teacher name if mentioned",
      "current_topics": ["what's being taught"],
      "upcoming_topics": ["what's coming next"],
      "revision_activities": [
        {{
          "activity": "Activity description",
          "type": "Quiz | Discussion | Hands-on | Worksheet | Game | Reading",
          "difficulty": "Easy | Medium | Hard",
          "time_needed": "X minutes",
          "materials_needed": ["any materials"],
          "parent_instructions": "How parents can facilitate this"
        }}
      ],
      "quiz_questions": [
        {{
          "question": "Question text",
          "type": "Multiple Choice | Short Answer | True/False",
          "options": ["if multiple choice"],
          "answer": "Correct answer",
          "explanation": "Why this is correct"
        }}
      ],
      "vocabulary": [
        {{"term": "Term", "definition": "Simple definition", "example": "Usage example"}}
      ],
      "parent_tips": "How parents can support learning in this area"
    }}
  ],

  "weekly_schedule": [
    {{
      "day": "Monday | Tuesday | etc.",
      "subject": "Subject to revise",
      "activity": "Suggested activity",
      "duration": "X minutes"
    }}
  ],

  "conversation_starters": [
    "Questions parents can ask kids about what they learned"
  ],

  "resources": [
    {{"resource": "Name", "type": "Website | Book | App | Video",
      "subject": "Related subject", "link_or_description": "Where to find it"}}
  ]
}}

Make activities age-appropriate, engaging, and practical for busy parents. Focus \
on reinforcement rather than introducing new concepts.

IMPORTANT: Return ONLY the JSON object.

---

NEWSLETTER CONTENT:
{newsletters}

PARAMETERS:
- Child's Grade: {grade}
- Child's Strengths: {strengths}
- Areas Needing Help: {weaknesses}
- Available Time: {available_time}
- Learning Style Preference: {learning_style}
"""


def generate_revision(config: dict, api_key: str) -> dict:
    """Generate revision activities from school newsletters."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = REVISER_PROMPT.format(**config)
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
