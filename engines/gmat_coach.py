"""GMAT Prep Coach engine - generates practice questions and evaluates answers."""

import json
import anthropic

QUESTION_PROMPT = """\
You are an expert GMAT tutor and test prep coach. Generate a practice question set
tailored to the student's profile and selected section.

Return a JSON object:

{{
  "session_info": {{
    "section": "{section}",
    "difficulty": "{difficulty}",
    "num_questions": {num_questions},
    "estimated_time_minutes": <number>
  }},

  "questions": [
    {{
      "id": <1-based number>,
      "type": "Problem Solving | Data Sufficiency | Reading Comprehension | Critical Reasoning | Sentence Correction",
      "difficulty": "Easy | Medium | Hard",
      "topic": "Specific topic (e.g., Algebra, Percentages, Inference, Parallelism)",
      "stem": "The question text. For RC, include a short passage first.",
      "choices": {{
        "A": "Choice A text",
        "B": "Choice B text",
        "C": "Choice C text",
        "D": "Choice D text",
        "E": "Choice E text"
      }},
      "correct_answer": "A|B|C|D|E",
      "explanation": "Detailed step-by-step explanation of the correct answer",
      "common_mistakes": ["mistake students often make"],
      "time_target_seconds": <number>,
      "strategy_tip": "A helpful test-taking strategy for this question type"
    }}
  ],

  "section_overview": {{
    "what_gmat_tests": "Brief description of what this section measures",
    "scoring_info": "How this section contributes to the overall GMAT score",
    "key_strategies": ["strategy 1", "strategy 2"]
  }}
}}

Generate exactly {num_questions} questions at the {difficulty} difficulty level for the {section} section.
Make questions realistic and representative of actual GMAT content.
Vary the specific topics within the section.

IMPORTANT: Return ONLY the JSON object.

---

STUDENT PROFILE:
- Target Score: {target_score}
- Weak Areas: {weak_areas}
- Study Stage: {study_stage}
- Additional Context: {context}
"""

EVALUATE_PROMPT = """\
You are an expert GMAT tutor. Evaluate the student's answers to this practice set
and provide a detailed performance analysis.

Return a JSON object:

{{
  "score_summary": {{
    "total_questions": <number>,
    "correct": <number>,
    "incorrect": <number>,
    "accuracy_pct": <number>,
    "estimated_section_score": "Estimated GMAT section percentile range",
    "performance_level": "Below Average | Average | Above Average | Excellent"
  }},

  "per_question_review": [
    {{
      "id": <question number>,
      "student_answer": "What the student chose",
      "correct_answer": "The right answer",
      "is_correct": true|false,
      "explanation": "Why the correct answer is right and why the student's choice was wrong (if applicable)",
      "concept_tested": "The underlying concept",
      "improvement_tip": "Specific tip for this question"
    }}
  ],

  "strength_areas": ["topics the student did well on"],
  "weakness_areas": ["topics needing more work"],

  "study_plan": {{
    "immediate_focus": ["top 2-3 areas to study right now"],
    "recommended_practice": ["specific practice suggestions"],
    "resources": ["study resource suggestions"],
    "time_allocation": "How to allocate study time across weak areas"
  }},

  "motivation": "An encouraging message about their performance and progress"
}}

IMPORTANT: Return ONLY the JSON object.

---

QUESTIONS AND ANSWERS:
{qa_data}
"""


def generate_questions(config: dict, api_key: str) -> dict:
    """Generate GMAT practice questions."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = QUESTION_PROMPT.format(**config)
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


def evaluate_answers(qa_data: str, api_key: str) -> dict:
    """Evaluate student answers and provide feedback."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = EVALUATE_PROMPT.format(qa_data=qa_data)
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
