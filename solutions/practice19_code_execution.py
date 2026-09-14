"""REFERENCE SOLUTION — Step 19: Code execution tool (server-side sandbox)

Try it yourself first! You'll learn far more from a broken script you debug
than from a working one you copied. Come back here when you're genuinely
stuck, or afterwards to compare approaches.

Exercise file this corresponds to: exercises/practice19_code_execution.py
Graded by:                        .github/scripts/check_step19.py

To use: copy this file to exercises/practice19_code_execution.py, then run
    python exercises/practice19_code_execution.py
"""

import anthropic                                   # 1
import os                                          # 2
from dotenv import load_dotenv                     # 3

load_dotenv()                                      # 4

client = anthropic.Anthropic(                      # 5
    api_key=os.environ.get("ICA_API_KEY"),         # 6
    base_url="https://api.servicesessentials.ibm.com",   # 7
)

response = client.messages.create(                 # 8
    model="claude-sonnet-5",                       # 9
    max_tokens=4096,                               # 10
    messages=[                                     # 11
        {"role": "user", "content": "Use code execution to find the mean of [1,...,10]. State the mean clearly in your final sentence."}
    ],
    tools=[{"type": "code_execution_20250825", "name": "code_execution"}],   # 12
)

for block in response.content:                     # 13
    if block.type == "text":                       # 14
        print("answer:", block.text)               # 15
