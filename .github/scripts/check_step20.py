#!/usr/bin/env python3
"""Grading check for Step 20 — web search tool (server-side tool).

Runs exercises/practice20_web_search.py (live API call through this
project's gateway) using the web_search_20250305 server tool, and checks
stdout has both the labeled block_types line and the answer line.

Deliberately does NOT require a server_tool_use / web_search_tool_result
block to appear. Whether Claude actually searches is a model decision, not
something the learner controls — so requiring it made this step fail
randomly through no fault of the learner. If the search blocks are absent
we still pass, with a warning explaining what happened and why.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _report import (
    CLIENT_SETUP_CHECKS,
    check_source,
    contains,
    flexible_regex,
    require_api_key,
    require_exercise,
    require_in_stdout,
    run_exercise,
)

EXERCISE_PATH = Path("exercises/practice20_web_search.py")

TOOL_TYPE = "web_search_20250305"

# Block types the API emits when a server-side search actually runs.
SEARCH_BLOCK_TYPES = ("server_tool_use", "web_search_tool_result")

SOURCE_CHECKS = CLIENT_SETUP_CHECKS + [
    (
        TOOL_TYPE,
        f"Your script doesn't use tool type '{TOOL_TYPE}' — that's the exact server tool string required.",
        f'The tool type is version-dated and must match exactly: {{"type": '
        f'"{TOOL_TYPE}", "name": "web_search", "max_uses": 3}}.',
    ),
    (
        "web_search",
        "Your script doesn't reference the web_search tool name.",
        'Set "name": "web_search" on the tool entry, alongside the dated type string.',
    ),
]


def search_happened(stdout: str) -> bool:
    """True if stdout shows the server-side search blocks.

    Looks at the reported block_types line rather than all of stdout, so a
    learner echoing the type names in their own prose can't fake a pass.
    """
    # Tolerant on the label's spacing/case, but still line-scoped: the block
    # type names themselves must appear on the block_types line, not anywhere.
    match = re.search(
        r"^\s*" + flexible_regex("block_types:") + r".*$",
        stdout,
        re.MULTILINE | re.IGNORECASE,
    )
    if not match:
        return False
    line = match.group(0)
    return any(contains(line, bt) for bt in SEARCH_BLOCK_TYPES)


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
        "block_types:",
        "Expected a line starting with 'block_types:' in stdout.",
        expected="stdout to contain the literal text 'block_types:'",
        hint=(
            "Print the block types on one line so the grader can inspect them, e.g. "
            'print("block_types:", [b.type for b in response.content]).'
        ),
    )
    require_in_stdout(
        stdout,
        "answer:",
        "Expected a line starting with 'answer:' in stdout.",
        expected="stdout to contain the literal text 'answer:'",
        hint=(
            'Print the reply text with the exact lowercase label, e.g. '
            'print("answer:", final_text) — join the text blocks from response.content.'
        ),
    )

    if search_happened(stdout):
        print("✅ PASS: web search tool ran and returned a cited answer.")
    else:
        # Not the learner's fault, and not worth a red X. Explain and pass.
        print("✅ PASS (with warning): your script is wired up correctly.")
        print()
        print(
            "⚠️  Heads up: this run shows no 'server_tool_use' or\n"
            "    'web_search_tool_result' block, which means Claude answered\n"
            "    from its own knowledge instead of running a search.\n"
            "\n"
            "    That is a model decision, not a bug in your code — the tool is\n"
            "    offered, and Claude chooses whether to reach for it. Your setup\n"
            "    passed every structural requirement (correct tool type, gateway\n"
            "    client, and both output labels), so you are NOT being marked\n"
            "    down for it.\n"
            "\n"
            "    Want to see the search blocks? Re-run the script — the same\n"
            "    prompt often searches on a second attempt. Asking for something\n"
            "    that literally cannot be in training data (today's date, today's\n"
            "    top headline) makes searching far more likely."
        )
    print(stdout)


if __name__ == "__main__":
    main()
