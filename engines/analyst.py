"""AI Stock Market Analysis engine."""

import json
import anthropic

ANALYSIS_PROMPT = """\
You are an expert financial analyst and investment advisor. Analyze the specified
stock(s) and provide a comprehensive investment analysis.

IMPORTANT DISCLAIMER: This is for educational purposes only. Not financial advice.
Past performance does not guarantee future results.

Return a JSON object:

{{
  "disclaimer": "This analysis is for educational purposes only and does not constitute financial advice.",
  "analysis_date": "Current date estimate",
  "stocks": [
    {{
      "ticker": "SYMBOL",
      "company_name": "Full company name",
      "sector": "Technology | Healthcare | Finance | etc.",
      "current_price_est": <number>,
      "market_cap": "e.g., $2.8T",

      "fundamental_analysis": {{
        "revenue_trend": "Growing | Stable | Declining",
        "profit_margin": "e.g., 25%",
        "pe_ratio": <number>,
        "pe_vs_industry": "Above | In-line | Below industry average",
        "debt_to_equity": <number>,
        "free_cash_flow": "Strong | Moderate | Weak",
        "dividend_yield": "e.g., 0.5% or N/A",
        "earnings_growth_5yr": "e.g., +15% annually",
        "moat": "Description of competitive advantage",
        "summary": "2-sentence fundamental summary"
      }},

      "technical_analysis": {{
        "trend": "Bullish | Neutral | Bearish",
        "support_level": <number>,
        "resistance_level": <number>,
        "rsi_indication": "Overbought | Neutral | Oversold",
        "moving_avg_signal": "Above 200-day MA (bullish) | Below (bearish)",
        "volume_trend": "Increasing | Normal | Decreasing",
        "summary": "2-sentence technical summary"
      }},

      "risk_assessment": {{
        "overall_risk": "Low | Medium | High | Very High",
        "volatility": "Low | Medium | High",
        "beta": <number>,
        "key_risks": ["risk 1", "risk 2", "risk 3"],
        "catalysts_positive": ["catalyst 1", "catalyst 2"],
        "catalysts_negative": ["negative catalyst 1"]
      }},

      "recommendation": {{
        "action": "Strong Buy | Buy | Hold | Sell | Strong Sell",
        "confidence": <0-100>,
        "time_horizon": "Short-term (1-3 mo) | Medium-term (3-12 mo) | Long-term (1-5 yr)",
        "target_price": <number>,
        "stop_loss": <number>,
        "reasoning": "2-3 sentence justification"
      }},

      "comparable_companies": [
        {{"ticker": "SYM", "name": "Name", "pe_ratio": <num>, "recommendation": "Brief note"}}
      ]
    }}
  ],

  "portfolio_suggestion": {{
    "allocation_strategy": "Description of suggested allocation",
    "diversification_notes": "Notes on portfolio diversification",
    "rebalancing_suggestion": "When/how to rebalance"
  }},

  "market_context": {{
    "market_sentiment": "Bullish | Neutral | Bearish",
    "key_macro_factors": ["factor 1", "factor 2"],
    "upcoming_events": ["event that could impact these stocks"]
  }}
}}

Use your training knowledge for approximate current values. Be realistic and balanced.

IMPORTANT: Return ONLY the JSON object.

---

ANALYSIS REQUEST:
- Stocks: {tickers}
- Investment Thesis: {thesis}
- Risk Tolerance: {risk_tolerance}
- Investment Horizon: {horizon}
- Portfolio Size: {portfolio_size}
- Additional Context: {context}
"""


def analyze_stocks(config: dict, api_key: str) -> dict:
    client = anthropic.Anthropic(api_key=api_key)
    prompt = ANALYSIS_PROMPT.format(**config)
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
