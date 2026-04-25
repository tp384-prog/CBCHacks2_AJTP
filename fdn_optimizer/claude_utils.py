import os
import json
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def parse_input(raw_text):
    """
    Prompt 1: Takes free-text coordinator input.
    Returns a clean Python dict with donations list.
    """
    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        system="""You are a logistics assistant for a food rescue nonprofit called
Friendship Donations Network in Ithaca, NY.

Parse the user description of today's food donations into a JSON object.
Return ONLY valid JSON — no explanation, no markdown, no code blocks.

Use exactly this structure:
{
  "donations": [
    {
      "name": "donor organization name e.g. Wegmans",
      "item": "type of food e.g. produce, bread, canned goods",
      "quantity": 80,
      "location": [42.4440, -76.5019],
      "expiry": "2026-04-25T15:00:00"
    }
  ]
}

Rules:
- name is the donor organization
- item is the type of food being donated
- quantity is in lbs as an integer
- location is [lat, lng] as floats
- expiry is ISO 8601 datetime string, always date 2026-04-25
- If location is unknown, use [42.4440, -76.5019] (downtown Ithaca)
- If expiry is unknown, use 2026-04-25T18:00:00 (end of day)
- Extract one entry per distinct donor mentioned""",
        messages=[{"role": "user", "content": raw_text}]
    )

    raw = response.content[0].text.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Claude occasionally wraps in markdown — strip it
        cleaned = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)


def narrate_routes(assignments, unroutable):
    """
    Prompt 2: Takes optimizer output.
    Returns a plain-English daily briefing per driver.
    """
    payload = {
        "assignments": assignments,
        "unroutable": unroutable
    }

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        system="""You are a logistics coordinator for Friendship Donations Network,
a food rescue nonprofit in Ithaca NY.

Write a clear, practical daily briefing for volunteer drivers based on
the route assignments provided. Format it as follows:

For each driver:
- Driver name as a header
- Each stop listed with: pantry name, what they are delivering, quantity in lbs
- Remind them of any time-sensitive deliveries (items expiring soon)

Then a short section for any unroutable donations explaining they could
not be assigned and why (expired, no capacity, time window missed).

Be concise and warm — these are volunteers doing important community work.""",
        messages=[{
            "role": "user",
            "content": f"Here are today's assignments:\n{json.dumps(payload, indent=2)}"
        }]
    )

    return response.content[0].text


# --- Test both prompts in isolation ---
if __name__ == "__main__":
    print("=== Testing Prompt 1: parse_input ===")
    test_input = (
        "We have 80 lbs of produce from Wegmans expiring at 3pm, "
        "and 40 loaves from Purity Bakery good until 5pm. "
        "3 drivers available 10am to 3pm."
    )
    result = parse_input(test_input)
    print(json.dumps(result, indent=2))

    print("\n=== Testing Prompt 2: narrate_routes ===")
    mock_assignments = [
        {"driver": "Driver 1", "donation": "Wegmans", "quantity": 80,
         "pantry": "Loaves and Fishes", "travel_seconds": 420},
        {"driver": "Driver 2", "donation": "Purity Bakery", "quantity": 40,
         "pantry": "REACH Medical Pantry", "travel_seconds": 600},
    ]
    mock_unroutable = []
    briefing = narrate_routes(mock_assignments, mock_unroutable)
    print(briefing)