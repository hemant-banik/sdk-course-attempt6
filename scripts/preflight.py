#!/usr/bin/env python3
"""Step 0 preflight — prove your environment can talk to the API.

Learner-facing. Run it any time you suspect your setup, not your code, is the
problem:

    python3 scripts/preflight.py

It runs six checks and prints one PASS/FAIL line each. Every failure comes with
a one-line remedy. Exit code is 0 only if all six pass, 1 otherwise, so CI or a
shell `&&` chain can rely on it.

(Graders live in .github/scripts/ — this file is not one of them and is never
run by a workflow.)
"""
import os
import sys
import traceback
from pathlib import Path

# --- config -----------------------------------------------------------------
# Same gateway + model the course exercises use. Keep these in sync with the
# step instructions; a preflight that tests a different endpoint is worthless.
BASE_URL = "https://api.servicesessentials.ibm.com"
MODEL = "claude-sonnet-5"
MIN_PYTHON = (3, 9)
ENV_VAR = "ICA_API_KEY"

# Values people leave behind when they copy .env.example but never edit it.
# Compared lowercase, after stripping quotes/whitespace.
PLACEHOLDERS = {
    "",
    "your-key-here",
    "your_key_here",
    "yourkeyhere",
    "your-api-key",
    "your_api_key",
    "changeme",
    "change-me",
    "todo",
    "xxx",
    "xxxxxxxx",
    "none",
    "null",
    "paste-your-key-here",
    "replace-me",
    "sk-ant-xxx",
    "<your-key>",
}

# Project root = parent of scripts/. Lets you run the script from anywhere.
REPO_ROOT = Path(__file__).resolve().parent.parent
ENV_PATH = REPO_ROOT / ".env"
EXAMPLE_PATH = REPO_ROOT / ".env.example"

PASS = "\u2705"  # white heavy check mark
FAIL = "\u274c"  # cross mark


class CheckFailed(Exception):
    """Raised by a check to report a failure plus its one-line remedy."""

    def __init__(self, reason: str, remedy: str):
        super().__init__(reason)
        self.reason = reason
        self.remedy = remedy


# --- individual checks ------------------------------------------------------
# Each returns a short success detail string, or raises CheckFailed.
# Nothing here is allowed to raise anything else; run_check() is the safety net.


def check_python() -> str:
    v = sys.version_info
    found = f"{v.major}.{v.minor}.{v.micro}"
    if (v.major, v.minor) < MIN_PYTHON:
        raise CheckFailed(
            f"Python {found} is too old (need {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+)",
            "Install Python 3.11 from python.org, or open this repo in a GitHub "
            "Codespace where the right version is preinstalled.",
        )
    return f"Python {found}"


def check_anthropic() -> str:
    try:
        import anthropic
    except ImportError:
        raise CheckFailed(
            "the `anthropic` package is not installed",
            "Run: python3 -m pip install -r requirements.txt",
        )
    version = getattr(anthropic, "__version__", "unknown")
    if version == "unknown":
        # Very old releases didn't expose __version__. Installed is installed,
        # but say so rather than printing a confident wrong number.
        return "anthropic installed (version attribute missing — likely very old)"
    return f"anthropic {version}"


def check_dotenv() -> str:
    try:
        import dotenv  # noqa: F401
    except ImportError:
        raise CheckFailed(
            "the `python-dotenv` package is not installed",
            "Run: python3 -m pip install -r requirements.txt",
        )
    return "python-dotenv installed"


def check_env_file() -> str:
    if not ENV_PATH.exists():
        raise CheckFailed(
            f"no .env file at {ENV_PATH}",
            f"Run: cp {EXAMPLE_PATH.name} .env   (then paste your key into it)",
        )
    if ENV_PATH.is_dir():
        raise CheckFailed(
            ".env exists but is a directory, not a file",
            "Delete it (rm -r .env) and run: cp .env.example .env",
        )
    return f"found {ENV_PATH.name}"


