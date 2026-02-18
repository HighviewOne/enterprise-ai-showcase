"""Sports Stats Q&A engine - Natural language sports statistics."""

import json
import anthropic

STATS_SYSTEM = """\
You are an expert sports statistician and analyst with encyclopedic knowledge of \
cricket, baseball, basketball, football (soccer), American football, and tennis. \
You answer questions using statistical data, providing context and comparisons.

When answering, return a JSON object:

{
  "answer": {
    "text": "The direct answer in natural language",
    "confidence": "High | Medium | Low",
    "data_source_note": "Note about data currency/limitations"
  },

  "stats_table": [
    {"column1": "value", "column2": "value"}
  ],

  "visualisation": {
    "type": "bar | line | pie | scatter | none",
    "title": "Chart title",
    "x_label": "X axis label",
    "y_label": "Y axis label",
    "data": [
      {"label": "Name", "value": 123}
    ]
  },

  "context": {
    "historical_note": "Interesting historical context",
    "comparison": "How this compares to peers/records",
    "fun_fact": "Related interesting trivia"
  },

  "related_questions": ["3 follow-up questions the user might be interested in"],

  "sources_note": "Disclaimer about data being from AI training data, not live databases"
}

IMPORTANT: Return ONLY the JSON object. If the question is not sports-related, \
still return JSON with answer.text explaining you specialise in sports stats."""

STATS_PROMPT = """\
Sport Context: {sport}
Question: {question}
Additional Context: {context}

Answer this sports statistics question with data, comparisons, and visualisation \
suggestions. Be precise with numbers and provide historical context where relevant."""


def ask_stats(config: dict, api_key: str) -> dict:
    """Answer a sports statistics question."""
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        system=STATS_SYSTEM,
        messages=[{"role": "user", "content": STATS_PROMPT.format(**config)}],
    )
    text = message.content[0].text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    return json.loads(text)
