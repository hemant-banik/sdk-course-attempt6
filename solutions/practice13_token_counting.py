"""REFERENCE SOLUTION — Step 13: Count tokens before you spend them

Try it yourself first! You'll learn far more from a broken script you debug
than from a working one you copied. Come back here when you're genuinely
stuck, or afterwards to compare approaches.

Exercise file this corresponds to: exercises/practice13_token_counting.py
Graded by:                        .github/scripts/check_step13.py

To use: copy this file to exercises/practice13_token_counting.py, then run
    python exercises/practice13_token_counting.py
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

short_count = client.messages.count_tokens(
    model="claude-sonnet-5",
    messages=[{"role": "user", "content": "Hi"}],
)
long_count = client.messages.count_tokens(
    model="claude-sonnet-5",
    messages=[{
        "role": "user",
        "content": (
            "Please write a detailed, three-paragraph explanation of how "
            "photosynthesis works, including the role of chlorophyll and "
            "sunlight."
        ),
    }],
)
print("short_tokens:", short_count.input_tokens)
print("long_tokens:", long_count.input_tokens)
