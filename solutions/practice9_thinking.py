"""REFERENCE SOLUTION — Step 9: Extended thinking

Try it yourself first! You'll learn far more from a broken script you debug
than from a working one you copied. Come back here when you're genuinely
stuck, or afterwards to compare approaches.

Exercise file this corresponds to: exercises/practice9_thinking.py
Graded by:                        .github/scripts/check_step9.py

To use: copy this file to exercises/practice9_thinking.py, then run
    python exercises/practice9_thinking.py
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
    max_tokens=2000,
    thinking={"type": "enabled", "budget_tokens": 1024},
    messages=[{"role": "user", "content": "What is 27 * 34? Think it through step by step."}],
)

thinking_text = ""
answer_text = ""
for block in message.content:
    if block.type == "thinking":
        thinking_text = block.thinking
    elif block.type == "text":
        answer_text = block.text

print("has thinking block:", bool(thinking_text))
print("thinking length:", len(thinking_text))
print("answer:", answer_text)
