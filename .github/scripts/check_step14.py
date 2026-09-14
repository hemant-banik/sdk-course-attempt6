#!/usr/bin/env python3
"""Grading check for Step 14 — Batch API (create, poll, retrieve results).

Runs exercises/practice14_batch_api.py (live API calls through this
project's gateway) and checks stdout has the expected labeled lines,
including a final tally showing both requests succeeded. Batches are
async server-side, so this checker allows extra time for polling.
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

EXERCISE_PATH = Path("exercises/practice14_batch_api.py")

REQUIRED_LABELS = ["batch_id:", "initial_status:", "succeeded:", "errored:"]

# Batches usually finish in minutes, but give CI plenty of headroom.
TIMEOUT_SECONDS = 600

LABEL_HINTS = {
    "batch_id:": (
        'Print the id returned by create(), e.g. print("batch_id:", batch.id) — '
        "it starts with 'msgbatch_'."
    ),
    "initial_status:": (
        'Print the status right after creating the batch, e.g. '
        'print("initial_status:", batch.processing_status).'
    ),
    "succeeded:": (
        "After polling completes, count results whose result.type == 'succeeded' and "
        'print("succeeded:", n).'
    ),
    "errored:": (
        "Count results whose result.type == 'errored' and print(\"errored:\", n) — "
        "print it even when the count is 0."
    ),
}

SOURCE_CHECKS = CLIENT_SETUP_CHECKS + [
    (
        "batches.create",
        "Your script doesn't call messages.batches.create() — that's the whole point of this step!",
        "Submit the batch with client.messages.batches.create(requests=[...]), where "
        "each entry has a custom_id and a params dict.",
    ),
    (
        "batches.retrieve",
        "Your script doesn't poll with messages.batches.retrieve() — you need to check batch status.",
        "Poll in a loop: client.messages.batches.retrieve(batch.id) and keep going "
        "while processing_status != 'ended', sleeping a few seconds between checks.",
    ),
    (
        "batches.results",
        "Your script doesn't call messages.batches.results() — you need to retrieve the batch results.",
        "Once the status is 'ended', iterate client.messages.batches.results(batch.id) "
        "— the results are not on the batch object itself.",
    ),
]


def main() -> None:
    require_api_key()
    source = require_exercise(EXERCISE_PATH)
    check_source(source, SOURCE_CHECKS)

    stdout = run_exercise(
        EXERCISE_PATH,
        timeout=TIMEOUT_SECONDS,
        timeout_msg=(
            f"Your script did not finish within {TIMEOUT_SECONDS} seconds. "
            "Batches usually finish within minutes — if this keeps happening, re-run the workflow."
        ),
        timeout_hint=(
            "Make sure your polling loop sleeps between retrieve() calls and exits when "
            "processing_status == 'ended' — a loop that only breaks on 'succeeded' will "
            "spin forever."
        ),
        error_hint=(
            "Check the last line of the stderr traceback. Calling results() before the "
            "batch has ended raises an error — poll until processing_status == 'ended' "
            "first."
        ),
    )

    require_labels(stdout, REQUIRED_LABELS, LABEL_HINTS)

    if not contains(stdout, "batch_id: msgbatch_"):
        fail(
            "Expected the printed 'batch_id:' to start with 'msgbatch_'.",
            expected="a line matching the regex  batch_id:\\s*msgbatch_",
            actual=stdout,
            hint=(
                "Print batch.id itself, not the whole batch object or a custom_id. Real "
                "batch ids always begin with the 'msgbatch_' prefix."
            ),
        )

    succeeded_match = search_value(stdout, "succeeded:")
    errored_match = search_value(stdout, "errored:")
    if not succeeded_match or not errored_match:
        fail(
            "Couldn't parse succeeded/errored counts out of stdout:",
            expected="lines matching  succeeded:\\s*(\\d+)  and  errored:\\s*(\\d+)",
            actual=stdout,
            hint=(
                "Print bare integers after those labels (e.g. 'succeeded: 2'), not lists "
                "or booleans — the grader parses the digits that follow the colon."
            ),
        )

    succeeded = int(succeeded_match.group(1))
    errored = int(errored_match.group(1))
    if succeeded < 2:
        fail(
            f"Expected both batch requests to succeed (succeeded: 2), got succeeded: {succeeded}.",
            expected="succeeded: 2 (both requests in the batch completing successfully)",
            actual=stdout,
            hint=(
                "Send exactly two requests and count every result with "
                "result.type == 'succeeded'. A count of 1 usually means you broke out of "
                "the results loop after the first item."
            ),
        )
    if errored != 0:
        fail(
            f"Expected 0 errored requests, got errored: {errored}.",
            expected="errored: 0 (no request in the batch failing)",
            actual=stdout,
            hint=(
                "Print result.error for each errored item to see the cause — a bad model "
                "name or a missing max_tokens in the per-request params is typical."
            ),
        )

    print("✅ PASS: batch created, polled, and results retrieved correctly.")
    print(stdout)


if __name__ == "__main__":
    main()
