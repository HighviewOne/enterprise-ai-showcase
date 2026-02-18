"""LLM-powered resume analysis using Anthropic Claude."""

import json
import anthropic


ANALYSIS_PROMPT = """\
You are an expert ATS (Applicant Tracking System) analyzer and career coach.

Analyze the following resume against the provided job description. Return your analysis as a JSON object with exactly these fields:

{{
  "overall_score": <integer 0-100>,
  "keyword_match_score": <integer 0-100>,
  "skills_alignment_score": <integer 0-100>,
  "experience_relevance_score": <integer 0-100>,
  "education_match_score": <integer 0-100>,
  "matched_keywords": ["list", "of", "matched", "keywords"],
  "missing_keywords": ["list", "of", "important", "missing", "keywords"],
  "matched_skills": ["list", "of", "matched", "skills"],
  "missing_skills": ["list", "of", "missing", "skills"],
  "strengths": ["strength 1", "strength 2", "..."],
  "improvement_suggestions": ["suggestion 1", "suggestion 2", "..."],
  "summary": "A 2-3 sentence overall assessment of the candidate's fit for this role."
}}

Scoring guidelines:
- overall_score: Weighted average reflecting how well the resume matches the job (keyword 30%, skills 30%, experience 25%, education 15%)
- keyword_match_score: How many key terms from the job description appear in the resume
- skills_alignment_score: How well the candidate's skills match the required/preferred skills
- experience_relevance_score: How relevant the candidate's experience is to the role
- education_match_score: How well education/certifications align with requirements

Be specific and actionable in your improvement suggestions. Focus on what would make the biggest impact.

IMPORTANT: Return ONLY the JSON object, no other text.

---

JOB DESCRIPTION:
{job_description}

---

RESUME:
{resume_text}
"""


def analyze_resume(resume_text: str, job_description: str, api_key: str) -> dict:
    """Analyze a resume against a job description using Claude."""
    client = anthropic.Anthropic(api_key=api_key)

    prompt = ANALYSIS_PROMPT.format(
        resume_text=resume_text,
        job_description=job_description,
    )

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text.strip()

    # Handle possible markdown code fences
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        # Remove first and last lines (the fences)
        lines = [l for l in lines if not l.strip().startswith("```")]
        response_text = "\n".join(lines)

    return json.loads(response_text)
