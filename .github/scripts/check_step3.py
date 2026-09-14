#!/usr/bin/env python3
"""Grading check for Step 3 — inspect the full response object.

Runs exercises/practice_inspect.py (live API call through this project's
gateway) and checks stdout has all six expected labeled lines, that the
id/role/stop_reason values look right, and that the client setup still uses
this project's real pattern (load_dotenv + ICA_API_KEY + base_url).
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

EXERCISE_PATH = Path("exercises/practice_inspect.py")

REQUIRED_LABELS = ["id:", "model:", "role:", "stop_reason:", "usage:", "text:"]

LABEL_HINTS = {
    "id:": 'print("id:", response.id) — the message id, e.g. msg_01ABC...',
    "model:": 'print("model:", response.model) — the model that actually served the request.',
    "role:": 'print("role:", response.role) — always "assistant" on a reply.',
    "stop_reason:": 'print("stop_reason:", response.stop_reason) — e.g. "end_turn".',
    "usage:": 'print("usage:", response.usage) — the input/output token counts.',
    "text:": 'print("text:", response.content[0].text) — the actual reply text.',
}


def main() -> None:
    require_api_key()
    source = require_exercise(EXERCISE_PATH)
    check_source(source, CLIENT_SETUP_CHECKS)

    stdout = run_exercise(
        EXERCISE_PATH,
        timeout=60,
        error_hint=(
            "Check the last line of the stderr traceback. AttributeError here usually "
            "means you used a wrong field name — the response has .id, .model, .role, "
            ".stop_reason, .usage and .content."
        ),
    )

    require_labels(stdout, REQUIRED_LABELS, LABEL_HINTS)

    if not contains(stdout, "id: msg_"):
        fail(
            "Expected the printed 'id:' to start with 'msg_'.",
            expected="a line matching the regex  id:\\s*msg_  (e.g. 'id: msg_01AbC...')",
            actual=stdout,
            hint=(
                "Print response.id itself, not the whole response or a nested field. "
                "Real message ids always begin with the 'msg_' prefix."
            ),
        )
    if not contains(stdout, "role: assistant"):
        fail(
            "Expected 'role: assistant' in stdout.",
            expected="stdout to contain the literal text 'role: assistant'",
            actual=stdout,
            hint=(
                'Use print("role:", response.role) — that is the reply\'s role and it '
                'is always "assistant". Printing the role you *sent* gives "user".'
            ),
        )

    print("✅ PASS: response object inspected correctly.")
    print(stdout)


if __name__ == "__main__":
    main()
