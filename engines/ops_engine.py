"""OpsAgent engine - Agentic Operations Assistant for Shared Platform Management."""

import json
import anthropic

OPS_PROMPT = """\
You are an expert shared-services operations architect and automation specialist. \
Analyse the operations request below and produce a comprehensive plan for the shared \
platform team, covering databases, ETL pipelines, reporting, and administrative tasks.

Return a JSON object:

{{
  "request_summary": {{
    "title": "Short title for the request",
    "requester_role": "Role of the requester",
    "service_area": "Database | ETL | Reporting | Admin | Multi-Domain",
    "priority": "Critical | High | Medium | Low",
    "complexity": "Simple | Moderate | Complex",
    "estimated_effort_hours": <number>,
    "compliance_flags": ["any compliance or audit concerns"]
  }},

  "operations_plan": {{
    "objective": "What this plan achieves",
    "prerequisites": ["things that must be in place before starting"],
    "steps": [
      {{"step_number": <n>, "action": "What to do", "owner": "Role/team responsible",
        "tool_or_system": "System or tool used", "duration_minutes": <n>,
        "risk_level": "High | Medium | Low",
        "rollback_plan": "How to undo if something goes wrong"}}
    ],
    "validation_checks": ["how to verify success"]
  }},

  "database_impact": {{
    "affected_databases": ["list of databases or schemas affected"],
    "migration_required": true/false,
    "schema_changes": ["description of any DDL changes"],
    "data_volume_estimate": "estimated rows or size affected",
    "backup_strategy": "recommended backup approach",
    "downtime_required": true/false,
    "downtime_window": "recommended maintenance window if needed"
  }},

  "etl_pipeline_impact": {{
    "affected_pipelines": ["pipeline names or IDs"],
    "new_pipelines_needed": ["descriptions of new pipelines to create"],
    "schedule_changes": ["any cron or schedule modifications"],
    "source_systems": ["upstream data sources"],
    "target_systems": ["downstream consumers"],
    "data_quality_checks": ["validation rules to add or update"]
  }},

  "reporting_impact": {{
    "affected_reports": ["report names or dashboards"],
    "new_reports_needed": ["descriptions of new reports"],
    "stakeholder_notifications": ["who needs to know about changes"],
    "data_freshness_sla": "expected data latency"
  }},

  "compliance_assessment": {{
    "data_classification": "Public | Internal | Confidential | Restricted",
    "pii_involved": true/false,
    "audit_trail_required": true/false,
    "approval_chain": ["who must approve this change"],
    "regulatory_frameworks": ["SOX | GDPR | HIPAA | SOC2 | None"],
    "retention_policy": "data retention requirements"
  }},

  "cost_analysis": {{
    "compute_cost_delta": "estimated change in compute costs",
    "storage_cost_delta": "estimated change in storage costs",
    "license_implications": "any licensing changes needed",
    "total_monthly_impact": "net monthly cost change estimate",
    "cost_optimisation_tips": ["suggestions to reduce cost"]
  }},

  "risk_matrix": [
    {{"risk": "What could go wrong", "likelihood": "High | Medium | Low",
      "impact": "High | Medium | Low", "mitigation": "How to prevent or handle it"}}
  ],

  "automation_opportunities": [
    {{"task": "Manual task that can be automated",
      "current_effort_hours": <n>,
      "automation_approach": "How to automate it",
      "savings_hours_per_month": <n>,
      "implementation_complexity": "Simple | Moderate | Complex"}}
  ],

  "communication_plan": {{
    "stakeholders": ["who to notify"],
    "change_advisory_board": true/false,
    "pre_change_notice": "how far in advance to notify",
    "post_change_validation": "who validates after deployment"
  }},

  "recommendation": {{
    "go_no_go": "Go | No-Go | Conditional Go",
    "conditions": ["conditions that must be met for Go"],
    "alternative_approaches": ["other ways to solve this"],
    "rationale": "Detailed reasoning for the recommendation"
  }}
}}

Be thorough, practical, and risk-aware. Always consider rollback plans and compliance.

IMPORTANT: Return ONLY the JSON object.

---

OPERATIONS REQUEST:
{ops_request}

ENVIRONMENT CONTEXT:
- Platform: {platform}
- Team Size: {team_size}
- Environment: {environment}
- Current Systems: {current_systems}
- Compliance Requirements: {compliance_reqs}
"""


def analyze_operations(config: dict, api_key: str) -> dict:
    """Analyse an operations request and generate a comprehensive plan."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = OPS_PROMPT.format(**config)
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
