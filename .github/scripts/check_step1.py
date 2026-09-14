#!/usr/bin/env python3
"""Grading check for Step 1 — Install SDK & create a client.

Runs the learner's exercises/practice1.py and verifies stdout contains the
two expected lines. Exits 0 on pass, 1 on fail (with a human-readable
reason printed to stdout so it shows up in the Actions log and, if needed,
in the issue comment).
"""
import sys
from pathlib import Path

# Workflows run this from the repo root, so the script dir isn't on sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _report import (  # noqa: E402
    CLIENT_SETUP_CHECKS,
    check_source,
    fail,
    require_exercise,
    require_in_stdout,
    run_exercise,
)

EXERCISE_PATH = Path("exercises/practice1.py")


def main() -> None:
    source = require_exercise(EXERCISE_PATH)
    check_source(source, CLIENT_SETUP_CHECKS)

    stdout = run_exercise(
        EXERCISE_PATH,
        timeout=60,
        error_hint=(
            "Read the stderr traceback above — its last line names the real problem. "
            "ModuleNotFoundError means 'pip install anthropic python-dotenv' hasn't "
            "run; a TypeError on Anthropic(...) usually means a misspelled keyword."
        ),
    )

    require_in_stdout(
        stdout,
        "SDK version:",
        "Expected a line starting with 'SDK version:' in stdout.",
        expected="stdout to contain the literal text 'SDK version:'",
        hint=(
            'Print the installed version with the exact label, e.g. '
            'print("SDK version:", anthropic.__version__) — note the capital "SDK" '
            "and the colon."
        ),
    )
    require_in_stdout(
        stdout,
        "Client type: Anthropic",
        "Expected a line 'Client type: Anthropic' in stdout.",
        expected="stdout to contain the literal text 'Client type: Anthropic'",
        hint=(
            'Print the class name, e.g. print("Client type:", type(client).__name__) '
            "— that yields 'Anthropic'. Printing the object itself gives "
            "'<anthropic.Anthropic object at 0x...>', which does not match."
        ),
    )

    print("✅ PASS: SDK installed and client created correctly.")
    print(stdout)


if __name__ == "__main__":
    main()
