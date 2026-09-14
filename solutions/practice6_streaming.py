"""REFERENCE SOLUTION — Step 6: Streaming responses

Try it yourself first! You'll learn far more from a broken script you debug
than from a working one you copied. Come back here when you're genuinely
stuck, or afterwards to compare approaches.

Exercise file this corresponds to: exercises/practice6_streaming.py
Graded by:                        .github/scripts/check_step6.py

To use: copy this file to exercises/practice6_streaming.py, then run
    python exercises/practice6_streaming.py
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

print("streaming:")
full_text = ""
with client.messages.stream(
    model="claude-sonnet-5",
    max_tokens=300,
    messages=[{"role": "user", "content": "Count from 1 to 5, one number per line."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
        full_text += text

    final_message = stream.get_final_message()

print()  # newline after the streamed text
print("stop_reason:", final_message.stop_reason)
print("chars streamed:", len(full_text))
