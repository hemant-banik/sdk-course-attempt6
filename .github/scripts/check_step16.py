#!/usr/bin/env python3
"""Grading check for Step 16 — error handling with APIStatusError.

Runs exercises/practice16_error_handling.py (live API call through this
project's gateway using a deliberately invalid model name) and checks
stdout has the labeled error_type/error_message output, proving the
exception was caught rather than crashing the script.
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
    require_labels,
    run_exercise,
)

EXERCISE_PATH = Path("exercises/practice16_error_handling.py")

REQUIRED_LABELS = ["error_type:", "error_message:"]

LABEL_HINTS = {
    "error_type:": (
        "Inside the except block print the exception class name, e.g. "
        'print("error_type:", type(exc).__name__).'
    ),
    "error_message:": (
        'Also print the message: print("error_message:", str(exc)) — both labels are '
        "required so the grader can see the error was handled."
    ),
}

SOURCE_CHECKS = CLIENT_SETUP_CHECKS + [
    (
        # Original grader required both markers together.
        lambda src: "except" in src and "anthropic." in src,
        "Your script doesn't appear to catch an anthropic exception type.",
        "Wrap the call in try/except and catch the SDK's own class, e.g. "
        "'except anthropic.APIStatusError as exc:' — a bare 'except Exception' won't "
        "show you the status code.",
    ),
]


def main() -> None:
    require_api_key()
    source = require_exercise(EXERCISE_PATH)
    check_source(source, SOURCE_CHECKS)

    stdout = run_exercise(
        EXERCISE_PATH,
        timeout=60,
        error_msg=(
            "Your script raised an uncaught error when run (the exception "
            "should have been caught, not crash the script):"
        ),
        error_hint=(
            "The error escaped your try/except. Either the create() call sits outside "
            "the try block, or you're catching the wrong class — an invalid model name "
            "raises anthropic.NotFoundError, a subclass of anthropic.APIStatusError."
        ),
    )

    if contains(stdout, "No error was raised"):
        fail(
            "The API call succeeded instead of failing — use an invalid model name so an error is actually raised.",
            expected=(
                "the API call to FAIL and be caught, so stdout must NOT contain "
                "'No error was raised'"
            ),
            actual=stdout,
            hint=(
                'Use a model string that cannot exist, e.g. model="claude-does-not-'
                'exist-99" — a real model name succeeds and there is no error to catch.'
            ),
        )

    require_labels(stdout, REQUIRED_LABELS, LABEL_HINTS)

    print("✅ PASS: error was deliberately triggered and caught correctly.")
    print(stdout)


if __name__ == "__main__":
    main()
