#!/usr/bin/env python3
"""Grading check for Step 6 — streaming responses.

Runs exercises/practice6_streaming.py (live API call through this project's
gateway, streamed) and checks stdout has the "streaming:", "stop_reason:",
and "chars streamed:" labels, with a nonzero character count.
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

EXERCISE_PATH = Path("exercises/practice6_streaming.py")

REQUIRED_LABELS = ["streaming:", "stop_reason:", "chars streamed:"]

LABEL_HINTS = {
    "streaming:": (
        'Print the lowercase label before you start consuming the stream, e.g. '
        'print("streaming:", ...).'
    ),
    "stop_reason:": (
        "Get the finished message after the with-block: "
        'final = stream.get_final_message(), then print("stop_reason:", '
        "final.stop_reason)."
    ),
    "chars streamed:": (
        "Accumulate the text as you iterate, then "
        'print("chars streamed:", len(collected)).'
    ),
}

SOURCE_CHECKS = CLIENT_SETUP_CHECKS + [
    (
        "messages.stream(",
        "Your script doesn't call client.messages.stream() — use the streaming method, not .create().",
        "Use 'with client.messages.stream(...) as stream:' — .create() returns the "
        "whole reply at once and cannot stream.",
    ),
    (
        "text_stream",
        "Your script doesn't iterate stream.text_stream.",
        "Iterate the text deltas with 'for chunk in stream.text_stream:' — that is the "
        "convenience iterator that yields plain strings.",
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
            "Check the last line of the stderr traceback. Calling "
            "get_final_message() outside the 'with' block, or forgetting 'with' "
            "entirely, is the usual cause here."
        ),
    )

    require_labels(stdout, REQUIRED_LABELS, LABEL_HINTS)

    match = search_value(stdout, "chars streamed:")
    if not match or int(match.group(1)) <= 0:
        fail(
            "Expected 'chars streamed:' to be greater than 0. Got stdout:",
            expected="a line matching  chars streamed:\\s*(\\d+)  with a value > 0",
            actual=stdout,
            hint=(
                "Build up the text while streaming, e.g. collected = \"\" then "
                "collected += chunk inside the loop — a count of 0 means you printed "
                "the chunks but never accumulated them."
            ),
        )

    if not contains(stdout, "stop_reason: end_turn"):
        fail(
            "Expected 'stop_reason: end_turn' in stdout. Got:",
            expected="stdout to contain the literal text 'stop_reason: end_turn'",
            actual=stdout,
            hint=(
                "'stop_reason: max_tokens' means the reply was cut off — raise "
                "max_tokens so the model finishes naturally and reports 'end_turn'."
            ),
        )

    print("✅ PASS: streaming response handled correctly.")
    print(stdout)


if __name__ == "__main__":
    main()
