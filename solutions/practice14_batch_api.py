"""REFERENCE SOLUTION — Step 14: Batch API: create, poll, retrieve results

Try it yourself first! You'll learn far more from a broken script you debug
than from a working one you copied. Come back here when you're genuinely
stuck, or afterwards to compare approaches.

Exercise file this corresponds to: exercises/practice14_batch_api.py
Graded by:                        .github/scripts/check_step14.py

To use: copy this file to exercises/practice14_batch_api.py, then run
    python exercises/practice14_batch_api.py
"""

import os
import time
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
config = {"ICA_API_KEY": os.environ.get("ICA_API_KEY")}

client = Anthropic(
    api_key=config["ICA_API_KEY"],
    base_url="https://api.servicesessentials.ibm.com",
)

message_batch = client.messages.batches.create(requests=[
    {
        "custom_id": "capital-question",
        "params": {
            "model": "claude-sonnet-5",
            "max_tokens": 50,
            "messages": [{"role": "user", "content": "What is the capital of France? One word."}],
        },
    },
    {
        "custom_id": "math-question",
        "params": {
            "model": "claude-sonnet-5",
            "max_tokens": 50,
            "messages": [{"role": "user", "content": "What is 7 times 6? Just the number."}],
        },
    },
])
print("batch_id:", message_batch.id)
print("initial_status:", message_batch.processing_status)

# Short, bounded polling loop — batches usually finish within minutes
for attempt in range(30):
    batch = client.messages.batches.retrieve(message_batch.id)
    print(f"poll_attempt_{attempt + 1}:", batch.processing_status)
    if batch.processing_status == "ended":
        break
    time.sleep(10)

succeeded, errored = 0, 0
for result in client.messages.batches.results(message_batch.id):
    if result.result.type == "succeeded":
        succeeded += 1
        text = next(b.text for b in result.result.message.content if b.type == "text")
        print(result.custom_id, "SUCCEEDED ->", text)
    elif result.result.type == "errored":
        errored += 1
        print(result.custom_id, "ERRORED ->", result.result.error)

print("succeeded:", succeeded)
print("errored:", errored)
