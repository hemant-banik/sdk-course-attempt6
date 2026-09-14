"""REFERENCE SOLUTION — Step 12: Prompt caching

Try it yourself first! You'll learn far more from a broken script you debug
than from a working one you copied. Come back here when you're genuinely
stuck, or afterwards to compare approaches.

Exercise file this corresponds to: exercises/practice12_caching.py
Graded by:                        .github/scripts/check_step12.py

To use: copy this file to exercises/practice12_caching.py, then run
    python exercises/practice12_caching.py
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

# A long block of repeated text to make caching worthwhile.
long_context = "The quick brown fox jumps over the lazy dog. " * 400

system_blocks = [
    {
        "type": "text",
        "text": long_context,
        "cache_control": {"type": "ephemeral"},
    }
]

# First call: writes to the cache.
first = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=100,
    system=system_blocks,
    messages=[{"role": "user", "content": "In one short sentence, what animal is mentioned above?"}],
)
print("first cache_creation_input_tokens:", first.usage.cache_creation_input_tokens)
print("first cache_read_input_tokens:", first.usage.cache_read_input_tokens)

# Second call with the identical cached block: reads from the cache.
second = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=100,
    system=system_blocks,
    messages=[{"role": "user", "content": "In one short sentence, what animal is mentioned above?"}],
)
print("second cache_creation_input_tokens:", second.usage.cache_creation_input_tokens)
print("second cache_read_input_tokens:", second.usage.cache_read_input_tokens)
