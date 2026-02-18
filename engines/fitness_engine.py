"""AI Fitness Coach engine - analyzes workouts and provides coaching."""

import json
import anthropic

ANALYSIS_PROMPT = """\
You are an expert personal trainer, exercise scientist, and fitness coach.
Analyze the user's workout log and fitness profile to provide personalized
coaching, progress insights, and recommendations.

Return a JSON object:

{{
  "athlete_profile_summary": "One-line summary of the user's fitness level and goals",

  "workout_analysis": [
    {{
      "session": "Workout label (e.g., Day 1 - Upper Body)",
      "effectiveness_score": <1-10>,
      "volume_assessment": "Too Low | Appropriate | Too High",
      "intensity_assessment": "Too Light | Moderate | Heavy | Too Heavy",
      "strengths": ["what was done well"],
      "improvements": ["what could be better"],
      "muscle_groups_hit": ["chest", "triceps", "shoulders"]
    }}
  ],

  "progress_insights": {{
    "overall_consistency": "Excellent | Good | Needs Improvement",
    "estimated_training_age": "Beginner (0-1yr) | Intermediate (1-3yr) | Advanced (3+yr)",
    "strength_trend": "Progressing | Plateaued | Declining",
    "volume_trend": "Increasing | Stable | Decreasing",
    "key_observations": ["observation 1", "observation 2"],
    "potential_plateaus": ["area that may stall soon"]
  }},

  "weekly_split_review": {{
    "current_split_type": "e.g., Push/Pull/Legs, Upper/Lower, Full Body, Bro Split",
    "balance_assessment": "Well-balanced | Needs adjustment",
    "muscle_coverage": {{
      "well_trained": ["muscle groups getting enough work"],
      "undertrained": ["muscle groups needing more work"],
      "overtrained": ["muscle groups potentially overworked"]
    }},
    "recovery_assessment": "Adequate | Needs more rest | Could train more"
  }},

  "recommendations": {{
    "immediate_changes": ["change to make this week"],
    "program_adjustments": ["longer-term program tweaks"],
    "exercise_swaps": [
      {{"current": "exercise to swap out", "suggested": "better alternative", "reason": "why"}}
    ],
    "nutrition_tips": ["nutrition suggestion relevant to goals"],
    "recovery_tips": ["recovery/sleep suggestion"]
  }},

  "next_workout_suggestion": {{
    "focus": "What to train next",
    "exercises": [
      {{"exercise": "name", "sets": <num>, "reps": "rep range", "notes": "coaching cue"}}
    ],
    "warm_up": "Suggested warm-up routine",
    "duration_estimate": "Estimated workout duration"
  }},

  "motivation": {{
    "wins": ["positive things to celebrate"],
    "quote": "A motivational quote or message",
    "weekly_challenge": "A fun challenge for the week"
  }}
}}

Be specific, actionable, and encouraging. Base suggestions on exercise science principles.

IMPORTANT: Return ONLY the JSON object.

---

FITNESS PROFILE:
- Name: {name}
- Age: {age}, Gender: {gender}
- Height: {height}, Weight: {weight}
- Goal: {goal}
- Experience Level: {experience}
- Days per Week Available: {days_per_week}
- Equipment Access: {equipment}
- Injuries/Limitations: {limitations}

WORKOUT LOG:
{workout_log}

ADDITIONAL NOTES: {notes}
"""


def analyze_fitness(config: dict, api_key: str) -> dict:
    """Analyze workout log and provide coaching recommendations."""
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
