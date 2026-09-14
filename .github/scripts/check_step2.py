#!/usr/bin/env python3
"""Grading check for Step 2 — first messages.create() call.

Runs exercises/practice_message.py for real (this step DOES call the live
Anthropic API through this project's gateway, so ICA_API_KEY must be set)
and checks the reply contains "4" (the answer to "What is 2 + 2?").
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
    run_exercise,
)

EXERCISE_PATH = Path("exercises/practice_message.py")

CREATE_PARAM_HINTS = {
    "model=": 'Pass the model explicitly, e.g. model="claude-sonnet-4-5-20250929".',
    "max_tokens=": "max_tokens= is required by the Messages API — add e.g. max_tokens=1024.",
    "messages=": 'Pass messages=[{"role": "user", "content": "What is 2 + 2?"}].',
}


def main() -> None:
    require_api_key()
    source = require_exercise(EXERCISE_PATH)

    for required in ("model=", "max_tokens=", "messages="):
        if required not in source:
            fail(
                f"Your call to messages.create() is missing the '{required}' parameter.",
                expected=f"{EXERCISE_PATH} source to contain '{required}'",
                actual_title="YOUR SCRIPT (source as the grader sees it)",
                actual=source,
                hint=CREATE_PARAM_HINTS[required],
            )

    check_source(source, CLIENT_SETUP_CHECKS)

    stdout = run_exercise(
        EXERCISE_PATH,
        timeout=60,
        error_hint=(
            "Check the last line of the stderr traceback. A 401 means ICA_API_KEY is "
            "wrong or unset; a 404 usually means base_url is wrong; a TypeError means "
            "a create() keyword is misspelled."
        ),
    )

    if not contains(stdout, "4"):
        fail(
            f"Expected the reply to mention '4'. Got stdout:",
            expected="stdout to contain the character '4' (Claude's answer to 2 + 2)",
            actual=stdout,
            hint=(
                "Print the reply text, not the response object: "
                "print(response.content[0].text). If stdout is empty you probably "
                "assigned the result without printing it."
            ),
        )

    print("✅ PASS: messages.create() call succeeded and returned the right answer.")
    print(stdout)


if __name__ == "__main__":
    main()
