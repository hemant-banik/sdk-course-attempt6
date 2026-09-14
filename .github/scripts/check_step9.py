#!/usr/bin/env python3
"""Grading check for Step 9 — extended thinking.

Runs exercises/practice9_thinking.py (live API call through this project's
gateway) and checks stdout shows a nonempty thinking block plus the correct
final answer (918 = 27 * 34).
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
    search_value,
)

EXERCISE_PATH = Path("exercises/practice9_thinking.py")

REQUIRED_LABELS = ["has thinking block:", "thinking length:", "answer:"]

LABEL_HINTS = {
    "has thinking block:": (
        "Check the block types in response.content, e.g. "
        'print("has thinking block:", any(b.type == "thinking" for b in '
        "response.content)) — it must print the word True."
    ),
    "thinking length:": (
        "Find the thinking block and print the length of its .thinking text, e.g. "
        'print("thinking length:", len(block.thinking)).'
    ),
    "answer:": (
        "The final text is in a *separate* block from the thinking. Print the text "
        'block: print("answer:", text_block.text).'
    ),
}

SOURCE_CHECKS = CLIENT_SETUP_CHECKS + [
    (
        ('"thinking"', "'thinking'"),
        "Your script doesn't pass thinking={'type': 'enabled', ...} to enable extended thinking.",
        'Add thinking={"type": "enabled", "budget_tokens": 2000} to your '
        "messages.create() call — extended thinking is off unless you ask for it.",
    ),
    (
        "budget_tokens",
        "Your script doesn't set budget_tokens — required by the thinking parameter.",
        "The thinking dict needs budget_tokens, e.g. "
        '{"type": "enabled", "budget_tokens": 2000}. It must be less than '
        "max_tokens.",
    ),
]


def main() -> None:
    require_api_key()
    source = require_exercise(EXERCISE_PATH)
    check_source(source, SOURCE_CHECKS)

    stdout = run_exercise(
        EXERCISE_PATH,
        timeout=90,
        error_hint=(
            "Check the last line of the stderr traceback. AttributeError on .text "
            "usually means you read content[0] — with thinking on, content[0] is the "
            "thinking block, so find the text block by its .type instead."
        ),
    )

    require_labels(stdout, REQUIRED_LABELS, LABEL_HINTS)

    if not contains(stdout, "has thinking block: True"):
        fail(
            "Expected 'has thinking block: True'. Got stdout:",
            expected="stdout to contain the literal text 'has thinking block: True'",
            actual=stdout,
            hint=(
                "Printing False means no block had type == 'thinking'. Verify the "
                "thinking parameter was actually passed and that you compare "
                'block.type to the string "thinking".'
            ),
        )

    match = search_value(stdout, "thinking length:")
    if not match or int(match.group(1)) <= 0:
        fail(
            "Expected 'thinking length:' to be greater than 0. Got stdout:",
            expected="a line matching  thinking length:\\s*(\\d+)  with a value > 0",
            actual=stdout,
            hint=(
                "Print len() of the thinking block's .thinking attribute (not .text, "
                "which is empty on a thinking block) — a 0 means you measured the "
                "wrong field."
            ),
        )

    if not contains(stdout, "918"):
        fail(
            "Expected the answer to contain '918' (27 * 34). Got stdout:",
            expected="stdout to contain the literal text '918'",
            actual=stdout,
            hint=(
                "Make sure you print the final *text* block, not the thinking block — "
                "the answer 918 appears in the text block. Also confirm the prompt "
                "asks for 27 * 34."
            ),
        )

    print("✅ PASS: extended thinking enabled and both block types read correctly.")
    print(stdout)


if __name__ == "__main__":
    main()
