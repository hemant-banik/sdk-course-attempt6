import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
config = {"ICA_API_KEY": os.environ.get("ICA_API_KEY")}

client = Anthropic(
    api_key=config["ICA_API_KEY"],
    base_url="https://api.servicesessentials.ibm.com",
)

message = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=100,
    messages=[{"role": "user", "content": "Name one planet."}],
)
print("id:", message.id)
print("model:", message.model)
print("role:", message.role)
print("stop_reason:", message.stop_reason)
print("usage:", message.usage)

for block in message.content:
    if block.type == "text":
        print("text:", block.text)
        break
