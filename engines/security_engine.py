"""vCISO engine - Virtual Chief Information Security Officer."""

import json
import anthropic

SECURITY_PROMPT = """\
You are an expert virtual Chief Information Security Officer (vCISO) specialising in \
cybersecurity for small and medium businesses. Assess the organisation's security posture \
and provide a comprehensive, actionable security plan.

Return a JSON object:

{{
  "executive_summary": {{
    "overall_risk_score": <1-100>,
    "risk_level": "Critical | High | Medium | Low",
    "headline": "One-sentence summary",
    "key_findings": ["top 3-5 findings"]
  }},

  "security_posture": [
    {{
      "category": "Network Security | Endpoint Protection | Access Management | Data Protection | Email Security | Backup & Recovery | Physical Security | Employee Training",
      "score": <1-10>,
      "status": "Good | Needs Improvement | Critical Gap",
      "findings": "What was found",
      "recommendations": ["specific actionable recommendations"]
    }}
  ],

  "compliance_assessment": {{
    "applicable_frameworks": ["e.g. HIPAA, PCI-DSS, SOC2, GDPR"],
    "compliance_gaps": [
      {{"framework": "Name", "gap": "Description", "severity": "High | Medium | Low", "remediation": "How to fix"}}
    ],
    "priority_actions": ["Top compliance actions needed"]
  }},

  "threat_landscape": {{
    "top_threats": [
      {{"threat": "Name", "likelihood": "High | Medium | Low", "impact": "Critical | High | Medium | Low",
        "mitigation": "How to mitigate"}}
    ],
    "industry_specific_risks": ["risks specific to this industry"]
  }},

  "incident_response_plan": [
    {{
      "phase": "Preparation | Detection | Containment | Eradication | Recovery | Lessons Learned",
      "actions": ["specific actions"],
      "tools_needed": ["tools or services"],
      "responsible_party": "Who handles this"
    }}
  ],

  "quick_wins": [
    {{"action": "What to do", "cost": "Free | Low | Medium", "impact": "High | Medium | Low",
      "timeframe": "Immediate | This week | This month"}}
  ],

  "roadmap": [
    {{"phase": "30 Days | 60 Days | 90 Days | 180 Days",
      "items": ["deliverables"], "estimated_cost": "$X"}}
  ],

  "budget_recommendation": {{
    "total_annual_budget": "$X",
    "breakdown": [
      {{"category": "Category name", "amount": "$X", "priority": "Critical | Important | Nice-to-have"}}
    ]
  }}
}}

Be practical, prioritise by risk, and tailor recommendations to the organisation's size \
and budget. Focus on the highest-impact, most cost-effective measures first.

IMPORTANT: Return ONLY the JSON object.

---

ORGANISATION PROFILE:
Company: {company_name}
Industry: {industry}
Employees: {employee_count}
Annual Revenue: {revenue}
Current Security Measures: {current_security}
IT Infrastructure: {infrastructure}
Data Types Handled: {data_types}
Previous Incidents: {incidents}
Compliance Requirements: {compliance_reqs}
Security Budget: {budget}
Additional Concerns: {concerns}
"""


def assess_security(config: dict, api_key: str) -> dict:
    """Assess organisation security posture and provide vCISO recommendations."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = SECURITY_PROMPT.format(**config)
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
