"""AI Property Search engine - generates personalized property recommendations."""

import json
import anthropic

SEARCH_PROMPT = """\
You are an expert real estate advisor. Based on the user's preferences, generate
realistic property recommendations with detailed analysis. Create plausible listings
that match real-world market conditions for the specified area.

Return a JSON object:

{{
  "search_summary": "2-3 sentence summary of what you found and market conditions.",
  "listings": [
    {{
      "id": "PROP-001",
      "title": "Descriptive listing title",
      "type": "{search_type}",
      "property_type": "House | Condo | Apartment | Townhouse | Multi-family",
      "address": "Realistic address in the specified area",
      "neighborhood": "Neighborhood name",
      "price": <number>,
      "price_per_sqft": <number>,
      "bedrooms": <int>,
      "bathrooms": <float>,
      "sqft": <int>,
      "year_built": <int>,
      "lot_size": "e.g., 0.25 acres or N/A for condos",
      "features": ["feature 1", "feature 2", "feature 3"],
      "pros": ["pro 1", "pro 2"],
      "cons": ["con 1"],
      "match_score": <0-100 how well it matches preferences>,
      "match_reasons": ["Why this matches", "preference 2 met"],
      "estimated_monthly": <number for mortgage/rent estimate>
    }}
  ],
  "neighborhood_insights": [
    {{
      "name": "Neighborhood name",
      "vibe": "Brief character description",
      "walk_score": <0-100>,
      "transit_score": <0-100>,
      "school_rating": "<Good|Average|Below Average>",
      "median_price": <number>,
      "price_trend": "Rising | Stable | Declining",
      "best_for": "Who this neighborhood is best for"
    }}
  ],
  "market_analysis": {{
    "median_price_area": <number>,
    "inventory_level": "Low | Moderate | High",
    "days_on_market_avg": <int>,
    "market_type": "Seller's Market | Balanced | Buyer's Market",
    "price_trend_12mo": "+X% or -X%",
    "advice": "Strategic advice for the buyer/renter given market conditions."
  }},
  "financial_summary": {{
    "budget_fit": "Under Budget | On Budget | Stretch",
    "monthly_range": "$X,XXX - $X,XXX",
    "down_payment_20pct": <number or null if renting>,
    "closing_costs_est": <number or null if renting>,
    "tips": ["Financial tip 1", "Tip 2"]
  }}
}}

Generate 4-5 realistic listings. Vary the options to show range.
Match prices to the actual market for the specified location.

IMPORTANT: Return ONLY the JSON object.

---

SEARCH CRITERIA:
- Location: {location}
- Search Type: {search_type}
- Budget: ${budget_min:,.0f} - ${budget_max:,.0f}
- Bedrooms: {bedrooms}
- Bathrooms: {bathrooms}
- Min Square Feet: {min_sqft}
- Property Types: {property_types}
- Must-Haves: {must_haves}
- Nice-to-Haves: {nice_to_haves}
- Deal-Breakers: {deal_breakers}
- Lifestyle Priorities: {lifestyle}
- Additional Notes: {notes}
"""


def search_properties(config: dict, api_key: str) -> dict:
    client = anthropic.Anthropic(api_key=api_key)
    prompt = SEARCH_PROMPT.format(**config)
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
