"""SmartSchool Reviser engine - Newsletter to revision activities."""

from engines.llm import call_claude_json

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
    prompt = REVISER_PROMPT.format(**config)
    return call_claude_json(prompt, api_key, max_tokens=4096)
