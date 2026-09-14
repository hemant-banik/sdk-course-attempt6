#!/usr/bin/env python3
"""Grading check for Step 15 — Async client (AsyncAnthropic).

Runs exercises/practice15_async_client.py (live API calls through this
project's gateway) and checks stdout has both expected labeled answer
lines, confirming asyncio.gather concurrency worked and both async calls
completed successfully.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _report import (  # noqa: E402
    CLIENT_SETUP_CHECKS,
    check_source,
    require_api_key,
    require_exercise,
    require_labels,
    run_exercise,
)

EXERCISE_PATH = Path("exercises/practice15_async_client.py")

REQUIRED_LABELS = ["answer_1:", "answer_2:"]

LABEL_HINTS = {
    "answer_1:": (
        "Unpack the gather() results and print the first one with the exact "
        'snake_case label, e.g. print("answer_1:", r1.content[0].text).'
    ),
    "answer_2:": (
        'Print the second gathered result too: '
        'print("answer_2:", r2.content[0].text) — note the underscore in "answer_2:".'
    ),
}

SOURCE_CHECKS = CLIENT_SETUP_CHECKS + [
    (
        "AsyncAnthropic",
        "Your script doesn't use AsyncAnthropic — that's the whole point of this step!",
        "Instantiate the async client: client = AsyncAnthropic(api_key=..., "
        "base_url=...). The sync Anthropic class cannot be awaited.",
    ),
    (
        # Both async markers were required together in the original grader.
        lambda src: "async def" in src and "await " in src,
        "Your script doesn't use async/await — you need an async def main() with awaited calls.",
        "Define 'async def main():' and await each request: "
        "response = await client.messages.create(...).",
    ),
    (
        "asyncio.run",
        "Your script doesn't call asyncio.run(main()) to actually run the coroutine.",
        "Calling main() alone just builds a coroutine and warns 'never awaited' — "
        "start the event loop with asyncio.run(main()).",
    ),
    (
        "asyncio.gather",
        "Your script doesn't use asyncio.gather() — you need to run both requests concurrently.",
        "Awaiting the two calls on separate lines runs them one after another. Use "
        "r1, r2 = await asyncio.gather(coro1, coro2) to overlap them.",
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
            "Check the last line of the stderr traceback. 'coroutine was never awaited' "
            "means a missing await; 'object Message can't be used in await expression' "
            "means you awaited the sync client."
        ),
    )

    require_labels(stdout, REQUIRED_LABELS, LABEL_HINTS)

    print("✅ PASS: async client fired concurrent requests correctly.")
    print(stdout)


if __name__ == "__main__":
    main()
