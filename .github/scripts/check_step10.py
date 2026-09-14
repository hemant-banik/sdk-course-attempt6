#!/usr/bin/env python3
"""Grading check for Step 10 — vision with multiple images.

Runs exercises/practice10_vision.py (live API call through this project's
gateway) and checks stdout shows the "answer:" label with Claude correctly
distinguishing the red first image from the blue second image.
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

EXERCISE_PATH = Path("exercises/practice10_vision.py")

SOURCE_CHECKS = CLIENT_SETUP_CHECKS + [
    (
        # Two image blocks in ONE message — a count check, so use a callable.
        lambda src: src.count('"type": "image"') >= 2,
        "Your script needs at least two image content blocks in the same message.",
        'Put both images in one user message\'s content list: [{"type": "image", ...}, '
        '{"type": "image", ...}, {"type": "text", "text": "..."}]. The grader counts '
        'occurrences of the exact text \'"type": "image"\', so it must appear twice.',
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
            "Check the last line of the stderr traceback. FileNotFoundError means an "
            "image path doesn't resolve from the repo root; a 400 'could not process "
            "image' means one of the base64 strings is malformed."
        ),
    )

    require_in_stdout(
        stdout,
        "answer:",
        "Expected a line starting with 'answer:' in stdout.",
        expected="stdout to contain the literal text 'answer:'",
        hint=(
            'Print the reply with the exact lowercase label, e.g. '
            'print("answer:", response.content[0].text).'
        ),
    )

    if not contains(stdout, "red"):
        fail(
            "Expected the reply to mention 'red' for the first image. Got stdout:",
            expected="stdout to contain 'red' (case-insensitive)",
            actual=stdout,
            hint=(
                "The first test image is solid red. If Claude never says 'red', the "
                "first image block probably didn't carry real base64 data — verify you "
                "encoded the correct file."
            ),
        )
    if not contains(stdout, "blue"):
        fail(
            "Expected the reply to mention 'blue' for the second image. Got stdout:",
            expected="stdout to contain 'blue' (case-insensitive)",
            actual=stdout,
            hint=(
                "The second test image is solid blue. Mentioning only red usually means "
                "you sent the same image twice — check you encoded two different files."
            ),
        )

    print("✅ PASS: Claude correctly compared two images in one request.")
    print(stdout)


if __name__ == "__main__":
    main()
