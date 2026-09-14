"""REFERENCE SOLUTION — Step 18: Upload once, reference by ID

Try it yourself first! You'll learn far more from a broken script you debug
than from a working one you copied. Come back here when you're genuinely
stuck, or afterwards to compare approaches.

Exercise file this corresponds to: exercises/practice18_files_api.py
Graded by:                        .github/scripts/check_step18.py

To use: copy this file to exercises/practice18_files_api.py, then run
    python exercises/practice18_files_api.py
"""

import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

client = anthropic.Anthropic(
    api_key=os.environ["ICA_API_KEY"],
    base_url="https://api.servicesessentials.ibm.com",
)

# 1. Create something real to upload.
with open("upload_notes.txt", "w") as f:
    f.write("Claude is an AI model made by Anthropic. It can read text, images, and PDFs.")

# 2. Upload it once and keep the ID.
with open("upload_notes.txt", "rb") as f:
    uploaded = client.files.upload(file=("upload_notes.txt", f, "text/plain"))

print("file_id:", uploaded.id)

# 3. Reference the file by ID instead of re-sending its bytes.
response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=200,
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "Summarize this document in one sentence."},
            {"type": "document", "source": {"type": "file", "file_id": uploaded.id}},
        ],
    }],
)

summary = next(b.text for b in response.content if b.type == "text")
print("summary:", summary)
