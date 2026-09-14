#!/usr/bin/env python3
"""Grading check for Step 12 — prompt caching.

Runs exercises/practice12_caching.py (two live API calls through this
project's gateway) and checks stdout shows the first call writing to the
cache and the second call reading from it.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _report import (
    CLIENT_SETUP_CHECKS,
    check_source,
    fail,
    require_api_key,
    require_exercise,
    require_labels,
    run_exercise,
    search_value,
)

EXERCISE_PATH = Path("exercises/practice12_caching.py")

REQUIRED_LABELS = [
    "first cache_creation_input_tokens:",
    "first cache_read_input_tokens:",
    "second cache_creation_input_tokens:",
    "second cache_read_input_tokens:",
]

_USAGE_HINT = (
    "Read it off the first response's usage object: "
    'print("first cache_creation_input_tokens:", r1.usage.cache_creation_input_tokens).'
)

LABEL_HINTS = {
    "first cache_creation_input_tokens:": _USAGE_HINT,
    "first cache_read_input_tokens:": (
        'print("first cache_read_input_tokens:", r1.usage.cache_read_input_tokens) '
        "— expected to be 0 on the very first call."
    ),
    "second cache_creation_input_tokens:": (
        'Same field, second response: print("second cache_creation_input_tokens:", '
        "r2.usage.cache_creation_input_tokens) — usually 0 on the cache hit."
    ),
    "second cache_read_input_tokens:": (
        'print("second cache_read_input_tokens:", r2.usage.cache_read_input_tokens) '
        "— this is the number that proves the cache was reused."
    ),
}

SOURCE_CHECKS = CLIENT_SETUP_CHECKS + [
    (
        "cache_control",
        "Your script doesn't set cache_control on any block — that's what enables caching.",
        'Mark the large block you want cached with "cache_control": '
        '{"type": "ephemeral"} — caching never happens implicitly.',
    ),
    (
        "ephemeral",
        "Your script doesn't use {'type': 'ephemeral'} for cache_control.",
        'cache_control takes {"type": "ephemeral"} — that is currently the only '
        "supported cache type.",
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
            "Check the last line of the stderr traceback. AttributeError on "
            "cache_creation_input_tokens means you read it off the response instead of "
            "response.usage; a 400 usually means cache_control sat on the wrong block."
        ),
    )

    require_labels(stdout, REQUIRED_LABELS, LABEL_HINTS)

    creation_match = search_value(stdout, "first cache_creation_input_tokens:")
    if not creation_match or int(creation_match.group(1)) <= 0:
        fail(
            "Expected 'first cache_creation_input_tokens:' to be greater than 0 (the cache write). Got:",
            expected=(
                "a line matching  first cache_creation_input_tokens:\\s*(\\d+)  "
                "with a value > 0"
            ),
            actual=stdout,
            hint=(
                "A 0 here means nothing was cached. The cached prefix must be large "
                "enough to hit the minimum cacheable length (~1024 tokens) — pad the "
                "system prompt with more text."
            ),
        )

    read_match = search_value(stdout, "second cache_read_input_tokens:")
    if not read_match or int(read_match.group(1)) <= 0:
        fail(
            "Expected 'second cache_read_input_tokens:' to be greater than 0 (the cache hit). Got:",
            expected=(
                "a line matching  second cache_read_input_tokens:\\s*(\\d+)  "
                "with a value > 0"
            ),
            actual=stdout,
            hint=(
                "A 0 means the second call missed the cache. The cached prefix must be "
                "byte-for-byte identical between the two calls — even one changed "
                "character (or a different model) invalidates it."
            ),
        )

    print("✅ PASS: prompt caching wrote on the first call and was read on the second call.")
    print(stdout)


if __name__ == "__main__":
    main()
