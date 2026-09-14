#!/usr/bin/env python3
"""Grading check for Step 19 — code execution tool (server-side sandbox).

Runs exercises/practice19_code_execution.py (live API call through this
project's gateway) using the code_execution_20250825 server tool, and
checks stdout has the labeled answer line with the correct computed mean.
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

EXERCISE_PATH = Path("exercises/practice19_code_execution.py")

TOOL_TYPE = "code_execution_20250825"

SOURCE_CHECKS = CLIENT_SETUP_CHECKS + [
    (
        TOOL_TYPE,
        f"Your script doesn't use tool type '{TOOL_TYPE}' — that's the exact server tool string required.",
        f'The tool type is version-dated and must match exactly: {{"type": '
        f'"{TOOL_TYPE}", "name": "code_execution"}}. A different date string is rejected.',
    ),
    (
        "code_execution",
        "Your script doesn't reference the code_execution tool name.",
        'Set "name": "code_execution" on the tool entry, alongside the dated type '
        "string.",
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
            "Check the last line of the stderr traceback. Server tools need the "
            "anthropic-beta header (see the step doc); a 400 'unsupported tool' means "
            "the type string or beta flag is off."
        ),
    )

    require_in_stdout(
        stdout,
        "answer:",
        "Expected a line starting with 'answer:' in stdout.",
        expected="stdout to contain the literal text 'answer:'",
        hint=(
            'Print the final text with the exact lowercase label, e.g. '
            'print("answer:", final_text) — collect the text blocks after the tool runs.'
        ),
    )
    if not contains(stdout, "5.5"):
        fail(
            "Expected the correct mean (5.5) to appear in the answer. Got:",
            expected="stdout to contain the literal text '5.5' (the computed mean)",
            actual=stdout,
            hint=(
                "The mean of 1..10 is 5.5. If it's missing, Claude likely answered "
                "without running code — print every block's .type to confirm a "
                "'code_execution_tool_result' block actually came back."
            ),
        )

    print("✅ PASS: code execution tool ran and returned the correct mean.")
    print(stdout)


if __name__ == "__main__":
    main()
