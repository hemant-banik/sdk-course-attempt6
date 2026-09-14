"""REFERENCE SOLUTION — Step 8: Tool use

Try it yourself first! You'll learn far more from a broken script you debug
than from a working one you copied. Come back here when you're genuinely
stuck, or afterwards to compare approaches.

Exercise file this corresponds to: exercises/practice8_tools.py
Graded by:                        .github/scripts/check_step8.py

To use: copy this file to exercises/practice8_tools.py, then run
    python exercises/practice8_tools.py
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

tools = [{
    "name": "get_weather",
    "description": "Get the current weather for a city.",
    "input_schema": {
        "type": "object",
        "properties": {"city": {"type": "string", "description": "City name"}},
        "required": ["city"],
    },
}]

user_question = "What's the weather in Paris?"

message = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=300,
    tools=tools,
    messages=[{"role": "user", "content": user_question}],
)

print("stop_reason:", message.stop_reason)

if message.stop_reason == "tool_use":
    tool_use_block = next(b for b in message.content if b.type == "tool_use")
    print("tool name:", tool_use_block.name)
    print("tool input:", tool_use_block.input)

    # A real integration would call a weather API here. We hardcode a result.
    result = "18°C, partly cloudy"

    follow_up = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=300,
        tools=tools,
        messages=[
            {"role": "user", "content": user_question},
            {"role": "assistant", "content": message.content},
            {
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use_block.id,
                    "content": result,
                }],
            },
        ],
    )
    for block in follow_up.content:
        if block.type == "text":
            print("final answer:", block.text)
            break
