"""AI Incident Triage engine - correlates alerts and suggests remediation."""

import json
import anthropic

TRIAGE_PROMPT = """\
You are a senior Site Reliability Engineer (SRE) and incident commander. Analyze \
the provided alerts, logs, and error traces to perform incident triage. Correlate \
related alerts, identify probable root causes, and recommend remediation steps.

Return a JSON object:

{{
  "incident_summary": {{
    "title": "Short incident title",
    "severity": "SEV1 | SEV2 | SEV3 | SEV4",
    "status": "Investigating | Identified | Mitigating | Resolved",
    "impact": "Description of user/business impact",
    "affected_services": ["service 1", "service 2"],
    "start_time": "When the incident likely started",
    "detection_time": "When first alert fired",
    "blast_radius": "Small | Medium | Large | Critical"
  }},

  "alert_correlation": [
    {{
      "group_name": "Correlated alert group name",
      "alerts": ["alert summary 1", "alert summary 2"],
      "relationship": "How these alerts are related",
      "is_symptom_or_cause": "Symptom | Root Cause | Contributing Factor"
    }}
  ],

  "root_cause_analysis": {{
    "primary_hypothesis": "Most likely root cause",
    "confidence": "High | Medium | Low",
    "evidence": ["evidence supporting this hypothesis"],
    "contributing_factors": ["factor 1", "factor 2"],
    "alternative_hypotheses": [
      {{"hypothesis": "Alternative cause", "likelihood": "High | Medium | Low"}}
    ],
    "timeline_reconstruction": [
      {{"time": "timestamp", "event": "What happened", "significance": "Why it matters"}}
    ]
  }},

  "remediation": {{
    "immediate_actions": [
      {{"action": "What to do now", "priority": "P0 | P1 | P2", "owner": "Suggested team/role",
        "command_hint": "Relevant CLI command or runbook step if applicable"}}
    ],
    "short_term_fixes": [
      {{"action": "Fix for today/this week", "rationale": "Why this helps"}}
    ],
    "long_term_prevention": [
      {{"action": "Prevent recurrence", "rationale": "Why this prevents future incidents"}}
    ]
  }},

  "communication": {{
    "internal_update": "Status update for the engineering team",
    "stakeholder_update": "Non-technical update for leadership/stakeholders",
    "customer_facing": "Public status page message (if needed)",
    "escalation_needed": true|false,
    "teams_to_notify": ["team 1", "team 2"]
  }},

  "metrics_to_watch": [
    {{"metric": "What to monitor", "expected_behavior": "What recovery looks like",
      "dashboard": "Where to find this metric"}}
  ],

  "post_incident": {{
    "blameless_review_topics": ["topic for post-mortem discussion"],
    "action_items": [
      {{"item": "Follow-up task", "priority": "High | Medium | Low", "owner": "Team"}}
    ],
    "process_improvements": ["improvement suggestion"]
  }}
}}

Be thorough, specific, and follow SRE best practices. Prioritize customer impact.

IMPORTANT: Return ONLY the JSON object.

---

ALERTS AND LOGS:
{alerts}

SYSTEM CONTEXT:
- Environment: {environment}
- Architecture: {architecture}
- Recent Changes: {recent_changes}
- On-call Team: {oncall_team}

ADDITIONAL CONTEXT: {context}
"""


def triage_incident(config: dict, api_key: str) -> dict:
    """Analyze alerts and perform incident triage."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = TRIAGE_PROMPT.format(**config)
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
