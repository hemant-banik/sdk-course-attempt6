#!/usr/bin/env python3
"""Grading check for Step 18 — Files API upload + reference by file_id.

Runs exercises/practice18_files_api.py (live API call through this
project's gateway) and checks stdout has both expected labeled lines: a
real file_id and a non-empty summary referencing the uploaded content.
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

EXERCISE_PATH = Path("exercises/practice18_files_api.py")

REQUIRED_LABELS = ["file_id:", "summary:"]

LABEL_HINTS = {
    "file_id:": (
        "Print the id returned by the upload, e.g. "
        'print("file_id:", uploaded.id) — it starts with \'file_\'.'
    ),
    "summary:": (
        'Print Claude\'s reply about the uploaded file: '
        'print("summary:", response.content[0].text).'
    ),
}

SOURCE_CHECKS = CLIENT_SETUP_CHECKS + [
    (
        "files.upload",
        "Your script doesn't call client.files.upload() — that's the whole point of this step!",
        "Upload the file first with client.files.upload(file=(name, handle, mime)) and "
        "keep the returned object — you need its .id for the document block.",
    ),
    (
        "file_id",
        "Your script doesn't reference file_id in a document content block.",
        'Reference the upload instead of inlining base64: {"type": "document", '
        '"source": {"type": "file", "file_id": uploaded.id}}.',
    ),
]


def main() -> None:
    require_api_key()
    source = require_exercise(EXERCISE_PATH)
    check_source(source, SOURCE_CHECKS)

    stdout = run_exercise(
        EXERCISE_PATH,
        timeout=60,
        error_msg=(
            "Your script raised an error when run (see the step's troubleshooting "
            "note if this is a gateway Files API limitation):"
        ),
        error_hint=(
            "Check the last line of the stderr traceback. A 404 on /v1/files usually "
            "means this gateway doesn't expose the Files API — see the step's "
            "troubleshooting note. Files API also needs the anthropic-beta header."
        ),
    )

    require_labels(stdout, REQUIRED_LABELS, LABEL_HINTS)

    # contains() already tolerates the missing/extra space after the colon.
    if not contains(stdout, "file_id: file_"):
        fail(
            "Expected file_id to start with 'file_'. Got stdout:",
            expected="stdout to contain 'file_id: file_' (the real uploaded file id)",
            actual=stdout,
            hint=(
                "Print the .id of the upload result, not the local filename or the whole "
                "object. Real Files API ids always begin with the 'file_' prefix."
            ),
        )

    print("✅ PASS: file uploaded and referenced by file_id successfully.")
    print(stdout)


if __name__ == "__main__":
    main()
