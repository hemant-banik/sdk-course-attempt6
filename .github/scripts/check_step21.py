#!/usr/bin/env python3
"""Grading check for Step 21 — Bedrock/Vertex client variants.

Last step that teaches new API surface; Step 22 is the capstone.

Unlike every other checker in this course, this one does NOT run the
learner's script as a subprocess and does NOT require ICA_API_KEY — the
whole point of this step is a conceptual, text-based comparison that most
learners can complete without real AWS/GCP credentials. We only validate
the source text: both client class names must appear, and each must be
accompanied by an explanatory comment about when to use it.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _report import fail, require_exercise  # noqa: E402

EXERCISE_PATH = Path("exercises/practice21_bedrock_vertex.py")

REQUIRED_CLASSES = ["AnthropicBedrock", "AnthropicVertex"]

CLASS_HINTS = {
    "AnthropicBedrock": (
        "Add the AWS variant: 'from anthropic import AnthropicBedrock' and show "
        "constructing it (aws_region=...). Spelling is exact and case-sensitive."
    ),
    "AnthropicVertex": (
        "Add the GCP variant: 'from anthropic import AnthropicVertex' and show "
        "constructing it (project_id=..., region=...). Spelling is exact and "
        "case-sensitive."
    ),
}


def has_nearby_explanatory_comment(source: str, class_name: str) -> bool:
    """Look for a '#' comment line near (within 6 lines above) a class usage
    that contains words suggesting a "when to use this" explanation."""
    lines = source.splitlines()
    for i, line in enumerate(lines):
        if class_name in line:
            window = lines[max(0, i - 6):i + 1]
            for w_line in window:
                stripped = w_line.strip()
                if stripped.startswith("#"):
                    lower = stripped.lower()
                    if "use" in lower and ("when" in lower or "if" in lower or "want" in lower):
                        return True
    return False


def main() -> None:
    # NOTE: intentionally no ICA_API_KEY check here — this step makes no
    # live API call, unlike every other step in the course.
    source = require_exercise(EXERCISE_PATH)

    for class_name in REQUIRED_CLASSES:
        if class_name not in source:
            fail(
                f"Your script doesn't reference {class_name} — both client classes are required.",
                expected=f"{EXERCISE_PATH} source to contain '{class_name}'",
                actual_title="YOUR SCRIPT (source as the grader sees it)",
                actual=source,
                hint=CLASS_HINTS[class_name],
            )

    if "import" not in source or not re.search(r"from\s+anthropic\s+import", source):
        fail(
            "Your script doesn't import from the anthropic package (expected 'from anthropic import ...').",
            expected="source to match the regex  from\\s+anthropic\\s+import",
            actual_title="YOUR SCRIPT (source as the grader sees it)",
            actual=source,
            hint=(
                "Use the 'from anthropic import AnthropicBedrock, AnthropicVertex' form. "
                "A plain 'import anthropic' does not match what this step asks for."
            ),
        )

    for class_name in REQUIRED_CLASSES:
        if not has_nearby_explanatory_comment(source, class_name):
            fail(
                f"Couldn't find an explanatory '# ... use ... when/if/want ...' comment "
                f"near your {class_name} usage. Add a comment explaining when you'd "
                f"reach for {class_name} specifically.",
                expected=(
                    f"a '#' comment within the 6 lines above your {class_name} usage "
                    f"containing the word 'use' AND one of 'when' / 'if' / 'want'"
                ),
                actual_title="YOUR SCRIPT (source as the grader sees it)",
                actual=source,
                hint=(
                    f"Put a comment directly above the {class_name} line that says when "
                    f"to pick it, e.g. '# Use {class_name} when your workload already "
                    f"runs on that cloud.' — it must contain 'use' plus "
                    f"'when'/'if'/'want'."
                ),
            )

    print("✅ PASS: script demonstrates both client variants with clear usage comments.")
    print(f"Found classes: {', '.join(REQUIRED_CLASSES)}")


if __name__ == "__main__":
    main()
