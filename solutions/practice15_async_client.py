"""REFERENCE SOLUTION — Step 15: Async Client: `AsyncAnthropic`

Try it yourself first! You'll learn far more from a broken script you debug
than from a working one you copied. Come back here when you're genuinely
stuck, or afterwards to compare approaches.

Exercise file this corresponds to: exercises/practice15_async_client.py
Graded by:                        .github/scripts/check_step15.py

To use: copy this file to exercises/practice15_async_client.py, then run
    python exercises/practice15_async_client.py
"""

import os                                  # 1
import asyncio                             # 2
from dotenv import load_dotenv             # 3
from anthropic import AsyncAnthropic       # 4

load_dotenv()                              # 5
config = {"ICA_API_KEY": os.environ.get("ICA_API_KEY")}   # 6

client = AsyncAnthropic(                   # 7
    api_key=config["ICA_API_KEY"],         # 8
    base_url="https://api.servicesessentials.ibm.com",    # 9
)

async def ask(question: str) -> str:       # 10
    message = await client.messages.create(               # 11
        model="claude-sonnet-5",           # 12
        max_tokens=50,                     # 13
        messages=[{"role": "user", "content": question}],  # 14
    )
    return next(b.text for b in message.content if b.type == "text")  # 15

async def main() -> None:                  # 16
    results = await asyncio.gather(        # 17
        ask("What is the capital of Italy? One word."),    # 18
        ask("What is 9 times 9? Just the number."),        # 19
    )
    print("answer_1:", results[0])         # 20
    print("answer_2:", results[1])         # 21

asyncio.run(main())                        # 22
