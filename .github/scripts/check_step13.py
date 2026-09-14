#!/usr/bin/env python3
"""Grading check for Step 13 — count tokens with client.messages.count_tokens().

Runs exercises/practice13_token_counting.py (live API call through this
project's gateway) and checks stdout has both expected labeled lines, that
the long message counted more tokens than the short one, and that the
client setup still uses this project's real pattern (load_dotenv +
ICA_API_KEY + base_url).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _report import (
    CLIENT_SETUP_CHECKS,
    check_source,
    fail,
    require_api_key,
    require_exercise,
    require_labels,
    run_exercise,
    search_value,
)

EXERCISE_PATH = Path("exercises/practice13_token_counting.py")

REQUIRED_LABELS = ["short_tokens:", "long_tokens:"]

LABEL_HINTS = {
    "short_tokens:": (
        "Count the short message and print it with the exact snake_case label, e.g. "
        'print("short_tokens:", client.messages.count_tokens(...).input_tokens).'
    ),
    "long_tokens:": (
        "Do the same for the long message: "
        'print("long_tokens:", client.messages.count_tokens(...).input_tokens).'
    ),
}

SOURCE_CHECKS = CLIENT_SETUP_CHECKS + [
    (
        "count_tokens",
        "Your script doesn't call count_tokens() — that's the whole point of this step!",
        "Use client.messages.count_tokens(model=..., messages=[...]) and read "
        ".input_tokens off the result — don't estimate by len(text.split()).",
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
            "Check the last line of the stderr traceback. count_tokens() needs both "
            "model= and messages=; it returns an object, so read .input_tokens rather "
            "than printing it directly."
        ),
    )

    require_labels(stdout, REQUIRED_LABELS, LABEL_HINTS)

    short_match = search_value(stdout, "short_tokens:")
    long_match = search_value(stdout, "long_tokens:")
    if not short_match or not long_match:
        fail(
            "Couldn't parse integer token counts out of stdout:",
            expected=(
                "lines matching  short_tokens:\\s*(\\d+)  and  long_tokens:\\s*(\\d+)"
            ),
            actual=stdout,
            hint=(
                "Print the bare integer after the label — printing the whole "
                "MessageTokensCount object gives 'input_tokens=12' style text that the "
                "grader can't parse. Use .input_tokens."
            ),
        )

    short_tokens = int(short_match.group(1))
    long_tokens = int(long_match.group(1))
    if long_tokens <= short_tokens:
        fail(
            f"Expected long_tokens ({long_tokens}) to be greater than "
            f"short_tokens ({short_tokens}) — the long message should count more tokens.",
            expected=f"long_tokens > short_tokens (got {long_tokens} <= {short_tokens})",
            actual=stdout,
            hint=(
                "The two labels look swapped, or both counted the same message. Pass "
                "the short text to the first count_tokens() call and the long text to "
                "the second."
            ),
        )

    print("✅ PASS: token counting works correctly.")
    print(stdout)


if __name__ == "__main__":
    main()
