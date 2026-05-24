"""POS Recommendation engine - Payment system guidance for SMBs."""

from engines.llm import call_claude_json

POS_PROMPT = """\
You are an expert payment systems consultant helping small businesses choose the right \
POS (Point of Sale) system. Analyse the merchant's needs and recommend the best payment \
solutions with clear cost comparisons.

Return a JSON object:

{{
  "merchant_profile": {{
    "business_type": "Restaurant | Retail | Service | Food Truck | etc.",
    "size_category": "Micro | Small | Medium",
    "key_needs": ["prioritised needs"],
    "complexity_level": "Simple | Moderate | Complex"
  }},

  "recommendations": [
    {{
      "rank": <1-5>,
      "system": "POS system name",
      "best_for": "Why this is recommended",
      "monthly_cost": "$X/month",
      "transaction_fees": "X% + $X per transaction",
      "hardware_cost": "$X upfront",
      "total_first_year_estimate": "$X",
      "pros": ["advantages"],
      "cons": ["disadvantages"],
      "key_features": ["relevant features"],
      "contract_terms": "Month-to-month | Annual | Multi-year",
      "setup_difficulty": "Easy | Moderate | Complex",
      "best_fit_score": <1-100>
    }}
  ],

  "feature_comparison": [
    {{"feature": "Feature name", "importance": "Must-Have | Nice-to-Have | Optional",
      "system_1": "Yes/No/Limited", "system_2": "Yes/No/Limited", "system_3": "Yes/No/Limited"}}
  ],

  "cost_analysis": {{
    "monthly_volume_estimate": "$X",
    "cost_comparison": [
      {{"system": "Name", "monthly_software": "$X", "monthly_processing": "$X",
        "monthly_total": "$X", "annual_total": "$X"}}
    ],
    "hidden_costs_warning": ["costs merchants often miss"]
  }},

  "implementation_guide": [
    {{"step": <number>, "action": "What to do", "timeline": "When",
      "tips": "Helpful advice"}}
  ],

  "glossary": [
    {{"term": "Payment term", "definition": "Simple explanation"}}
  ],

  "final_recommendation": "Clear, confident recommendation with reasoning"
}}

Use simple, jargon-free language. Be transparent about all costs including hidden fees.

IMPORTANT: Return ONLY the JSON object.

---

MERCHANT DETAILS:
{merchant_details}

PARAMETERS:
- Business Type: {business_type}
- Monthly Sales Volume: {monthly_volume}
- Average Transaction: {avg_transaction}
- Priorities: {priorities}
- Current Setup: {current_setup}
"""


def recommend_pos(config: dict, api_key: str) -> dict:
    """Recommend POS systems for a merchant."""
    prompt = POS_PROMPT.format(**config)
    return call_claude_json(prompt, api_key, max_tokens=4096)
