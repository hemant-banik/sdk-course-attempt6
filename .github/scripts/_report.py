#!/usr/bin/env python3
"""Shared failure-reporting helpers for the check_stepN.py graders.

Why this module exists
----------------------
Every grader used to fail with a bare "expected X, not found", which tells a
learner *what* the grader wanted but not what their program actually did, and
gives them no next action. Debugging from that is guesswork.

Every failure printed through here has three parts:

    1. EXPECTED  — the specific string or condition that was being checked.
    2. YOUR OUTPUT — the learner's real captured stdout (truncated), clearly
       delimited so it can't be confused with the grader's own words.
    3. HINT      — one concrete line telling them what to go change.

Grading rules live in the individual check_stepN.py files. Nothing in this
module decides pass or fail; it only formats the report and exits. Exit code
is 1 for every failure, matching the original graders.

This module also owns `normalise()` / `contains()` — the one place that decides
how tolerant stdout matching is (see the comment on `normalise`).

Import contract
---------------
The workflows invoke the graders directly from the repo root
(`python .github/scripts/check_step4.py`), so the script directory is NOT on
sys.path. Each grader bootstraps it with:

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _report import ...

which keeps every grader runnable standalone.
"""
import os
import re
import subprocess
import sys
import textwrap

# Learner stdout is usually a handful of lines; 40 is enough to show the whole
# thing for a normal step while still capping a runaway loop's output.
MAX_OUTPUT_LINES = 40

_WIDTH = 68


def _rule(title: str) -> str:
    """A labeled horizontal rule, e.g. '--- EXPECTED -------------'."""
    prefix = f"--- {title} "
    return prefix + "-" * max(3, _WIDTH - len(prefix))


def truncate_lines(text: str, max_lines: int = MAX_OUTPUT_LINES, keep: str = "head") -> str:
    """Trim `text` to `max_lines` lines, noting how many were dropped.

    keep="head" for stdout (the learner's first prints are what's graded);
    keep="tail" for tracebacks, where the actual exception is at the bottom.
    """
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return "\n".join(lines)

    dropped = len(lines) - max_lines
    if keep == "tail":
        return f"[... {dropped} earlier line(s) omitted ...]\n" + "\n".join(lines[-max_lines:])
    return "\n".join(lines[:max_lines]) + f"\n[... {dropped} more line(s) omitted ...]"


def format_output_block(
    text: str,
    title: str = "YOUR ACTUAL OUTPUT (stdout)",
    max_lines: int = MAX_OUTPUT_LINES,
    keep: str = "head",
    empty_note: str = "(nothing — your script printed no output at all)",
) -> str:
    """Render captured output inside delimiters, with line numbers.

    Line numbers matter here: they make "your 3rd print is the problem"
    something the learner can act on, and they make trailing-whitespace or
    blank-line issues visible instead of invisible.
    """
    body = truncate_lines(text or "", max_lines=max_lines, keep=keep)
    if not body.strip():
        rendered = f"  {empty_note}"
    else:
        numbered = []
        for i, line in enumerate(body.splitlines(), start=1):
            if line.startswith("[..."):  # the truncation marker, not learner output
                numbered.append(f"       {line}")
            else:
                numbered.append(f"  {i:>3} | {line}")
        rendered = "\n".join(numbered)

    return f"{_rule(title)}\n{rendered}\n{'-' * _WIDTH}"


def fail(
    msg: str,
    expected: str = None,
    actual: str = None,
    actual_title: str = "YOUR ACTUAL OUTPUT (stdout)",
    actual_keep: str = "head",
    stderr: str = None,
    hint: str = None,
    exit_code: int = 1,
) -> None:
    """Print a full failure report and exit.

    `actual=""` still renders the (empty) output block — printing nothing is
    itself the most common failure, and hiding it would hide the diagnosis.
    Pass actual=None only when stdout is genuinely irrelevant (e.g. the file
    doesn't exist yet).
    """
    print(f"❌ FAIL: {msg}")

    if expected:
        print()
        print(_rule("EXPECTED"))
        for line in str(expected).splitlines():
            print(f"  {line}")
        print("-" * _WIDTH)

    if actual is not None:
        print()
        print(format_output_block(actual, title=actual_title, keep=actual_keep))

    if stderr is not None and stderr.strip():
        print()
        print(
            format_output_block(
                stderr,
                title="YOUR ERROR OUTPUT (stderr)",
                keep="tail",
                empty_note="(empty)",
            )
        )

    if hint:
        print()
        print(_rule("HINT"))
        # Wrap so long hints stay readable in the Actions log, which does not
        # soft-wrap. 💡 on the first line only; continuations align under it.
        wrapped = []
        for para in str(hint).splitlines():
            wrapped.extend(textwrap.wrap(para, width=_WIDTH - 5) or [""])
        for i, line in enumerate(wrapped):
            print(f"  💡 {line}" if i == 0 else f"     {line}")
        print("-" * _WIDTH)

    sys.exit(exit_code)


