#!/usr/bin/env python3
"""Grading check for Step 11 — PDF support (document content block).

Runs exercises/practice11_pdf.py (live API call through this project's
gateway) and checks stdout shows the PDF was created and Claude correctly
read the secret code (4471) straight out of the PDF text.
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

EXERCISE_PATH = Path("exercises/practice11_pdf.py")

SOURCE_CHECKS = CLIENT_SETUP_CHECKS + [
    (
        '"type": "document"',
        "Your script doesn't include a document content block ('type': 'document').",
        'PDFs use a document block, not an image block: {"type": "document", '
        '"source": {"type": "base64", "media_type": "application/pdf", "data": b64}}. '
        'The grader looks for the exact text \'"type": "document"\'.',
    ),
    (
        "application/pdf",
        "Your script doesn't set media_type to 'application/pdf'.",
        'Inside the document source set "media_type": "application/pdf" — using '
        "image/png here makes the API reject the block.",
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
            "Check the last line of the stderr traceback. "
            "ModuleNotFoundError: reportlab means 'pip install -r requirements.txt' "
            "hasn't run; a 400 here usually means the base64 isn't a valid PDF."
        ),
    )

    require_in_stdout(
        stdout,
        "pdf created: True",
        "Expected 'pdf created: True' in stdout.",
        expected="stdout to contain the literal text 'pdf created: True'",
        hint=(
            "Generate the PDF first, then confirm it exists on disk, e.g. "
            'print("pdf created:", Path("report.pdf").exists()) — it must print True '
            "before the API call."
        ),
    )
    require_in_stdout(
        stdout,
        "answer:",
        "Expected a line starting with 'answer:' in stdout.",
        expected="stdout to contain the literal text 'answer:'",
        hint=(
            'Print Claude\'s reply with the exact lowercase label, e.g. '
            'print("answer:", response.content[0].text).'
        ),
    )
    if not contains(stdout, "4471"):
        fail(
            "Expected the answer to contain the secret code '4471'. Got stdout:",
            expected="stdout to contain the literal text '4471'",
            actual=stdout,
            hint=(
                "4471 is written inside the generated PDF, so Claude can only report it "
                "if the document block really reached the API. Re-read the PDF bytes "
                "after writing them and confirm you base64-encoded that same file."
            ),
        )

    print("✅ PASS: Claude correctly read the contents of the base64-encoded PDF.")
    print(stdout)


if __name__ == "__main__":
    main()
