"""Software Factory engine - AI-powered technical blueprint generation."""

import json
import anthropic

FACTORY_PROMPT = """\
You are a senior enterprise architect and technical strategist. Given a business concept \
and constraints, generate a comprehensive technical blueprint that a development team can \
use to plan and execute the project.

Return a JSON object:

{{
  "executive_summary": {{
    "project_name": "Suggested project name",
    "vision": "One-paragraph vision statement",
    "business_value": "Key business value proposition",
    "complexity": "Low | Medium | High | Very High",
    "confidence_level": "High | Medium | Low",
    "key_differentiators": ["What makes this solution unique"]
  }},

  "requirements_analysis": {{
    "functional_requirements": [
      {{"id": "FR-001", "requirement": "Description", "priority": "Must | Should | Could", "complexity": "Low | Medium | High"}}
    ],
    "non_functional_requirements": [
      {{"id": "NFR-001", "category": "Performance | Security | Scalability | Reliability | Compliance", "requirement": "Description", "target_metric": "Measurable target"}}
    ],
    "assumptions": ["Key assumptions made"],
    "constraints": ["Known constraints"]
  }},

  "architecture_blueprint": {{
    "pattern": "Architecture pattern (e.g., Microservices, Event-Driven, CQRS)",
    "components": [
      {{"name": "Component name", "type": "Service | Database | Queue | Cache | Gateway | CDN", "responsibility": "What it does", "technology": "Specific tech choice"}}
    ],
    "data_flows": [
      {{"from": "source", "to": "destination", "protocol": "REST | gRPC | Kafka | WebSocket", "data": "What data flows"}}
    ],
    "architecture_decisions": [
      {{"decision": "What was decided", "rationale": "Why", "alternatives_considered": ["other options"], "trade_offs": "What we give up"}}
    ]
  }},

  "technology_stack": {{
    "frontend": {{"technology": "name", "rationale": "why chosen"}},
    "backend": {{"technology": "name", "rationale": "why chosen"}},
    "database": {{"technology": "name", "rationale": "why chosen"}},
    "cache": {{"technology": "name", "rationale": "why chosen"}},
    "message_queue": {{"technology": "name", "rationale": "why chosen"}},
    "monitoring": {{"technology": "name", "rationale": "why chosen"}},
    "ci_cd": {{"technology": "name", "rationale": "why chosen"}},
    "additional": [{{"technology": "name", "purpose": "what for", "rationale": "why"}}]
  }},

  "api_design": [
    {{
      "endpoint": "/api/v1/resource",
      "method": "GET | POST | PUT | DELETE",
      "description": "What it does",
      "request_body": "Key request fields",
      "response": "Key response fields",
      "auth": "Authentication requirement"
    }}
  ],

  "data_model": [
    {{
      "entity": "Entity name",
      "description": "What it represents",
      "key_fields": ["field1: type", "field2: type"],
      "relationships": ["relationship descriptions"],
      "storage": "Where it is stored"
    }}
  ],

  "infrastructure_plan": {{
    "cloud_provider": "{target_platform}",
    "environments": ["dev", "staging", "production"],
    "compute": [{{"service": "name", "spec": "sizing", "purpose": "what for"}}],
    "storage": [{{"service": "name", "spec": "sizing", "purpose": "what for"}}],
    "networking": [{{"service": "name", "purpose": "what for"}}],
    "managed_services": [{{"service": "name", "purpose": "what for"}}]
  }},

  "security_architecture": {{
    "authentication": "Auth strategy",
    "authorization": "Authz strategy",
    "data_encryption": "Encryption approach",
    "network_security": "Network security measures",
    "compliance_requirements": ["applicable standards"],
    "security_controls": [
      {{"control": "description", "layer": "Network | Application | Data | Identity"}}
    ]
  }},

  "deployment_strategy": {{
    "approach": "Blue-Green | Canary | Rolling | Feature Flags",
    "ci_pipeline": ["pipeline stages"],
    "cd_pipeline": ["deployment stages"],
    "testing_strategy": ["unit", "integration", "e2e", "performance"],
    "rollback_plan": "How to rollback",
    "environment_promotion": "How code moves through environments"
  }},

  "cost_estimate": {{
    "monthly_dev": "Monthly cost during development",
    "monthly_staging": "Monthly staging cost",
    "monthly_production": "Monthly production cost at launch",
    "monthly_scaled": "Monthly cost at full scale",
    "cost_breakdown": [
      {{"category": "Compute | Storage | Network | Services | Licensing", "monthly_cost": "$X", "notes": "details"}}
    ],
    "optimization_tips": ["cost saving suggestions"]
  }},

  "implementation_roadmap": [
    {{
      "phase": "Phase name",
      "duration_weeks": <int>,
      "milestones": ["key deliverables"],
      "dependencies": ["what must be done first"],
      "team_focus": "Which team members are key",
      "risks": ["phase-specific risks"]
    }}
  ],

  "team_structure": [
    {{
      "role": "Role title",
      "count": <int>,
      "skills": ["required skills"],
      "phase_needed": "When they join",
      "full_time": true or false
    }}
  ],

  "risk_assessment": [
    {{
      "risk": "Risk description",
      "category": "Technical | Organizational | Market | Resource | Schedule",
      "probability": "High | Medium | Low",
      "impact": "High | Medium | Low",
      "mitigation": "How to mitigate",
      "contingency": "Backup plan"
    }}
  ]
}}

Be practical, specific, and enterprise-grade. Tailor recommendations to the team size ({team_size}) \
and budget ({budget_range}).

IMPORTANT: Return ONLY the JSON object.

---

BUSINESS CONCEPT:
{business_concept}

PROJECT PARAMETERS:
- Target Platform: {target_platform}
- Tech Preferences: {tech_preferences}
- Team Size: {team_size}
- Timeline: {timeline}
- Budget Range: {budget_range}
"""


def generate_blueprint(config: dict, api_key: str) -> dict:
    """Generate a technical blueprint from a business concept."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = FACTORY_PROMPT.format(**config)
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
