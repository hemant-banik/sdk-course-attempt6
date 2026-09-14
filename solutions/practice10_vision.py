"""REFERENCE SOLUTION — Step 10: Vision: multiple images in one request

Try it yourself first! You'll learn far more from a broken script you debug
than from a working one you copied. Come back here when you're genuinely
stuck, or afterwards to compare approaches.

Exercise file this corresponds to: exercises/practice10_vision.py
Graded by:                        .github/scripts/check_step10.py

To use: copy this file to exercises/practice10_vision.py, then run
    python exercises/practice10_vision.py
"""

import base64
import io
import os

from dotenv import load_dotenv
from PIL import Image
from anthropic import Anthropic

load_dotenv()
config = {"ICA_API_KEY": os.environ.get("ICA_API_KEY")}

client = Anthropic(
    api_key=config["ICA_API_KEY"],
    base_url="https://api.servicesessentials.ibm.com",
)


def make_image_b64(color):
    img = Image.new("RGB", (32, 32), color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.standard_b64encode(buf.getvalue()).decode("utf-8")


image1_b64 = make_image_b64((220, 20, 20))   # red
image2_b64 = make_image_b64((20, 80, 220))   # blue

message = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=300,
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image1_b64}},
                {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": image2_b64}},
                {"type": "text", "text": "What color is the first image, and what color is the second? Answer in the form 'first: <color>, second: <color>'."},
            ],
        }
    ],
)

for block in message.content:
    if block.type == "text":
        print("answer:", block.text)
        break
