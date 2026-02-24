"""LLM-powered requirement extraction, classification, and analysis."""

import json
import anthropic

EXTRACTION_PROMPT = """\
You are an expert requirements engineer and document analyst.

Analyze the following document(s) and extract ALL requirements. For each requirement, provide:

Return a JSON object with exactly this structure:

{{
  "requirements": [
    {{
      "id": "REQ-001",
      "title": "Short descriptive title",
      "description": "Full requirement description as stated in the document",
      "source_ref": "Document name, section, or page reference",
      "type": "Functional | Non-Functional | Constraint | Interface | Performance | Security | Compliance",
      "category": "Domain-specific category (e.g., Bogie, Power System, Safety, Data, UI, API, etc.)",
      "priority": "Must Have | Should Have | Nice to Have | Not Specified",
      "related_to": ["REQ-XXX", "REQ-YYY"]
    }}
  ],
  "document_summary": "2-3 sentence summary of what the document covers.",
  "total_requirements_found": <integer>,
  "type_breakdown": {{"Functional": <count>, "Non-Functional": <count>, ...}}
}}

Guidelines:
- Extract EVERY requirement, even implicit ones (e.g., "the system must...", "shall...", "should...")
- Assign sequential IDs starting from REQ-001
- Identify cross-references between related requirements
- Be thorough — missing requirements is worse than extracting too many
- If a requirement is ambiguous, note that in the description

IMPORTANT: Return ONLY the JSON object, no other text.

---

DOCUMENT(S):
{document_text}
"""

CONTRADICTION_PROMPT = """\
You are an expert requirements analyst specializing in conflict detection.

Given the following extracted requirements, identify any contradictions, conflicts, overlaps,
or ambiguities between them. Look for:
1. Direct contradictions (two requirements that cannot both be satisfied)
2. Partial conflicts (requirements that may conflict under certain conditions)
3. Ambiguities (vague requirements that could be interpreted in conflicting ways)
4. Redundancies (requirements that say the same thing differently)

Return a JSON object:

{{
  "contradictions": [
    {{
      "type": "Direct Contradiction | Partial Conflict | Ambiguity | Redundancy",
      "severity": "High | Medium | Low",
      "requirement_ids": ["REQ-001", "REQ-005"],
      "description": "Explanation of the conflict",
      "recommendation": "Suggested resolution"
    }}
  ],
  "overall_consistency_score": <integer 0-100>,
  "summary": "Brief overall assessment of requirement set consistency."
}}

IMPORTANT: Return ONLY the JSON object. If no contradictions found, return an empty list.

---

REQUIREMENTS:
{requirements_json}
"""

CHAT_PROMPT = """\
You are a helpful requirements analyst assistant. You have access to the following
requirement document(s) and extracted requirements.

Answer the user's question based on this context. Be specific, cite requirement IDs
when relevant, and provide actionable answers. If the answer isn't in the documents, say so.

---

DOCUMENT TEXT:
{document_text}

---

EXTRACTED REQUIREMENTS:
{requirements_json}

---

USER QUESTION: {question}
"""


def _call_claude(prompt: str, api_key: str, max_tokens: int = 4096) -> str:
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


def _parse_json(text: str) -> dict:
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return json.loads(text)


def extract_requirements(document_text: str, api_key: str) -> dict:
    """Extract and classify requirements from document text."""
    # Truncate very large documents to fit context
    max_chars = 80_000
    if len(document_text) > max_chars:
        document_text = document_text[:max_chars] + "\n\n[... document truncated ...]"

    prompt = EXTRACTION_PROMPT.format(document_text=document_text)
    response = _call_claude(prompt, api_key)
    return _parse_json(response)


def detect_contradictions(requirements: list[dict], api_key: str) -> dict:
    """Analyze requirements for contradictions and conflicts."""
    reqs_json = json.dumps(requirements, indent=2)
    prompt = CONTRADICTION_PROMPT.format(requirements_json=reqs_json)
    response = _call_claude(prompt, api_key)
    return _parse_json(response)


def chat_about_requirements(
    question: str,
    document_text: str,
    requirements: list[dict],
    api_key: str,
) -> str:
    """Answer questions about the documents and requirements."""
    max_chars = 60_000
    if len(document_text) > max_chars:
        document_text = document_text[:max_chars] + "\n\n[... truncated ...]"

    reqs_json = json.dumps(requirements, indent=2)
    prompt = CHAT_PROMPT.format(
        document_text=document_text,
        requirements_json=reqs_json,
        question=question,
    )
    return _call_claude(prompt, api_key, max_tokens=2048)