# --------------------------------------------------------------------------
# Preconditions shared by nearly every grader
# --------------------------------------------------------------------------

def require_api_key(env: dict = None) -> None:
    """Fail unless ICA_API_KEY is set. Message text unchanged from before."""
    if env is None:
        env = os.environ
    if not env.get("ICA_API_KEY"):
        fail(
            "ICA_API_KEY is not set. Add it as a repo secret: "
            "Settings -> Secrets and variables -> Actions -> New repository secret.",
            expected="The ICA_API_KEY environment variable to be set (non-empty).",
            hint=(
                "In GitHub: Settings -> Secrets and variables -> Actions -> New "
                "repository secret, named exactly ICA_API_KEY. Running locally? "
                "Put ICA_API_KEY=... in a .env file beside your script."
            ),
        )


def require_exercise(path) -> str:
    """Fail unless the exercise file exists; return its source text."""
    if not path.exists():
        fail(
            f"{path} does not exist. Create it as instructed in the issue.",
            expected=f"A file at {path} (relative to the repo root).",
            hint=(
                f"Create it with the exact path and filename: {path}. A typo in the "
                "filename, or committing it to a different folder, both look like "
                "'missing' to the grader."
            ),
        )
    return path.read_text()


# The three client-setup requirements every live-API step shares, in the exact
# order the original graders checked them. Messages are copied verbatim so the
# learner sees no change in *what* is required.
CLIENT_SETUP_CHECKS = [
    (
        "load_dotenv()",
        "Your script doesn't call load_dotenv() \u2014 this project loads the key from a .env file.",
        "Add 'from dotenv import load_dotenv' and call load_dotenv() before you read "
        "os.environ \u2014 without it the key in .env is never loaded.",
    ),
    (
        "ICA_API_KEY",
        "Your script doesn't reference ICA_API_KEY \u2014 that's the key name this project uses.",
        'Read the key with os.environ.get("ICA_API_KEY") \u2014 this course uses '
        "ICA_API_KEY, not ANTHROPIC_API_KEY.",
    ),
    (
        "base_url=",
        "Your script doesn't set base_url= \u2014 this project routes requests through a custom gateway.",
        "Pass base_url=... to Anthropic(...) using this project's gateway URL. It is "
        "spelled exactly 'base_url=' \u2014 not 'baseurl=' or 'base_URL='.",
    ),
]


def check_source(source: str, checks) -> None:
    """Run static source requirements in order, reporting the first failure.

    `checks` is a list of (requirement, message, hint) where requirement is:
      * str      — must appear literally in the source
      * tuple    — at least one member must appear (equivalent forms)
      * callable — called with the source, must return truthy

    Order is preserved exactly, so the first thing a learner is told to fix is
    the same thing the original graders told them to fix.
    """
    for requirement, message, hint in checks:
        if isinstance(requirement, str):
            ok = requirement in source
            expected = f"Your source file to contain: {requirement!r}"
        elif isinstance(requirement, tuple):
            ok = any(item in source for item in requirement)
            forms = " or ".join(repr(item) for item in requirement)
            expected = f"Your source file to contain {forms}"
        else:
            ok = bool(requirement(source))
            expected = message

        if not ok:
            fail(
                message,
                expected=expected,
                actual=source,
                actual_title="YOUR SCRIPT (source as the grader sees it)",
                hint=hint,
            )


# --------------------------------------------------------------------------
# Running the learner's script
# --------------------------------------------------------------------------

def run_exercise(
    path,
    timeout: int,
    error_hint: str,
    error_msg: str = "Your script raised an error when run:",
    timeout_msg: str = None,
    timeout_hint: str = None,
) -> str:
    """Run the exercise, fail with a full report on crash/timeout, return stdout.

    Both failure paths exit 1, same as before. Previously a timeout escaped as
    an unhandled TimeoutExpired traceback (also exit 1) — same outcome, but the
    learner now gets a readable explanation instead of a grader stack trace.
    """
    try:
        result = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        partial = exc.stdout or ""
        if isinstance(partial, bytes):
            partial = partial.decode("utf-8", "replace")
        fail(
            timeout_msg
            or f"Your script did not finish within {timeout} seconds, so it was stopped.",
            expected=f"{path} to run to completion in under {timeout} seconds.",
            actual=partial,
            actual_title="YOUR OUTPUT BEFORE THE TIMEOUT (stdout)",
            hint=timeout_hint
            or (
                "Look for a polling loop with no exit condition, or an input() call "
                "waiting for typing that never comes — CI has no keyboard."
            ),
        )

    if result.returncode != 0:
        fail(
            error_msg,
            expected=f"{path} to exit cleanly (exit code 0).",
            actual=result.stdout,
            stderr=result.stderr,
            hint=error_hint,
        )

    return result.stdout


