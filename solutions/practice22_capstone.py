"""REFERENCE SOLUTION — Step 22: Capstone tool-using CLI assistant (FINAL STEP)

This is the capstone: it combines the client setup from Step 1, multi-turn
conversation state from Step 4, tool use from Step 8, the safe text-extraction
pattern used throughout, and error handling from Step 16 — all in one file.

Read it after you've made a real attempt of your own. Every requirement from
the step brief (R1-R7) is annotated below.

Run:
    pip install anthropic python-dotenv
    python exercises/practice22_capstone.py
"""
import os
import sys

import anthropic
from anthropic import Anthropic
from dotenv import load_dotenv

# --- R1: standard client setup, identical to every other step -------------
load_dotenv()
config = {"ICA_API_KEY": os.environ.get("ICA_API_KEY")}

client = Anthropic(
    api_key=config["ICA_API_KEY"],
    base_url="https://api.servicesessentials.ibm.com",
)

MODEL = "claude-sonnet-5"
MAX_TOOL_HOPS = 5  # safety cap so a misbehaving loop can never run forever


# --- R2: a real tool — schema + an implementation that actually computes ---
TOOLS = [
    {
        "name": "calculate",
        "description": (
            "Evaluate an arithmetic expression and return the numeric result. "
            "Use this whenever the user asks for a calculation, instead of "
            "doing the arithmetic yourself. Supports + - * / ** % and "
            "parentheses over numbers only."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": (
                        "A pure arithmetic expression, e.g. '127 * 8 + 40'. "
                        "Digits, spaces, and the operators + - * / ** % ( ) only."
                    ),
                }
            },
            "required": ["expression"],
        },
    }
]

# Characters we are willing to hand to eval(). Anything else is rejected
# before evaluation, so Claude cannot talk us into running arbitrary code.
_ALLOWED = set("0123456789.+-*/%() ")


def calculate(expression: str) -> str:
    """Run the arithmetic. Returns the result as a string, or an 'error: ...'
    string — never raises, because a raised tool error would kill the loop."""
    expr = (expression or "").strip()
    if not expr:
        return "error: empty expression"
    if not set(expr) <= _ALLOWED:
        bad = "".join(sorted(set(expr) - _ALLOWED))
        return f"error: unsupported characters {bad!r} — arithmetic only"
    try:
        # Safe enough given the whitelist above: no names, no calls possible.
        value = eval(expr, {"__builtins__": {}}, {})  # noqa: S307
    except ZeroDivisionError:
        return "error: division by zero"
    except SyntaxError:
        return f"error: could not parse {expr!r}"
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return str(value)


def run_tool(name: str, tool_input: dict) -> str:
    """Dispatch a tool_use block to the matching Python function."""
    if name == "calculate":
        return calculate(tool_input.get("expression", ""))
    return f"error: unknown tool {name!r}"


# --- R6: safe text extraction — NEVER response.content[0].text ------------
def get_text(response) -> str:
    """Return the first text block's text, or "" if the reply has none.

    Block order is not guaranteed: a reply can lead with a thinking block or
    a tool_use block, so indexing [0] is a coin flip.
    """
    for block in response.content:
        if block.type == "text":
            return block.text
    return ""


# --- R7: works with a keyboard AND unattended in CI -----------------------
SCRIPTED_TURNS = [
    "What is 127 * 8 + 40? Use your calculator tool.",
    "Nice. Remind me what calculation I just asked you to do, and the answer.",
]


def user_turns():
    """Yield user questions. Interactive when a TTY is attached (real CLI),
    scripted otherwise (GitHub Actions has no keyboard — bare input() there
    raises EOFError and would fail the grader)."""
    if not sys.stdin.isatty():
        for question in SCRIPTED_TURNS:
            print(f"you> {question}")
            yield question
        return

    while True:
        try:
            question = input("you> ").strip()
        except EOFError:
            return
        if not question or question.lower() in {"quit", "exit"}:
            return
        yield question


# --- R3 + R5: the agentic loop, with narrow exception handling ------------
def ask(messages: list) -> tuple[str, int]:
    """Drive one user turn to completion, running tools as requested.

    `messages` is mutated in place — it is the single source of conversation
    state (R4). Returns (assistant_text, errors_caught).
    """
    errors = 0

    for _ in range(MAX_TOOL_HOPS):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=500,
                tools=TOOLS,  # required on EVERY call, not just the first
                messages=messages,
            )
        # R5: a SPECIFIC anthropic exception class, not bare `except Exception`.
        # APIStatusError covers every 4xx/5xx (RateLimitError, NotFoundError,
        # OverloadedError are all subclasses); APIConnectionError covers
        # network failures where no status ever arrived.
        except anthropic.APIStatusError as exc:
            errors += 1
            print("api_error:", type(exc).__name__, "status", exc.status_code)
            return "", errors
        except anthropic.APIConnectionError as exc:
            errors += 1
            print("api_error:", type(exc).__name__, str(exc))
            return "", errors

        print("stop_reason:", response.stop_reason)

        if response.stop_reason != "tool_use":
            text = get_text(response)
            # Append the assistant's own words so the next turn has history.
            messages.append({"role": "assistant", "content": text})
            return text, errors

        # --- tool round trip -------------------------------------------
        # 1. Replay Claude's tool request verbatim. Skipping this is the #1
        #    cause of "tool_result without a corresponding tool_use block".
        messages.append({"role": "assistant", "content": response.content})

        # 2. Run every tool Claude asked for; collect one result per request.
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            print("tool name:", block.name)
            print("tool input:", block.input)
            result = run_tool(block.name, block.input)
            print("tool result:", result)
            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,  # the receipt number
                    "content": result,
                }
            )

        # 3. Hand the results back as a USER turn, then loop for the prose.
        messages.append({"role": "user", "content": results})

    print("api_error: tool loop exceeded", MAX_TOOL_HOPS, "hops")
    return "", errors + 1


def main() -> None:
    print("capstone: start")

    messages: list = []  # R4: ONE list for the whole session
    errors_caught = 0

    for question in user_turns():
        messages.append({"role": "user", "content": question})
        text, errors = ask(messages)
        errors_caught += errors
        print("assistant:", text)

    print("conversation turns:", len(messages))
    print("errors caught:", errors_caught)
    print("capstone: done")


if __name__ == "__main__":
    main()
