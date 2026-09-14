"""REFERENCE SOLUTION — Step 1: Install the SDK & create a client

Try it yourself first! You'll learn far more from a broken script you debug
than from a working one you copied. Come back here when you're genuinely
stuck, or afterwards to compare approaches.

Exercise file this corresponds to: exercises/practice1.py
Graded by:                        .github/scripts/check_step1.py

To use: copy this file to exercises/practice1.py, then run
    python exercises/practice1.py
"""

import os
import anthropic
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
config = {"ICA_API_KEY": os.environ.get("ICA_API_KEY")}

print("SDK version:", anthropic.__version__)

client = Anthropic(
    api_key=config["ICA_API_KEY"],
    base_url="https://api.servicesessentials.ibm.com",
)
print("Client type:", type(client).__name__)
