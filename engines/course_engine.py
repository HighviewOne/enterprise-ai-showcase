"""Smart Course Generator engine - automated course content creation."""

import json
import anthropic

COURSE_PROMPT = """\
You are an expert instructional designer and curriculum developer. Create a \
comprehensive course outline with detailed lesson content, assessments, and \
learning activities based on the specifications provided.

Return a JSON object:

{{
  "course_overview": {{
    "title": "Course title",
    "subtitle": "Course subtitle/tagline",
    "description": "2-3 sentence course description",
    "target_audience": "Who this course is for",
    "prerequisites": ["prerequisite 1"],
    "learning_outcomes": ["outcome 1 (students will be able to...)", "outcome 2"],
    "duration": "Total estimated duration",
    "difficulty": "Beginner | Intermediate | Advanced",
    "format": "{format}"
  }},

  "modules": [
    {{
      "module_number": <num>,
      "title": "Module title",
      "duration": "Estimated time",
      "overview": "What this module covers",
      "learning_objectives": ["specific measurable objective"],

      "lessons": [
        {{
          "lesson_number": <num>,
          "title": "Lesson title",
          "duration": "Estimated time",
          "content_outline": [
            "Key point or topic to cover with brief explanation"
          ],
          "instructor_notes": "Teaching tips and talking points",
          "activities": [
            {{"type": "Discussion | Exercise | Demo | Case Study | Group Work",
              "description": "Activity description",
              "duration": "Time needed"}}
          ],
          "resources": ["Recommended reading, tool, or reference"]
        }}
      ],

      "assessment": {{
        "type": "Quiz | Assignment | Project | Presentation | Peer Review",
        "title": "Assessment title",
        "description": "What students must do",
        "rubric_criteria": [
          {{"criterion": "What's evaluated", "weight": "Percentage", "description": "Expectations"}}
        ],
        "sample_questions": [
          {{"question": "Sample question text", "type": "Multiple Choice | Short Answer | Essay | Coding",
            "answer_key": "Expected answer or rubric"}}
        ]
      }}
    }}
  ],

  "final_project": {{
    "title": "Final project name",
    "description": "What students build or deliver",
    "requirements": ["requirement 1"],
    "evaluation_criteria": ["criterion 1"],
    "suggested_timeline": "How long to complete"
  }},

  "supplementary_materials": {{
    "reading_list": ["Recommended book or article"],
    "tools_needed": ["Software or tool needed"],
    "templates": ["Template or starter file to provide"],
    "community_resources": ["Forum, Slack, or community to join"]
  }}
}}

Create engaging, practical content. Include real-world examples and hands-on activities.

IMPORTANT: Return ONLY the JSON object.

---

COURSE SPECIFICATIONS:
- Subject: {subject}
- Level: {level}
- Number of Modules: {num_modules}
- Format: {format}
- Industry/Domain: {domain}
- Key Topics to Cover: {key_topics}
- Audience Background: {audience}
- Learning Style Focus: {learning_style}
- Assessment Preference: {assessment_pref}
- Additional Requirements: {requirements}
"""


def generate_course(config: dict, api_key: str) -> dict:
    """Generate a complete course curriculum."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = COURSE_PROMPT.format(**config)
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
