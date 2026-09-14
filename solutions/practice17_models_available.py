"""REFERENCE SOLUTION — Step 17: Compare models: same call, different model string

Try it yourself first! You'll learn far more from a broken script you debug
than from a working one you copied. Come back here when you're genuinely
stuck, or afterwards to compare approaches.

Exercise file this corresponds to: exercises/practice17_models_available.py
Graded by:                        .github/scripts/check_step17.py

To use: copy this file to exercises/practice17_models_available.py, then run
    python exercises/practice17_models_available.py
"""

import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.environ["ICA_API_KEY"],
    base_url="https://api.servicesessentials.ibm.com",
)

prompt = "In one sentence, what is your name/model family?"

# Note: we deliberately use Sonnet + Haiku here, NOT Opus — Opus costs
# roughly 5x more per token and this exercise doesn't need that horsepower.
for model_name in ["claude-sonnet-5", "claude-haiku-4-5"]:
    message = client.messages.create(
        model=model_name,
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}],
    )
    print("model:", message.model)
    print("stop_reason:", message.stop_reason)
