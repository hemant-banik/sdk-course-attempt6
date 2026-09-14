"""REFERENCE SOLUTION — Step 4: Message roles & multi-turn conversations

Try it yourself first! You'll learn far more from a broken script you debug
than from a working one you copied. Come back here when you're genuinely
stuck, or afterwards to compare approaches.

Exercise file this corresponds to: exercises/practice4_multiturn.py
Graded by:                        .github/scripts/check_step4.py

To use: copy this file to exercises/practice4_multiturn.py, then run
    python exercises/practice4_multiturn.py
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


def get_text(content_blocks):
    """Find the text block; some models put a ThinkingBlock first."""
    for block in content_blocks:
        if block.type == "text":
            return block.text
    return ""


messages = [{"role": "user", "content": "My name is Zara. Remember that."}]

first = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=200,
    messages=messages,
)
print("Turn 1:", get_text(first.content))

messages.append({"role": "assistant", "content": first.content})
messages.append({"role": "user", "content": "What is my name?"})

second = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=200,
    messages=messages,
)
print("Turn 2:", get_text(second.content))

messages.append({"role": "assistant", "content": second.content})
print("Messages in list:", len(messages))