# --------------------------------------------------------------------------
# Matching tolerance
# --------------------------------------------------------------------------
# Learners lost steps to formatting, not understanding: "Turn 1 :", "turn 1:"
# and "Turn  1:" all mean the same thing, but a plain `in` check only accepted
# one of them. Everything below widens matching for FORMATTING variance only:
#
#   * case            — casefolded on both sides
#   * whitespace runs — any run of spaces/tabs/newlines == one space
#   * space around :  — "a : b", "a:b" and "a:  b" all normalise the same
#
# It deliberately does NOT widen semantic variance. Values still have to be
# right: a needle that ends (or starts) with a digit will not match a longer
# number, so a check for "Messages in list: 4" cannot be satisfied by
# "Messages in list: 42", and "5.5" cannot be satisfied by "15.55".

_WS_RUN = re.compile(r"\s+")
_AROUND_COLON = re.compile(r"\s*:\s*")


def normalise(text: str) -> str:
    """Casefold, collapse whitespace runs, and drop whitespace around colons."""
    collapsed = _WS_RUN.sub(" ", text or "")
    return _AROUND_COLON.sub(":", collapsed).strip().casefold()


def _number_boundary_ok(haystack: str, start: int, end: int, needle: str) -> bool:
    """True if a match isn't just a fragment of a longer number.

    A trailing '.' or ',' is fine ('the answer is 918.') — only a digit, or a
    decimal separator followed by a digit, means we matched part of a bigger
    number and must reject.
    """
    if needle[-1].isdigit():
        after = haystack[end:]
        if re.match(r"[0-9]", after) or re.match(r"[.,][0-9]", after):
            return False
    if needle[0].isdigit():
        before = haystack[:start]
        if re.search(r"[0-9]$", before) or re.search(r"[0-9][.,]$", before):
            return False
    return True


def contains(haystack: str, needle: str) -> bool:
    """Formatting-tolerant substring test (see 'Matching tolerance' above)."""
    hay = normalise(haystack)
    pin = normalise(needle)
    if not pin:
        return True

    start = hay.find(pin)
    while start != -1:
        if _number_boundary_ok(hay, start, start + len(pin), pin):
            return True
        start = hay.find(pin, start + 1)
    return False


def flexible_regex(text: str) -> str:
    """Regex source matching `text` with the same tolerance as `normalise`.

    For checks that must capture a value ("chars streamed: 42") rather than
    just assert presence, so those greps accept the same formatting variance.
    Use with re.IGNORECASE.
    """
    segments = []
    for segment in text.split(":"):
        segments.append(r"\s+".join(re.escape(token) for token in segment.split()))
    return r"\s*:\s*".join(segments)


def search_value(stdout: str, label: str, value_pattern: str = r"(\d+)"):
    """Find `label` followed by `value_pattern` in stdout, tolerantly."""
    return re.search(flexible_regex(label) + value_pattern, stdout, re.IGNORECASE)


def find_values(stdout: str, label: str, value_pattern: str = r"(\S+)"):
    """All values printed after `label` (one per occurrence), tolerantly."""
    return re.findall(flexible_regex(label) + value_pattern, stdout, re.IGNORECASE)


# --------------------------------------------------------------------------
# stdout assertions
# --------------------------------------------------------------------------

def require_labels(stdout: str, labels, hints: dict) -> None:
    """Fail on the first missing label. Same order, same strings as before.

    `hints` maps label -> one-line hint. A label without an entry gets a
    generic fallback rather than no hint at all.
    """
    for label in labels:
        if not contains(stdout, label):
            fail(
                f"Expected a line starting with '{label}' in stdout. Got:",
                expected=(
                    f"stdout to contain {label!r}\n"
                    "(case and spacing don't matter — the wording does)"
                ),
                actual=stdout,
                hint=hints.get(
                    label,
                    f"Add a print that emits {label!r} followed by the value, e.g. "
                    f'print("{label}", value) — capitalisation and spacing are '
                    "forgiven, but the words and the colon must be there.",
                ),
            )


def require_in_stdout(stdout: str, needle: str, msg: str, expected: str, hint: str) -> None:
    """Fail unless `needle` appears in stdout (formatting-tolerant)."""
    if not contains(stdout, needle):
        fail(msg, expected=expected, actual=stdout, hint=hint)


def label_hint(label: str, what: str) -> str:
    """Build the usual 'print this label' hint for a value-bearing label."""
    return (
        f'Print {what} on a line labelled "{label}", e.g. '
        f'print("{label}", {what.split()[0].lower()}) — the grader ignores case '
        "and spacing, but needs the same words."
    )
