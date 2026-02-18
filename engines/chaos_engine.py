"""Chaos Agent engine - AI-powered chaos engineering for Kubernetes."""

import json
import anthropic

CHAOS_PROMPT = """\
You are an expert chaos engineer and Kubernetes reliability specialist. Given a cluster \
configuration and a natural-language chaos scenario description, generate a comprehensive \
chaos engineering plan with resilience findings.

Return a JSON object:

{{
  "scenario_plan": {{
    "scenario_name": "Descriptive name for this chaos experiment",
    "objective": "What we aim to learn or validate",
    "hypothesis": "What we expect to happen if the system is resilient",
    "chaos_type": "Network | Pod | Node | Resource | Application | Combined",
    "target_services": ["services being targeted"],
    "duration_minutes": <estimated duration>,
    "steady_state_definition": "Metrics that define normal operation"
  }},

  "blast_radius": {{
    "directly_affected": [
      {{"service": "name", "impact": "description of direct impact", "severity": "Critical | High | Medium | Low"}}
    ],
    "indirectly_affected": [
      {{"service": "name", "impact": "description of cascading impact", "severity": "Critical | High | Medium | Low"}}
    ],
    "dependency_chain": ["service-a -> service-b -> service-c"],
    "estimated_user_impact": "Description of end-user experience during chaos",
    "data_risk": "None | Low | Medium | High"
  }},

  "experiment_steps": [
    {{
      "step_number": <int>,
      "phase": "Inject | Observe | Rollback",
      "action": "Detailed action description",
      "command": "kubectl or chaos tool command if applicable",
      "duration_seconds": <int>,
      "success_criteria": "What to check",
      "abort_condition": "When to abort this step"
    }}
  ],

  "expected_behavior": {{
    "resilient_response": "What a well-designed system should do",
    "circuit_breakers": ["expected circuit breaker activations"],
    "failover_expectations": ["expected failover behaviors"],
    "degraded_mode": "How the system should gracefully degrade",
    "recovery_time_target": "Expected time to recover after rollback"
  }},

  "resilience_findings": [
    {{
      "finding": "Description of weakness or strength",
      "category": "Weakness | Strength | Observation",
      "severity": "Critical | High | Medium | Low",
      "affected_component": "Service or component name",
      "evidence": "How this was determined"
    }}
  ],

  "remediation_recommendations": [
    {{
      "recommendation": "What to fix or improve",
      "priority": "P0 | P1 | P2 | P3",
      "effort": "Low | Medium | High",
      "implementation": "How to implement this fix",
      "kubernetes_config": "Relevant K8s config snippet if applicable"
    }}
  ],

  "sla_impact_assessment": {{
    "availability_impact": "Estimated availability impact (e.g., 99.9% -> 99.5%)",
    "latency_impact": "Expected latency degradation",
    "error_rate_impact": "Expected error rate increase",
    "affected_slos": ["SLOs that may be breached"],
    "financial_impact": "Estimated cost of the failure scenario",
    "mttr_estimate": "Mean time to recovery estimate"
  }},

  "runbook_generation": {{
    "incident_title": "Title for the incident runbook",
    "detection": ["How to detect this failure in production"],
    "triage_steps": ["Step-by-step triage process"],
    "mitigation_steps": ["Immediate mitigation actions"],
    "resolution_steps": ["Full resolution procedure"],
    "communication_template": "Stakeholder communication template",
    "post_mortem_questions": ["Questions for post-incident review"]
  }}
}}

Be thorough, practical, and specific to Kubernetes. Include real kubectl commands where applicable.

IMPORTANT: Return ONLY the JSON object.

---

CLUSTER CONFIGURATION:
{cluster_config}

CHAOS SCENARIO:
{chaos_scenario}
"""


def run_chaos_analysis(config: dict, api_key: str) -> dict:
    """Analyze a chaos engineering scenario and generate resilience findings."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = CHAOS_PROMPT.format(**config)
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
