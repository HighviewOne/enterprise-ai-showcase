"""AI-powered policy analysis engine - conflict detection, regulation mapping, gap analysis."""

import json
import anthropic

ANALYSIS_PROMPT = """\
You are an expert policy analyst specializing in enterprise governance. Analyze the
provided policy documents to detect conflicts, gaps, outdated provisions, and regulatory
alignment issues.

Return a JSON object:

{{
  "policy_inventory": [
    {{
      "policy_name": "Name or section of the policy",
      "domain": "HR | IT | Finance | Compliance | Operations | Data Privacy | Security",
      "last_updated": "Date if mentioned, else 'Unknown'",
      "clause_count": <number of distinct clauses identified>,
      "status": "Current | Needs Update | Outdated | Conflicting"
    }}
  ],

  "conflicts": [
    {{
      "id": "CONF-001",
      "severity": "Critical | High | Medium | Low",
      "type": "Direct Contradiction | Partial Overlap | Ambiguity | Gap",
      "policies_involved": ["Policy A - Section X", "Policy B - Section Y"],
      "clause_a": "Exact or paraphrased text of clause A",
      "clause_b": "Exact or paraphrased text of clause B",
      "description": "Why these clauses conflict",
      "recommendation": "How to resolve the conflict",
      "priority": "Immediate | Short-term | Next Review Cycle"
    }}
  ],

  "regulatory_mapping": [
    {{
      "regulation": "GDPR Art. 17 | SOX Section 302 | OSHA 1910 | etc.",
      "relevant_policy": "Which internal policy addresses this",
      "coverage": "Full | Partial | Missing",
      "gaps": "What's missing or incomplete",
      "action_needed": "Specific update required"
    }}
  ],

  "outdated_provisions": [
    {{
      "policy": "Policy name/section",
      "clause": "The outdated clause",
      "reason": "Why it's outdated (new regulation, industry change, etc.)",
      "suggested_update": "Proposed new language or approach"
    }}
  ],

  "summary": {{
    "total_policies": <int>,
    "total_clauses": <int>,
    "conflicts_found": <int>,
    "critical_conflicts": <int>,
    "regulatory_gaps": <int>,
    "outdated_provisions": <int>,
    "health_score": <0-100>,
    "executive_summary": "3-4 sentence assessment of policy health."
  }},

  "action_plan": [
    {{"priority": 1, "action": "Description", "owner": "Department", "deadline": "Immediate | 30 days | 90 days"}}
  ]
}}

Be thorough. Look for:
1. Clauses that directly contradict each other across different policy documents
2. Gaps where no policy covers a critical regulatory requirement
3. Outdated language that doesn't reflect current regulations (GDPR, SOX, CCPA, etc.)
4. Ambiguous clauses that could be interpreted differently by different departments
5. Redundant clauses that create maintenance burden

Applicable regulations to check against: {regulations}

IMPORTANT: Return ONLY the JSON object.

---

POLICY DOCUMENTS:
{policy_text}
"""


def analyze_policies(policy_text: str, regulations: str, api_key: str) -> dict:
    """Analyze policies for conflicts, gaps, and regulatory alignment."""
    client = anthropic.Anthropic(api_key=api_key)

    if len(policy_text) > 80_000:
        policy_text = policy_text[:80_000] + "\n\n[... truncated ...]"

    prompt = ANALYSIS_PROMPT.format(policy_text=policy_text, regulations=regulations)

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
