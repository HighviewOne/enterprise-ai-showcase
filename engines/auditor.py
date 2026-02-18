"""AI-powered compliance audit engine."""

import json
import anthropic


AUDIT_PROMPT = """\
You are an expert compliance auditor with deep knowledge of regulatory frameworks
(SOX, GDPR, HIPAA, PCI-DSS, OSHA, employment law, financial regulations). Analyze
the provided policy documents and activity/transaction logs to identify compliance
violations, risks, and areas of concern.

Return a JSON object:

{{
  "audit_summary": {{
    "overall_risk_level": "Critical | High | Medium | Low",
    "compliance_score": <integer 0-100>,
    "total_findings": <integer>,
    "critical_findings": <integer>,
    "areas_audited": ["Finance", "HR", "IT", "Operations"],
    "summary": "2-3 sentence executive summary of audit results."
  }},
  "findings": [
    {{
      "id": "FIND-001",
      "title": "Short finding title",
      "severity": "Critical | High | Medium | Low",
      "category": "Finance | HR | IT Security | Data Privacy | Operations | Safety",
      "regulation": "The regulation or policy violated (e.g., SOX Section 302, GDPR Art. 17)",
      "description": "Detailed description of the violation or risk",
      "evidence": "Specific evidence from the provided documents/logs",
      "affected_policy": "Which internal policy is impacted",
      "impact": "Business impact if unaddressed",
      "remediation": "Specific steps to remediate this finding",
      "timeline": "Immediate | 30 days | 90 days | Next audit cycle",
      "owner": "Suggested responsible department or role"
    }}
  ],
  "positive_observations": [
    "Areas where compliance is strong"
  ],
  "recommendations": [
    {{
      "priority": "High | Medium | Low",
      "recommendation": "Actionable recommendation",
      "expected_benefit": "What improvement this would bring"
    }}
  ],
  "next_steps": ["Step 1 for follow-up", "Step 2"]
}}

Be thorough and specific. Cite exact evidence from the documents where possible.
If activity logs are provided, look for patterns like unauthorized access, unusual
transactions, missing approvals, or policy violations.

IMPORTANT: Return ONLY the JSON object.

---

AUDIT SCOPE: {audit_scope}
REGULATORY FRAMEWORKS: {frameworks}

POLICY DOCUMENTS:
{policy_text}

ACTIVITY / TRANSACTION LOGS:
{activity_text}

ADDITIONAL CONTEXT:
{additional_context}
"""


def run_audit(config: dict, api_key: str) -> dict:
    """Run AI compliance audit."""
    client = anthropic.Anthropic(api_key=api_key)

    # Truncate if needed
    for key in ("policy_text", "activity_text"):
        if len(config.get(key, "")) > 40_000:
            config[key] = config[key][:40_000] + "\n\n[... truncated ...]"

    prompt = AUDIT_PROMPT.format(**config)

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
