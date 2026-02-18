"""Personalized Learning Path Generator engine."""

import json
import anthropic

LEARNING_PATH_PROMPT = """\
You are an expert instructional designer and education technologist. Create a \
personalized learning path based on the student's profile, goals, and current \
knowledge level. Generate a structured curriculum with adaptive recommendations.

Return a JSON object:

{{
  "learner_assessment": {{
    "current_level": "Beginner | Intermediate | Advanced",
    "learning_style_suggestion": "Visual | Auditory | Reading/Writing | Kinesthetic | Mixed",
    "estimated_completion": "Total estimated time to reach goals",
    "readiness_score": <1-100>,
    "strengths": ["area of strength 1", "area of strength 2"],
    "gaps": ["knowledge gap 1", "knowledge gap 2"]
  }},

  "learning_path": {{
    "title": "Path title",
    "description": "Overview of what this path covers",
    "total_modules": <number>,
    "total_hours": <number>,

    "modules": [
      {{
        "module_number": <num>,
        "title": "Module title",
        "description": "What you'll learn",
        "duration_hours": <number>,
        "difficulty": "Beginner | Intermediate | Advanced",
        "prerequisites": ["previous module or skill needed"],
        "learning_objectives": ["objective 1", "objective 2"],
        "topics": [
          {{
            "topic": "Topic name",
            "type": "Concept | Hands-on | Project | Assessment",
            "estimated_minutes": <number>,
            "resources": [
              {{"type": "Video | Article | Book | Course | Tool", "title": "Resource name",
                "description": "What it covers"}}
            ]
          }}
        ],
        "milestone_project": {{
          "title": "Project name",
          "description": "What to build/do",
          "skills_applied": ["skill 1", "skill 2"]
        }},
        "assessment": {{
          "type": "Quiz | Project Review | Peer Review | Self-Assessment",
          "passing_criteria": "What counts as passing"
        }}
      }}
    ]
  }},

  "practice_questions": [
    {{
      "question": "Practice question text",
      "topic": "Which module/topic this tests",
      "difficulty": "Easy | Medium | Hard",
      "choices": {{"A": "choice", "B": "choice", "C": "choice", "D": "choice"}},
      "correct_answer": "A|B|C|D",
      "explanation": "Why this is correct"
    }}
  ],

  "study_schedule": {{
    "recommended_pace": "Intensive (20+ hrs/wk) | Standard (10-15 hrs/wk) | Part-time (5-8 hrs/wk)",
    "weekly_breakdown": [
      {{"week": <num>, "focus": "What to study", "hours": <num>, "deliverable": "What to complete"}}
    ],
    "study_tips": ["tip 1", "tip 2"],
    "accountability_suggestions": ["suggestion 1"]
  }},

  "motivation": {{
    "career_relevance": "How this path connects to career goals",
    "quick_wins": ["early achievements to build momentum"],
    "community_suggestions": ["ways to connect with other learners"]
  }}
}}

Create a comprehensive, actionable learning path. Be specific with resource suggestions.

IMPORTANT: Return ONLY the JSON object.

---

LEARNER PROFILE:
- Name: {name}
- Current Role: {current_role}
- Goal: {goal}
- Subject Area: {subject}
- Current Knowledge: {current_knowledge}
- Available Time: {available_time}
- Learning Preference: {preference}
- Deadline/Timeline: {deadline}
- Budget: {budget}
- Additional Context: {context}
"""


def generate_learning_path(config: dict, api_key: str) -> dict:
    """Generate a personalized learning path."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = LEARNING_PATH_PROMPT.format(**config)
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
