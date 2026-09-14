#!/usr/bin/env python3
"""Grading check for Step 7 — structured / JSON output.

Runs exercises/practice7_json.py (live API call through this project's
gateway) and checks stdout shows the raw text plus successfully parsed
'name'/'age' fields with the correct Python type for age.
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

EXERCISE_PATH = Path("exercises/practice7_json.py")

REQUIRED_LABELS = ["raw:", "parsed name:", "parsed age:", "age type:"]

LABEL_HINTS = {
    "raw:": 'print("raw:", raw_text) — the unparsed string Claude returned.',
    "parsed name:": 'After json.loads(), print("parsed name:", data["name"]).',
    "parsed age:": 'After json.loads(), print("parsed age:", data["age"]).',
    "age type:": (
        'print("age type:", type(data["age"]).__name__) — that prints the bare word '
        "'int' rather than \"<class 'int'>\"."
    ),
}

SOURCE_CHECKS = CLIENT_SETUP_CHECKS + [
    (
        "json.loads(",
        "Your script doesn't call json.loads() to parse Claude's reply.",
        "Import json and parse the reply text: data = json.loads(raw_text). The API "
        "returns a string — only json.loads() turns it into a dict.",
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
            "Your script raised an error when run (often a JSON parsing error — "
            "print raw_text to debug what Claude actually returned):"
        ),
        error_hint=(
            "A JSONDecodeError means the reply wasn't pure JSON — Claude often wraps it "
            "in prose or ```json fences. Ask for 'JSON only, no other text' and/or "
            "strip the fences before json.loads()."
        ),
    )

    require_labels(stdout, REQUIRED_LABELS, LABEL_HINTS)

    if not contains(stdout, "age type: int"):
        fail(
            "Expected 'age type: int' — json.loads() should parse age as an integer. Got:",
            expected="stdout to contain the literal text 'age type: int'",
            actual=stdout,
            hint=(
                "'age type: str' means the model quoted the number (\"age\": \"30\"). "
                "Ask for age as a JSON number, or print "
                'type(data["age"]).__name__ after coercing with int().'
            ),
        )

    print("✅ PASS: JSON output requested and parsed correctly.")
    print(stdout)


if __name__ == "__main__":
    main()
