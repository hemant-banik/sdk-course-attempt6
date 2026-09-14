#!/usr/bin/env python3
"""Grading check for Step 5 — content blocks: text + image input (base64).

Runs exercises/practice5_image.py (live API call through this project's
gateway) and checks stdout shows the expected "color:" label with Claude
correctly identifying the solid-red test image.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _report import (
    CLIENT_SETUP_CHECKS,
    check_source,
    contains,
    fail,
    require_api_key,
    require_exercise,
    require_in_stdout,
    run_exercise,
)

EXERCISE_PATH = Path("exercises/practice5_image.py")

SOURCE_CHECKS = CLIENT_SETUP_CHECKS + [
    (
        '"type": "image"',
        "Your script doesn't include an image content block ('type': 'image').",
        'Content must be a list of blocks, one of them {"type": "image", "source": '
        '{"type": "base64", "media_type": "image/png", "data": b64}} — the grader '
        'looks for the exact text \'"type": "image"\' (double quotes, one space).',
    ),
    (
        "base64",
        "Your script doesn't appear to base64-encode the image data.",
        "Import base64 and encode the bytes: "
        'base64.standard_b64encode(img_bytes).decode("utf-8") — the API needs a '
        "string, not raw bytes.",
    ),
]


def main() -> None:
    require_api_key()
    source = require_exercise(EXERCISE_PATH)
    check_source(source, SOURCE_CHECKS)

    stdout = run_exercise(
        EXERCISE_PATH,
        timeout=60,
        error_hint=(
            "Check the last line of the stderr traceback. A 400 'could not process "
            "image' means the base64 string or media_type is wrong; FileNotFoundError "
            "means the image path doesn't resolve from the repo root."
        ),
    )

    require_in_stdout(
        stdout,
        "color:",
        "Expected a line starting with 'color:' in stdout.",
        expected="stdout to contain the literal text 'color:'",
        hint=(
            'Print the answer with the exact lowercase label, e.g. '
            'print("color:", response.content[0].text).'
        ),
    )
    if not contains(stdout, "red"):
        fail(
            "Expected the reply to mention 'red'. Got stdout:",
            expected="stdout to contain 'red' (case-insensitive)",
            actual=stdout,
            hint=(
                "The test image is solid red, so Claude should say 'red'. If it "
                "describes something else the image bytes probably never reached the "
                "API — verify you sent the base64 of the actual PNG file."
            ),
        )

    print("✅ PASS: Claude correctly identified the base64-encoded image.")
    print(stdout)


if __name__ == "__main__":
    main()
