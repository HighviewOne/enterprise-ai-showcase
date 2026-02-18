"""AI Mortgage Consultant engine - loan matching and affordability analysis."""

import json
import anthropic

MORTGAGE_PROMPT = """\
You are an expert mortgage consultant and real estate financial advisor. Analyze \
the buyer's financial profile and provide personalized mortgage product recommendations, \
affordability analysis, and a home buying action plan.

DISCLAIMER: This is for educational purposes only. Not financial advice.
Consult a licensed mortgage lender for official pre-approval.

Return a JSON object:

{{
  "disclaimer": "For educational purposes only. Consult a licensed mortgage professional.",

  "financial_assessment": {{
    "readiness_score": <0-100>,
    "readiness_level": "Not Ready | Getting Close | Ready | Strong Candidate",
    "monthly_budget_for_housing": <number>,
    "max_home_price": <number>,
    "comfortable_home_price": <number>,
    "dti_ratio_current": <number as percentage>,
    "dti_ratio_projected": <number as percentage>,
    "strengths": ["financial strength 1"],
    "concerns": ["financial concern 1"],
    "improvements_needed": ["improvement 1"]
  }},

  "loan_recommendations": [
    {{
      "loan_type": "Conventional 30yr | Conventional 15yr | FHA | VA | USDA | Jumbo | ARM",
      "recommended": true|false,
      "fit_score": <1-10>,
      "estimated_rate": "X.XX%",
      "estimated_monthly_payment": <number>,
      "down_payment_required": "Minimum % and $ amount",
      "pmi_required": true|false,
      "pmi_monthly": <number or 0>,
      "total_monthly_cost": <number>,
      "pros": ["advantage 1"],
      "cons": ["disadvantage 1"],
      "best_for": "When this loan type is ideal",
      "qualification_likelihood": "High | Medium | Low"
    }}
  ],

  "affordability_breakdown": {{
    "home_price": <comfortable price>,
    "down_payment": <amount>,
    "loan_amount": <amount>,
    "monthly_principal_interest": <number>,
    "property_tax_monthly": <number>,
    "homeowners_insurance_monthly": <number>,
    "pmi_monthly": <number>,
    "hoa_estimate_monthly": <number>,
    "total_monthly_payment": <number>,
    "closing_costs_estimate": <number>,
    "cash_needed_at_closing": <number>,
    "emergency_fund_recommendation": <number>
  }},

  "market_insights": {{
    "market_condition": "Buyer's Market | Balanced | Seller's Market",
    "rate_environment": "Description of current rate trends",
    "timing_advice": "Whether now is a good time to buy",
    "location_considerations": ["consideration for the target area"],
    "price_trends": "Recent price trends in the area"
  }},

  "action_plan": [
    {{
      "step": <number>,
      "action": "What to do",
      "timeline": "When to do it",
      "details": "Specific details",
      "importance": "Critical | Important | Nice to Have"
    }}
  ],

  "tips": {{
    "credit_optimization": ["tip to improve credit for better rates"],
    "savings_strategies": ["way to save for down payment"],
    "negotiation_tips": ["tip for negotiating home purchase"],
    "mistakes_to_avoid": ["common first-time buyer mistake"]
  }}
}}

Be realistic with rates and calculations. Provide actionable, specific advice.

IMPORTANT: Return ONLY the JSON object.

---

BUYER PROFILE:
- Buyer Type: {buyer_type}
- Annual Household Income: {income}
- Monthly Debts: {monthly_debts}
- Credit Score: {credit_score}
- Savings / Down Payment Available: {savings}
- Target Location: {location}
- Target Home Price Range: {price_range}
- Property Type: {property_type}
- Timeline: {timeline}
- Employment: {employment}
- Additional Context: {context}
"""


def analyze_mortgage(config: dict, api_key: str) -> dict:
    """Analyze financial profile and recommend mortgage products."""
    client = anthropic.Anthropic(api_key=api_key)
    prompt = MORTGAGE_PROMPT.format(**config)
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
