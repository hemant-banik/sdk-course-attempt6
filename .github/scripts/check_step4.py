#!/usr/bin/env python3
"""Grading check for Step 4 — message roles & multi-turn conversation.

Runs exercises/practice4_multiturn.py (live API calls through this project's
gateway) and checks stdout shows Claude remembering the name from turn 1
when asked about it in turn 2, plus the expected "Messages in list:" count.
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

EXERCISE_PATH = Path("exercises/practice4_multiturn.py")

REQUIRED_LABELS = ["Turn 1:", "Turn 2:", "Messages in list:"]

LABEL_HINTS = {
    "Turn 1:": (
        'Print the first reply with the exact label, e.g. '
        'print("Turn 1:", response1.content[0].text).'
    ),
    "Turn 2:": (
        "Did you print the second response? Check you appended the assistant turn "
        "before the second create() call, then "
        'print("Turn 2:", response2.content[0].text).'
    ),
    "Messages in list:": (
        'After both turns, print the history length: '
        'print("Messages in list:", len(messages)).'
    ),
}

SOURCE_CHECKS = CLIENT_SETUP_CHECKS + [
    (
        ".append(",
        "Your script doesn't call .append() on the messages list — multi-turn requires resending history.",
        "Multi-turn is manual: after each reply do "
        'messages.append({"role": "assistant", "content": reply_text}) and then '
        "append the next user message before calling create() again.",
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
            "Check the last line of the stderr traceback. A 400 'messages' error here "
            "usually means roles are out of order — they must alternate "
            "user/assistant/user/assistant."
        ),
    )

    require_labels(stdout, REQUIRED_LABELS, LABEL_HINTS)

    if not contains(stdout, "zara"):
        fail(
            "Expected Turn 2's reply to mention the name 'Zara'. Got stdout:",
            expected="stdout to contain 'Zara' (case-insensitive) in Turn 2's reply",
            actual=stdout,
            hint=(
                "Claude only remembers the name if you resend the history. Append the "
                "turn-1 assistant reply to messages before the second create() call — "
                "otherwise turn 2 starts from scratch and cannot know the name."
            ),
        )

    if not contains(stdout, "Messages in list: 4"):
        fail(
            "Expected 'Messages in list: 4' (2 user + 2 assistant turns). Got stdout:",
            expected="stdout to contain the literal text 'Messages in list: 4'",
            actual=stdout,
            hint=(
                "After two full turns the list holds 4 entries: user, assistant, user, "
                "assistant. If you got 2 or 3 you skipped appending one of the "
                "assistant replies; print len(messages) at the very end."
            ),
        )

    print("✅ PASS: multi-turn conversation correctly remembered context across turns.")
    print(stdout)


if __name__ == "__main__":
    main()
