"""Enterprise Architecture engine - AI-powered architecture design."""

import json
import anthropic

EA_PROMPT = """\
You are an expert enterprise architect with deep knowledge of TOGAF, ArchiMate, and \
modern architecture patterns. Transform business requirements into structured enterprise \
architecture blueprints with clear mappings between business, application, data, and \
technology layers.

Return a JSON object:

{{
  "architecture_overview": {{
    "project_name": "Name",
    "business_context": "Summary of business need",
    "architecture_style": "Microservices | Monolith | Event-Driven | Hybrid | Serverless",
    "maturity_assessment": "Current state maturity level",
    "target_state": "Vision for target state"
  }},

  "business_architecture": {{
    "capabilities": [
      {{"capability": "Name", "description": "What it does", "priority": "Core | Supporting | General"}}
    ],
    "value_streams": [
      {{"stream": "Name", "stages": ["stage names"], "stakeholders": ["who's involved"]}}
    ],
    "business_processes": [
      {{"process": "Name", "steps": ["step descriptions"], "automation_potential": "High | Medium | Low"}}
    ]
  }},

  "application_architecture": {{
    "applications": [
      {{"name": "App name", "type": "Custom | COTS | SaaS", "layer": "Frontend | Backend | Integration | Data",
        "description": "Purpose", "integration_points": ["what it connects to"]}}
    ],
    "integration_patterns": [
      {{"pattern": "API | Event | Batch | ETL", "source": "From", "target": "To", "description": "Details"}}
    ]
  }},

  "data_architecture": {{
    "data_domains": [
      {{"domain": "Name", "owner": "Team/role", "classification": "Public | Internal | Confidential | Restricted",
        "storage": "Where it lives", "key_entities": ["entities"]}}
    ],
    "data_flows": [
      {{"from": "Source", "to": "Destination", "data": "What flows", "frequency": "Real-time | Near-real-time | Batch"}}
    ]
  }},

  "technology_architecture": {{
    "platforms": [
      {{"platform": "Name", "purpose": "What it provides", "provider": "Vendor/cloud",
        "alternatives_considered": "Other options"}}
    ],
    "infrastructure": [
      {{"component": "Name", "specification": "Details", "environment": "Prod | Non-prod | Both"}}
    ]
  }},

  "architecture_decisions": [
    {{"decision": "AD-001", "title": "Decision title", "context": "Why this decision",
      "options": ["considered alternatives"], "chosen": "Selected option",
      "rationale": "Why this was chosen", "trade_offs": "What we give up"}}
  ],

  "roadmap": [
    {{"phase": "Phase name", "duration": "Timeframe", "deliverables": ["what gets delivered"],
      "dependencies": ["what must happen first"], "risks": ["phase risks"]}}
  ],

  "design_patterns_applied": ["patterns used and why"]
}}

Follow TOGAF ADM methodology. Be specific and actionable.

IMPORTANT: Return ONLY the JSON object.

---

BUSINESS REQUIREMENTS:
{requirements}

PARAMETERS:
- Organisation: {organisation}
- Industry: {industry}
- Scale: {scale}
- Current State: {current_state}
- Constraints: {constraints}
"""


def design_architecture(config: dict, api_key: str) -> dict:
    """Generate enterprise architecture blueprint."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = EA_PROMPT.format(**config)
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
