#!/usr/bin/env python3
"""Grading check for Step 17 — compare model + stop_reason across models.

Runs exercises/practice17_models_available.py (live API calls through this
project's gateway to at least 2 different model strings) and checks stdout
labels the model name and stop_reason for each call.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _report import (
    CLIENT_SETUP_CHECKS,
    check_source,
    fail,
    find_values,
    require_api_key,
    require_exercise,
    run_exercise,
)

EXERCISE_PATH = Path("exercises/practice17_models_available.py")


def main() -> None:
    require_api_key()
    source = require_exercise(EXERCISE_PATH)
    check_source(source, CLIENT_SETUP_CHECKS)

    stdout = run_exercise(
        EXERCISE_PATH,
        timeout=90,
        error_hint=(
            "Check the last line of the stderr traceback. A 404 on one model means that "
            "model string isn't available through this gateway — try another from the "
            "step's list."
        ),
    )

    model_matches = find_values(stdout, "model:")
    stop_reason_matches = find_values(stdout, "stop_reason:")

    if len(model_matches) < 2:
        fail(
            "Expected at least 2 lines starting with 'model:' (one per model "
            f"tested). Got {len(model_matches)} in stdout:",
            expected="at least 2 lines matching  model:\\s*(\\S+)  — one per model tested",
            actual=stdout,
            hint=(
                "Loop over a list of 2-3 model strings and print "
                'print("model:", response.model) on every iteration — printing it once '
                "after the loop only yields one line."
            ),
        )
    if len(stop_reason_matches) < 2:
        fail(
            "Expected at least 2 lines starting with 'stop_reason:' (one per "
            f"model tested). Got {len(stop_reason_matches)} in stdout:",
            expected=(
                "at least 2 lines matching  stop_reason:\\s*(\\S+)  — one per model tested"
            ),
            actual=stdout,
            hint=(
                'Print print("stop_reason:", response.stop_reason) inside the same loop, '
                "right next to the model line, so each model contributes both lines."
            ),
        )
    if len(set(model_matches)) < 2:
        fail(
            f"Expected at least 2 DIFFERENT model names printed, got: {model_matches}. "
            "Use 2-3 different model= strings.",
            expected="at least 2 DISTINCT values printed after 'model:'",
            actual=stdout,
            hint=(
                "The same model name was printed every time — make sure the loop passes "
                "the current model into create(model=...) instead of a hard-coded "
                "constant."
            ),
        )

    print("✅ PASS: compared model + stop_reason across multiple models.")
    print(stdout)


if __name__ == "__main__":
    main()
