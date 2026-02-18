"""AI Event Planner engine - generates complete event plans."""

import json
import anthropic

EVENT_PLAN_PROMPT = """\
You are an expert event planner with 20 years of experience planning weddings, corporate
events, birthday parties, galas, and celebrations of all sizes. Create a detailed,
actionable event plan based on the user's requirements.

Return a JSON object:

{{
  "event_name": "A creative name for the event",
  "theme_suggestion": "A cohesive theme that ties everything together",
  "executive_summary": "2-3 sentence overview of the planned event",

  "budget_breakdown": [
    {{"category": "Venue", "estimated_cost": 5000, "percentage": 30, "notes": "Details"}},
    {{"category": "Catering", "estimated_cost": 3000, "percentage": 20, "notes": "Details"}}
  ],
  "total_estimated_cost": <number>,
  "budget_buffer_pct": 10,

  "venue_suggestions": [
    {{
      "name": "Venue Name",
      "type": "Hotel Ballroom | Garden | Restaurant | Rooftop | etc.",
      "capacity": "50-100 guests",
      "estimated_cost": 5000,
      "pros": ["pro 1", "pro 2"],
      "cons": ["con 1"],
      "best_for": "Why this venue fits"
    }}
  ],

  "vendor_recommendations": [
    {{
      "category": "Catering | Photography | DJ/Music | Florist | Decor | Cake | etc.",
      "what_to_look_for": "Key selection criteria",
      "estimated_cost_range": "$500-$1500",
      "booking_timeline": "Book 3 months ahead",
      "tips": "Insider tip"
    }}
  ],

  "timeline": {{
    "planning_milestones": [
      {{"weeks_before": 12, "task": "Book venue and caterer", "priority": "Critical"}},
      {{"weeks_before": 8, "task": "Send invitations", "priority": "High"}}
    ],
    "day_of_schedule": [
      {{"time": "10:00 AM", "activity": "Venue setup begins", "responsible": "Event coordinator"}},
      {{"time": "6:00 PM", "activity": "Guests arrive", "responsible": "Host"}}
    ]
  }},

  "menu_suggestions": [
    {{
      "course": "Appetizers | Main Course | Dessert | Drinks",
      "options": ["Option 1", "Option 2", "Option 3"],
      "dietary_notes": "Vegetarian/vegan alternatives included"
    }}
  ],

  "decor_and_ambiance": {{
    "color_palette": ["Color 1", "Color 2", "Color 3"],
    "key_elements": ["element 1", "element 2"],
    "lighting": "Description of lighting approach",
    "music_vibe": "Description of music/entertainment approach"
  }},

  "guest_experience": [
    "Touchpoint 1: What guests experience on arrival",
    "Touchpoint 2: Key moment during event"
  ],

  "checklist": [
    {{"item": "Task description", "category": "Venue | Catering | Decor | Logistics | Guest Management", "status": "To Do"}}
  ],

  "contingency_plans": [
    {{"risk": "Bad weather for outdoor event", "plan": "Reserve indoor backup space"}}
  ],

  "pro_tips": ["Tip 1 from an experienced planner", "Tip 2"]
}}

Ensure the total budget stays within the specified range. Be creative but practical.
Tailor everything to the event type, guest count, and preferences.

IMPORTANT: Return ONLY the JSON object.

---

EVENT DETAILS:
- Event Type: {event_type}
- Location/City: {location}
- Event Date: {event_date}
- Start Time: {start_time}
- Guest Count: {guest_count_min} to {guest_count_max}
- Budget Range: ${budget_min:,.0f} to ${budget_max:,.0f}
- Style/Vibe: {style}

PREFERENCES:
- Must-Haves: {must_haves}
- Nice-to-Haves: {nice_to_haves}
- Things to Avoid: {things_to_avoid}
- Dietary Requirements: {dietary}

ADDITIONAL NOTES:
{additional_notes}
"""


def generate_event_plan(config: dict, api_key: str) -> dict:
    """Generate a complete event plan."""
    client = anthropic.Anthropic(api_key=api_key)

    prompt = EVENT_PLAN_PROMPT.format(**config)

    message = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = message.content[0].text.strip()
    if response_text.startswith("```"):
        lines = response_text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        response_text = "\n".join(lines)

    return json.loads(response_text)
