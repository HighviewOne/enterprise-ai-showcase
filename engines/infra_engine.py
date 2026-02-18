"""Infrastructure Code Generator engine - AI-powered IaC generation."""

import json
import anthropic

INFRA_PROMPT = """\
You are an expert cloud infrastructure architect specialising in Infrastructure as Code. \
Generate production-ready IaC based on the requirements, following cloud provider best \
practices, security hardening, and organisational policies.

Return a JSON object:

{{
  "architecture_summary": {{
    "description": "High-level architecture description",
    "cloud_provider": "AWS | Azure | GCP",
    "iac_tool": "Terraform | CloudFormation | Pulumi | Bicep",
    "estimated_monthly_cost": "$X",
    "components": ["list of infrastructure components"],
    "diagram_description": "Text description of the architecture"
  }},

  "generated_code": [
    {{
      "filename": "filename.tf or filename.yaml",
      "description": "What this file does",
      "code": "The actual IaC code",
      "notes": "Important notes about this file"
    }}
  ],

  "security_review": {{
    "security_features": ["security measures included"],
    "compliance_alignment": ["standards this aligns with (CIS, SOC2, etc.)"],
    "remaining_considerations": ["security items to review manually"]
  }},

  "variables_and_inputs": [
    {{"variable": "var_name", "type": "string | number | bool | list | map",
      "description": "What it controls", "default": "default value", "sensitive": true|false}}
  ],

  "deployment_steps": [
    {{"step": <number>, "command": "CLI command", "description": "What this does",
      "prerequisites": "What needs to be in place first"}}
  ],

  "cost_breakdown": [
    {{"service": "Service name", "configuration": "Instance type/size",
      "estimated_monthly": "$X", "notes": "Cost notes"}}
  ],

  "best_practices_applied": ["list of best practices incorporated"],

  "warnings": ["any important warnings or caveats"]
}}

Generate clean, well-commented, production-quality code. Follow the principle of least \
privilege for all IAM configurations. Include tagging strategy.

IMPORTANT: Return ONLY the JSON object.

---

REQUIREMENTS:
{requirements}

PARAMETERS:
- Cloud Provider: {provider}
- IaC Tool: {iac_tool}
- Environment: {environment}
- Region: {region}
- Naming Convention: {naming}
- Security Level: {security_level}
- Additional Constraints: {constraints}
"""


def generate_infra(config: dict, api_key: str) -> dict:
    """Generate infrastructure code from requirements."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = INFRA_PROMPT.format(**config)
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
