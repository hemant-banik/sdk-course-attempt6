import base64
import os
from io import BytesIO

from dotenv import load_dotenv
from PIL import Image
from anthropic import Anthropic

load_dotenv()
config = {"ICA_API_KEY": os.environ.get("ICA_API_KEY")}

client = Anthropic(
    api_key=config["ICA_API_KEY"],
    base_url="https://api.servicesessentials.ibm.com",
)

# Generate a small solid-red test image in memory (no file needed)
img = Image.new("RGB", (100, 100), color="red")
buffer = BytesIO()
img.save(buffer, format="PNG")
image_data = base64.standard_b64encode(buffer.getvalue()).decode("utf-8")

message = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=200,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/png",
                    "data": image_data,
                },
            },
            {"type": "text", "text": "What color is this image? Answer in one word."},
        ],
    }],
)
for block in message.content:
    if block.type == "text":
        print("color:", block.text)
        break
