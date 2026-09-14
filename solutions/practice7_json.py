"""REFERENCE SOLUTION — Step 7: Structured / JSON output

Try it yourself first! You'll learn far more from a broken script you debug
than from a working one you copied. Come back here when you're genuinely
stuck, or afterwards to compare approaches.

Exercise file this corresponds to: exercises/practice7_json.py
Graded by:                        .github/scripts/check_step7.py

To use: copy this file to exercises/practice7_json.py, then run
    python exercises/practice7_json.py
"""

import json
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
config = {"ICA_API_KEY": os.environ.get("ICA_API_KEY")}

client = Anthropic(
    api_key=config["ICA_API_KEY"],
    base_url="https://api.servicesessentials.ibm.com",
)

message = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=200,
    messages=[{
        "role": "user",
        "content": (
            "Respond with ONLY a JSON object (no markdown, no extra text) "
            "describing a fictional person with exactly two fields: "
            "'name' (string) and 'age' (integer)."
        ),
    }],
)

raw_text = next(b.text for b in message.content if b.type == "text")
cleaned = raw_text.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
data = json.loads(cleaned)

print("raw:", raw_text)
print("parsed name:", data["name"])
print("parsed age:", data["age"])
print("age type:", type(data["age"]).__name__)
