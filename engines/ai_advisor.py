"""LLM-powered market assessment and strategic recommendations."""

import json
import anthropic


MARKET_ASSESSMENT_PROMPT = """\
You are an expert business analyst and market strategist.

A company is evaluating expanding their product into a new market. Based on the inputs and
financial projections below, provide a strategic assessment.

Return your analysis as a JSON object with exactly these fields:

{{
  "market_assessment": {{
    "market_attractiveness": "<High|Medium|Low>",
    "competitive_intensity": "<High|Medium|Low>",
    "entry_barriers": "<High|Medium|Low>",
    "market_summary": "2-3 sentence summary of market conditions and outlook."
  }},
  "risk_factors": [
    {{"risk": "description", "severity": "<High|Medium|Low>", "mitigation": "suggested mitigation"}},
    ...
  ],
  "recommendations": [
    "Actionable recommendation 1",
    "Actionable recommendation 2",
    ...
  ],
  "go_no_go": {{
    "verdict": "<Strong Go|Go|Cautious Go|No Go>",
    "confidence": "<High|Medium|Low>",
    "reasoning": "2-3 sentence justification."
  }},
  "sensitivity_notes": "Brief notes on which assumptions the ROI is most sensitive to."
}}

IMPORTANT: Return ONLY the JSON object, no other text.

---

PROJECT DETAILS:
- Product: {product_name}
- Description: {product_description}
- Target Market: {target_market}

FINANCIAL INPUTS:
- Initial Investment: ${initial_investment:,.0f}
- Annual Operating Cost: ${annual_operating_cost:,.0f}
- Total Addressable Market: {total_addressable_market:,} participants
- Qualifying Ratio: {qualifying_ratio_pct}%
- Expected Hit Rate: {hit_rate_pct}%
- Avg Annual License: ${avg_annual_license:,.0f}
- Revenue Start: Month {revenue_start_month}
- Projection Period: {projection_years} years

SCENARIO RESULTS (Most Likely):
- Expected Customers: {ml_customers}
- Total Revenue: ${ml_revenue:,.0f}
- Total Costs: ${ml_costs:,.0f}
- Net Profit: ${ml_profit:,.0f}
- ROI: {ml_roi}%
- NPV: ${ml_npv:,.0f}
- Payback: {ml_payback} months

SCENARIO RESULTS (Optimistic):
- ROI: {opt_roi}% | NPV: ${opt_npv:,.0f}

SCENARIO RESULTS (Pessimistic):
- ROI: {pess_roi}% | NPV: ${pess_npv:,.0f}
"""


def get_ai_assessment(inputs, scenarios: dict, api_key: str) -> dict:
    """Get AI-powered market assessment and recommendations."""
    client = anthropic.Anthropic(api_key=api_key)

    ml = scenarios["most_likely"]
    opt = scenarios["optimistic"]
    pess = scenarios["pessimistic"]

    prompt = MARKET_ASSESSMENT_PROMPT.format(
        product_name=inputs.product_name,
        product_description=inputs.product_description,
        target_market=inputs.target_market,
        initial_investment=inputs.initial_investment,
        annual_operating_cost=inputs.annual_operating_cost,
        total_addressable_market=inputs.total_addressable_market,
        qualifying_ratio_pct=inputs.qualifying_ratio_pct,
        hit_rate_pct=inputs.hit_rate_pct,
        avg_annual_license=inputs.avg_annual_license,
        revenue_start_month=inputs.revenue_start_month,
        projection_years=inputs.projection_years,
        ml_customers=ml.customer_count,
        ml_revenue=ml.total_revenue,
        ml_costs=ml.total_costs,
        ml_profit=ml.total_profit,
        ml_roi=ml.roi_pct,
        ml_npv=ml.npv,
        ml_payback=ml.payback_month or "N/A",
        opt_roi=opt.roi_pct,
        opt_npv=opt.npv,
        pess_roi=pess.roi_pct,
        pess_npv=pess.npv,
    )

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
