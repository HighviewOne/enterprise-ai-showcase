"""AWSentinel engine - AWS compliance scoring and remediation."""

import json
import anthropic

COMPLIANCE_PROMPT = """\
You are an expert AWS cloud security and compliance engineer. Analyse the AWS \
environment configuration and provide a comprehensive compliance assessment with \
scoring and automated remediation guidance.

Return a JSON object:

{{
  "overall_assessment": {{
    "compliance_score": <1-100>,
    "risk_level": "Critical | High | Medium | Low",
    "total_checks": <number>,
    "passed": <number>,
    "failed": <number>,
    "warnings": <number>,
    "headline": "One-line summary"
  }},

  "category_scores": [
    {{
      "category": "Identity & Access | Network Security | Data Protection | Logging & Monitoring | Compute | Storage | Database | Compliance Frameworks",
      "score": <1-100>,
      "passed": <number>,
      "failed": <number>,
      "critical_findings": <number>
    }}
  ],

  "findings": [
    {{
      "finding_id": "AWS-SEC-001",
      "title": "Finding title",
      "category": "Category",
      "severity": "Critical | High | Medium | Low | Informational",
      "status": "FAIL | WARN | PASS",
      "resource": "Affected resource ARN or description",
      "description": "What was found",
      "impact": "Security impact",
      "remediation": {{
        "description": "How to fix",
        "cli_command": "aws CLI command to remediate",
        "terraform_fix": "Terraform code snippet",
        "manual_steps": ["step-by-step manual fix"]
      }},
      "compliance_mapping": ["CIS 1.1", "SOC2 CC6.1", "NIST AC-2"]
    }}
  ],

  "compliance_frameworks": [
    {{
      "framework": "CIS AWS Benchmark | SOC 2 | HIPAA | PCI-DSS | NIST 800-53",
      "coverage": <percentage>,
      "gaps": <number>,
      "critical_gaps": ["most important gaps"]
    }}
  ],

  "remediation_priority": [
    {{
      "priority": <1-N>,
      "finding_id": "Reference",
      "action": "What to do",
      "effort": "Quick Win | Medium | Complex",
      "risk_reduction": "High | Medium | Low"
    }}
  ],

  "cost_of_compliance": {{
    "estimated_monthly": "$X additional cost for compliance",
    "breakdown": ["cost items"]
  }},

  "recommendations": ["top strategic recommendations"]
}}

Be specific with resource names and provide copy-paste-ready remediation commands.

IMPORTANT: Return ONLY the JSON object.

---

AWS ENVIRONMENT CONFIGURATION:
{config_data}

PARAMETERS:
- Account Type: {account_type}
- Target Frameworks: {frameworks}
- Environment: {environment}
- Additional Context: {context}
"""


def assess_compliance(config: dict, api_key: str) -> dict:
    """Assess AWS environment compliance."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = COMPLIANCE_PROMPT.format(**config)
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