def check_api_key() -> str:
    """Load .env, then sanity-check the key without ever printing it."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        raise CheckFailed(
            "cannot read .env because python-dotenv is missing",
            "Fix the python-dotenv check above first.",
        )

    # override=True so a stale/blank shell variable can't mask the .env value.
    try:
        load_dotenv(dotenv_path=ENV_PATH, override=True)
    except Exception as exc:
        raise CheckFailed(
            f".env could not be parsed ({exc.__class__.__name__})",
            "Each line must look like ICA_API_KEY=value — no spaces around '=', "
            "no stray quotes or blank continuation lines.",
        )

    raw = os.environ.get(ENV_VAR)
    if raw is None:
        raise CheckFailed(
            f"{ENV_VAR} is not set anywhere (.env or shell)",
            f"Add this line to .env:  {ENV_VAR}=<your real key>",
        )

    key = raw.strip().strip("\"'").strip()
    if not key:
        raise CheckFailed(
            f"{ENV_VAR} is set but empty",
            f"Put your real key after the '=' in .env:  {ENV_VAR}=<your real key>",
        )
    if key.lower() in PLACEHOLDERS or key.lower().startswith("your"):
        raise CheckFailed(
            f"{ENV_VAR} still holds the placeholder value {key!r}",
            f"Replace it in .env with your real key:  {ENV_VAR}=<your real key>",
        )
    if len(key) < 12:
        raise CheckFailed(
            f"{ENV_VAR} is only {len(key)} characters — that looks truncated",
            "Re-copy the whole key from IBM Consulting Advantage; don't let the "
            "terminal or editor wrap or cut it.",
        )
    # Show length + last 4 only. Never log a credential.
    return f"{ENV_VAR} present ({len(key)} chars, ends \u2026{key[-4:]})"


def check_api_call() -> str:
    """One real 1-token request. The only check that proves auth + network."""
    try:
        import anthropic
    except ImportError:
        raise CheckFailed(
            "cannot call the API because the `anthropic` package is missing",
            "Run: python3 -m pip install -r requirements.txt",
        )

    key = (os.environ.get(ENV_VAR) or "").strip().strip("\"'").strip()
    if not key:
        raise CheckFailed(
            f"cannot call the API without {ENV_VAR}",
            "Fix the API key check above first.",
        )

    try:
        client = anthropic.Anthropic(api_key=key, base_url=BASE_URL, timeout=30.0)
        resp = client.messages.create(
            model=MODEL,
            max_tokens=1,  # cheapest possible request that still proves auth
            messages=[{"role": "user", "content": "hi"}],
        )
    except Exception as exc:
        raise CheckFailed(*_diagnose_api_error(exc))

    stop = getattr(resp, "stop_reason", "?")
    return f"live call to {MODEL} succeeded (stop_reason={stop})"


def _diagnose_api_error(exc: Exception) -> tuple:
    """Turn an SDK/network exception into (reason, one-line remedy).

    Matched on class name rather than isinstance so this keeps working across
    anthropic SDK versions that move or rename exception classes.
    """
    name = exc.__class__.__name__
    status = getattr(exc, "status_code", None)
    detail = str(exc).strip().splitlines()[0] if str(exc).strip() else name
    # Gateway errors are long JSON blobs; keep the line readable in a terminal.
    if len(detail) > 130:
        detail = detail[:130].rstrip() + "\u2026"

    if status == 401 or name == "AuthenticationError":
        return (
            f"gateway rejected the key (401): {detail}",
            f"Your {ENV_VAR} is wrong or expired — paste a freshly issued key "
            "into .env.",
        )
    if status == 403 or name == "PermissionDeniedError":
        return (
            f"key authenticated but access was denied (403): {detail}",
            "Your key is valid but lacks access to this model — ask your IBM "
            "Consulting Advantage admin to enable it.",
        )
    if status == 404 or name == "NotFoundError":
        return (
            f"endpoint or model not found (404): {detail}",
            f"Check base_url is exactly {BASE_URL} and the model name is "
            f"{MODEL!r}.",
        )
    if status == 429 or name == "RateLimitError":
        return (
            f"rate limited (429): {detail}",
            "Your setup is fine — wait a minute and re-run this script.",
        )
    if name in ("APITimeoutError", "Timeout"):
        return (
            f"request timed out after 30s: {detail}",
            "Check your network/VPN/proxy, then re-run this script.",
        )
    if name in ("APIConnectionError", "ConnectionError") or isinstance(exc, OSError):
        return (
            f"could not reach {BASE_URL}: {detail}",
            "No network route to the gateway — check your internet connection, "
            "VPN, or corporate proxy settings.",
        )
    if status is not None and 500 <= int(status) < 600:
        return (
            f"gateway returned a server error ({status}): {detail}",
            "That's the gateway's side, not yours — retry in a few minutes.",
        )
    return (
        f"{name}: {detail}",
        "Re-run with more detail:  PREFLIGHT_DEBUG=1 python3 scripts/preflight.py",
    )


# --- runner -----------------------------------------------------------------

CHECKS = [
    ("Python version >= 3.9", check_python),
    ("anthropic SDK installed", check_anthropic),
    ("python-dotenv installed", check_dotenv),
    (".env file exists", check_env_file),
    (f"{ENV_VAR} looks like a real key", check_api_key),
    ("Live API call (1 token)", check_api_call),
]


def run_check(label: str, fn) -> bool:
    """Run one check. Never propagates an exception, never prints a traceback.

    An unexpected crash inside a check is reported as a normal FAIL line; the
    full traceback is only shown when PREFLIGHT_DEBUG=1.
    """
    try:
        detail = fn()
        print(f"{PASS} PASS  {label}: {detail}")
        return True
    except CheckFailed as exc:
        print(f"{FAIL} FAIL  {label}: {exc.reason}")
        print(f"         \u2192 Fix: {exc.remedy}")
        return False
    except KeyboardInterrupt:
        print(f"{FAIL} FAIL  {label}: interrupted by user (Ctrl-C)")
        print("         \u2192 Fix: re-run: python3 scripts/preflight.py")
        return False
    except BaseException as exc:  # truly unexpected — still must not traceback
        print(f"{FAIL} FAIL  {label}: unexpected {exc.__class__.__name__}: {exc}")
        print(
            "         \u2192 Fix: re-run with PREFLIGHT_DEBUG=1 to see details, "
            "then paste them into the course discussion."
        )
        if os.environ.get("PREFLIGHT_DEBUG"):
            traceback.print_exc()
        return False


def main() -> int:
    print()
    print("Preflight check \u2014 Anthropic Python SDK course")
    print("=" * 52)

    results = [run_check(label, fn) for label, fn in CHECKS]

    passed = sum(results)
    total = len(results)
    print("=" * 52)

    if passed == total:
        print(f"{PASS} All {total} checks passed \u2014 your environment is ready.")
        print("   Next: open the Step 1 issue in the Issues tab and start coding.")
        print()
        return 0

    print(f"{FAIL} {total - passed} of {total} checks failed.")
    print("   Fix them top-to-bottom (later checks depend on earlier ones),")
    print("   then re-run: python3 scripts/preflight.py")
    print()
    return 1


if __name__ == "__main__":
    # Compute the exit code inside the guard, but call sys.exit() outside it —
    # sys.exit raises SystemExit, which a bare `except BaseException` would eat.
    try:
        code = main()
    except KeyboardInterrupt:
        print("\nInterrupted.")
        code = 1
    except BaseException as exc:  # last-resort guard: no traceback, ever
        print(f"\n{FAIL} preflight itself crashed: {exc.__class__.__name__}: {exc}")
        print("   \u2192 Fix: re-run with PREFLIGHT_DEBUG=1 and report the output.")
        if os.environ.get("PREFLIGHT_DEBUG"):
            traceback.print_exc()
        code = 1
    sys.exit(code)
