#!/usr/bin/env python3
"""Grading check for Step 8 — tool use (single round-trip).

Runs exercises/practice8_tools.py (live API calls through this project's
gateway) and checks stdout shows Claude requesting the get_weather tool,
then producing a final answer after the tool_result is sent back.
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

EXERCISE_PATH = Path("exercises/practice8_tools.py")

REQUIRED_LABELS = ["stop_reason:", "tool name:", "tool input:", "final answer:"]

LABEL_HINTS = {
    "stop_reason:": (
        'print("stop_reason:", response.stop_reason) after the first create() call '
        "— it should read 'tool_use'."
    ),
    "tool name:": (
        "Find the tool_use block in response.content and print its .name, e.g. "
        'print("tool name:", block.name).'
    ),
    "tool input:": (
        'Print the arguments Claude chose: print("tool input:", block.input) — '
        "a dict like {'location': 'Paris'}."
    ),
    "final answer:": (
        "After sending the tool_result back, print the second reply: "
        'print("final answer:", response2.content[0].text).'
    ),
}

SOURCE_CHECKS = CLIENT_SETUP_CHECKS + [
    (
        "tool_use_id",
        "Your script doesn't send back a tool_result with tool_use_id — that's required to complete the round-trip.",
        "Your tool_result block must echo the id from Claude's tool_use block: "
        '{"type": "tool_result", "tool_use_id": block.id, "content": "..."} — '
        "without the matching id the API can't pair result to request.",
    ),
    (
        "input_schema",
        "Your script doesn't define a tool with an input_schema.",
        "Each tool needs an input_schema: a JSON Schema dict like "
        '{"type": "object", "properties": {"location": {"type": "string"}}, '
        '"required": ["location"]}.',
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
            "Check the last line of the stderr traceback. A 400 about tool_result "
            "usually means the tool_use_id doesn't match, or the assistant's tool_use "
            "message wasn't appended to messages before the tool_result."
        ),
    )

    require_labels(stdout, REQUIRED_LABELS, LABEL_HINTS)

    if not contains(stdout, "stop_reason: tool_use"):
        fail(
            "Expected 'stop_reason: tool_use' — Claude should decide to call the tool. Got:",
            expected="stdout to contain the literal text 'stop_reason: tool_use'",
            actual=stdout,
            hint=(
                "'stop_reason: end_turn' means Claude answered directly instead of "
                "calling the tool. Confirm you passed tools=[...] and that the "
                "question actually needs the tool (e.g. asks about the weather)."
            ),
        )

    if not contains(stdout, "get_weather"):
        fail(
            "Expected the tool name 'get_weather' to appear in stdout. Got:",
            expected="stdout to contain the literal text 'get_weather'",
            actual=stdout,
            hint=(
                'Name the tool exactly "get_weather" in your tool definition, and '
                "print the name from the tool_use block rather than hardcoding it."
            ),
        )

    print("✅ PASS: tool use round-trip handled correctly.")
    print(stdout)


if __name__ == "__main__":
    main()
