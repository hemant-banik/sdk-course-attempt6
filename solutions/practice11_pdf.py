"""REFERENCE SOLUTION — Step 11: PDF support

Try it yourself first! You'll learn far more from a broken script you debug
than from a working one you copied. Come back here when you're genuinely
stuck, or afterwards to compare approaches.

Exercise file this corresponds to: exercises/practice11_pdf.py
Graded by:                        .github/scripts/check_step11.py

To use: copy this file to exercises/practice11_pdf.py, then run
    python exercises/practice11_pdf.py
"""

import base64
import os

from dotenv import load_dotenv
from anthropic import Anthropic
from reportlab.pdfgen import canvas

load_dotenv()
config = {"ICA_API_KEY": os.environ.get("ICA_API_KEY")}

client = Anthropic(
    api_key=config["ICA_API_KEY"],
    base_url="https://api.servicesessentials.ibm.com",
)

# Generate a one-page PDF containing a made-up "secret code"
pdf_path = "test_doc.pdf"
c = canvas.Canvas(pdf_path)
c.drawString(100, 700, "The secret code is 4471.")
c.save()
print("pdf created:", os.path.exists(pdf_path))

with open(pdf_path, "rb") as f:
    pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")

response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=200,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type": "base64",
                        "media_type": "application/pdf",
                        "data": pdf_data,
                    },
                },
                {"type": "text", "text": "What is the secret code mentioned in this document? Reply with just the number."},
            ],
        }
    ],
)
answer = next(b.text for b in response.content if b.type == "text")
print("answer:", answer)
