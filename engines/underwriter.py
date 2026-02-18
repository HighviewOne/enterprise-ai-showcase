"""AI-powered loan underwriting engine with bias guardrails."""

import json
import anthropic


UNDERWRITING_PROMPT = """\
You are an expert loan underwriter at a regulated financial institution. Analyze the
following loan application and credit profile to produce an underwriting assessment.

IMPORTANT GUARDRAILS:
- Do NOT use race, ethnicity, religion, gender, marital status, national origin, or age
  as factors in your decision. These are prohibited under ECOA and Fair Housing Act.
- Base your decision ONLY on financial factors: credit score, DTI, income stability,
  employment history, loan-to-value ratio, and repayment capacity.
- If you detect any bias in your reasoning, flag it and correct it.

Return a JSON object:

{{
  "application_id": "{app_id}",
  "risk_classification": "Low Risk | Medium Risk | High Risk",
  "credit_tier": "Prime | Near-Prime | Subprime",
  "preliminary_decision": "Approve | Conditional Approve | Refer to Human | Deny",
  "confidence": <integer 0-100>,
  "recommended_terms": {{
    "approved_amount": <number or null>,
    "interest_rate_pct": <number or null>,
    "term_months": <integer or null>,
    "monthly_payment": <number or null>,
    "conditions": ["condition 1 if conditional"]
  }},
  "risk_factors": [
    {{"factor": "description", "impact": "Positive | Negative | Neutral", "weight": "High | Medium | Low"}}
  ],
  "financial_ratios": {{
    "debt_to_income_pct": <number>,
    "loan_to_value_pct": <number or null>,
    "payment_to_income_pct": <number>,
    "disposable_income_after_payment": <number>
  }},
  "bias_check": {{
    "protected_attributes_used": false,
    "decision_based_on_financial_factors_only": true,
    "notes": "Confirmation that decision is free from prohibited bias."
  }},
  "denial_reasons": ["reason 1 if denied"],
  "summary": "2-3 sentence underwriting summary with key decision drivers."
}}

IMPORTANT: Return ONLY the JSON object.

---

LOAN APPLICATION:
- Application ID: {app_id}
- Applicant Name: {applicant_name}
- Loan Purpose: {loan_purpose}
- Requested Amount: ${requested_amount:,.0f}
- Requested Term: {requested_term} months
- Property Value (if applicable): ${property_value:,.0f}

APPLICANT FINANCIAL PROFILE:
- Annual Income: ${annual_income:,.0f}
- Employment Status: {employment_status}
- Employment Duration: {employment_duration}
- Employer: {employer}
- Monthly Debt Obligations: ${monthly_debts:,.0f}

CREDIT BUREAU DATA:
- Credit Score: {credit_score}
- Credit History Length: {credit_history_years} years
- Open Accounts: {open_accounts}
- Late Payments (last 2 years): {late_payments}
- Collections: {collections}
- Bankruptcies: {bankruptcies}
- Current Total Debt: ${total_debt:,.0f}

ADDITIONAL INFORMATION:
{additional_info}
"""


def analyze_application(application: dict, api_key: str) -> dict:
    """Run AI underwriting analysis on a loan application."""
    client = anthropic.Anthropic(api_key=api_key)

    prompt = UNDERWRITING_PROMPT.format(**application)

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text.strip()
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        response_text = "\n".join(lines)

    return json.loads(response_text)


def calculate_basic_ratios(application: dict) -> dict:
    """Calculate basic financial ratios without AI (for quick pre-screening)."""
    annual_income = application["annual_income"]
    monthly_income = annual_income / 12
    monthly_debts = application["monthly_debts"]
    requested_amount = application["requested_amount"]
    requested_term = application["requested_term"]
    property_value = application.get("property_value", 0)

    # Estimate monthly payment (simple calculation at ~7% APR)
    rate = 0.07 / 12
    if rate > 0 and requested_term > 0:
        monthly_payment = requested_amount * (rate * (1 + rate) ** requested_term) / ((1 + rate) ** requested_term - 1)
    else:
        monthly_payment = requested_amount / max(requested_term, 1)

    dti = ((monthly_debts + monthly_payment) / monthly_income * 100) if monthly_income > 0 else 999
    ltv = (requested_amount / property_value * 100) if property_value > 0 else None
    pti = (monthly_payment / monthly_income * 100) if monthly_income > 0 else 999

    return {
        "monthly_payment_est": round(monthly_payment, 2),
        "dti_pct": round(dti, 1),
        "ltv_pct": round(ltv, 1) if ltv else None,
        "pti_pct": round(pti, 1),
        "disposable_after_payment": round(monthly_income - monthly_debts - monthly_payment, 2),
    }
