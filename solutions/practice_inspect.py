"""REFERENCE SOLUTION — Step 3: Inspect the full response object

Try it yourself first! You'll learn far more from a broken script you debug
than from a working one you copied. Come back here when you're genuinely
stuck, or afterwards to compare approaches.

Exercise file this corresponds to: exercises/practice_inspect.py
Graded by:                        .github/scripts/check_step3.py

To use: copy this file to exercises/practice_inspect.py, then run
    python exercises/practice_inspect.py
"""

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
    max_tokens=100,
    messages=[{"role": "user", "content": "Name one planet."}],
)
print("id:", message.id)
print("model:", message.model)
print("role:", message.role)
print("stop_reason:", message.stop_reason)
print("usage:", message.usage)

# Some models put a ThinkingBlock before the TextBlock in content[],
# so search by block.type instead of assuming content[0] is text.
for block in message.content:
    if block.type == "text":
        print("text:", block.text)
        break
