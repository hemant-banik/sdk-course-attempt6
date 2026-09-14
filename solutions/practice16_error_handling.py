"""REFERENCE SOLUTION — Step 16: Error Handling: `APIError`, `RateLimitError`, `APIStatusError`

Try it yourself first! You'll learn far more from a broken script you debug
than from a working one you copied. Come back here when you're genuinely
stuck, or afterwards to compare approaches.

Exercise file this corresponds to: exercises/practice16_error_handling.py
Graded by:                        .github/scripts/check_step16.py

To use: copy this file to exercises/practice16_error_handling.py, then run
    python exercises/practice16_error_handling.py
"""

import os                                        # 1
import anthropic                                 # 2
from dotenv import load_dotenv                   # 3

load_dotenv()                                    # 4
config = {"ICA_API_KEY": os.environ.get("ICA_API_KEY")}   # 5

client = anthropic.Anthropic(                    # 6
    api_key=config["ICA_API_KEY"],               # 7
    base_url="https://api.servicesessentials.ibm.com",    # 8
)

try:                                             # 9
    client.messages.create(                      # 10
        model="claude-does-not-exist-9000",       # 11
        max_tokens=100,                          # 12
        messages=[{"role": "user", "content": "Hi"}],     # 13
    )
    print("No error was raised — this should not happen!")  # 14
except anthropic.APIStatusError as e:            # 15
    print("error_type:", type(e).__name__)       # 16
    print("error_message:", str(e))              # 17
