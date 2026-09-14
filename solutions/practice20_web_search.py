"""REFERENCE SOLUTION — Step 20: Web search tool (server-side)

Try it yourself first! You'll learn far more from a broken script you debug
than from a working one you copied. Come back here when you're genuinely
stuck, or afterwards to compare approaches.

Exercise file this corresponds to: exercises/practice20_web_search.py
Graded by:                        .github/scripts/check_step20.py

To use: copy this file to exercises/practice20_web_search.py, then run
    python exercises/practice20_web_search.py
"""

import anthropic                                                  # 1
import os                                                         # 2
from dotenv import load_dotenv                                    # 3

load_dotenv()                                                     # 4

client = anthropic.Anthropic(                                      # 5
    api_key=os.environ.get("ICA_API_KEY"),                         # 6
    base_url="https://api.servicesessentials.ibm.com",             # 7
)

response = client.messages.create(                                 # 8
    model="claude-sonnet-5",                                       # 9
    max_tokens=1024,                                               # 10
    messages=[{"role": "user", "content": "Use web search to tell me who Claude Shannon was, in one or two sentences."}],   # 11
    tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 3}],   # 12
)

block_types = [block.type for block in response.content]           # 13
print("block_types:", block_types)                                 # 14

for block in response.content:                                     # 15
    if block.type == "text":                                       # 16
        print("answer:", block.text)                               # 17
