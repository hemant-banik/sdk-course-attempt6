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
    messages=[{"role": "user", "content": "What is 2 + 2?"}],
)

# Some models (e.g. with extended thinking on) put a ThinkingBlock BEFORE
# the TextBlock, so content[0] isn't always text. Search by type instead.
for block in message.content:
    if block.type == "text":
        print(block.text)
        break
