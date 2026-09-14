"""REFERENCE SOLUTION — Step 2: Your first `messages.create()` call

Try it yourself first! You'll learn far more from a broken script you debug
than from a working one you copied. Come back here when you're genuinely
stuck, or afterwards to compare approaches.

Exercise file this corresponds to: exercises/practice_message.py
Graded by:                        .github/scripts/check_step2.py

To use: copy this file to exercises/practice_message.py, then run
    python exercises/practice_message.py
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
    messages=[{"role": "user", "content": "What is 2 + 2?"}],
)

# Some models (e.g. with extended thinking on) put a ThinkingBlock BEFORE
# the TextBlock, so content[0] isn't always text. Search by type instead.
for block in message.content:
    if block.type == "text":
        print(block.text)
        break
