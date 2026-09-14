#!/usr/bin/env python3
"""Grading check for Step 22 — capstone tool-using CLI assistant (FINAL STEP).

The capstone is graded on behaviour, not on matching a reference file. It
runs exercises/practice22_capstone.py (live API calls through this project's
gateway) and verifies the five things the brief asks for:

  R2/R3  a tool schema is defined and the tool_use -> tool_result round trip
         completes, with a real (non-error) tool result
  R4     conversation state accumulates: >= 2 assistant answers, >= 4 turns
  R5     a SPECIFIC anthropic exception class is caught, not bare Exception
  R6     safe text extraction (block.type == "text"), never content[0].text

Because learners write this one from scratch, the source checks accept any
reasonable spelling of each requirement rather than one canonical form.
"""
import io
import re
import sys
import token
import tokenize
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _report import (
    CLIENT_SETUP_CHECKS,
    check_source,
    contains,
    fail,
    find_values,
    require_api_key,
    require_exercise,
    require_labels,
    run_exercise,
    search_value,
)

EXERCISE_PATH = Path("exercises/practice22_capstone.py")

MIN_ASSISTANT_TURNS = 2
MIN_CONVERSATION_TURNS = 4

REQUIRED_LABELS = [
    "capstone: start",
    "stop_reason:",
    "tool name:",
    "tool input:",
    "tool result:",
    "assistant:",
    "conversation turns:",
    "capstone: done",
]

LABEL_HINTS = {
    "capstone: start": (
        'print("capstone: start") as the first line of main(), before the '
        "conversation loop — it proves your script reached the loop at all."
    ),
    "stop_reason:": (
        'print("stop_reason:", response.stop_reason) after EVERY create() call. '
        "At least one of them must read 'tool_use'."
    ),
    "tool name:": (
        "For each tool_use block in response.content, print its name: "
        'print("tool name:", block.name).'
    ),
    "tool input:": (
        'Print the arguments Claude chose: print("tool input:", block.input) — '
        "a dict like {'expression': '127 * 8 + 40'}."
    ),
    "tool result:": (
        "After running your Python function on block.input, print what it "
        'returned: print("tool result:", result). This is the value you then '
        "send back in the tool_result block."
    ),
    "assistant:": (
        'Print each final answer on its own line: print("assistant:", '
        f"get_text(response)). The grader needs at least {MIN_ASSISTANT_TURNS} "
        "of these, one per user question."
    ),
    "conversation turns:": (
        'At the end print the size of your messages list: '
        'print("conversation turns:", len(messages)) — it proves the '
        "conversation history actually accumulated."
    ),
    "capstone: done": (
        'print("capstone: done") as the very last line, after the loop '
        "finishes — it proves your script ran to completion instead of dying "
        "part-way through."
    ),
}


# --------------------------------------------------------------------------
# source-level requirement helpers
# --------------------------------------------------------------------------


def code_only(source: str) -> str:
    """The source with comments and string/docstring bodies blanked out.

    Requirement checks that must reflect what the code DOES run through this
    first. Without it a learner who writes `# never do content[0].text` in a
    comment gets failed for the thing they correctly avoided, and one who
    writes `"except anthropic.RateLimitError"` inside a docstring gets credit
    for handling an error they never handle. Falls back to the raw source if
    the file doesn't tokenise (a syntax error is reported elsewhere).
    """
    try:
        pieces = []
        for tok in tokenize.generate_tokens(io.StringIO(source).readline):
            if tok.type == token.COMMENT:
                continue
            if tok.type == token.STRING:
                # Keep the quotes so `== "text"` style checks can still match
                # real code, but blank multi-line strings (docstrings) entirely.
                if "\n" in tok.string:
                    pieces.append("\n" * tok.string.count("\n"))
                    continue
            pieces.append(tok.string)
            if tok.type in (token.NEWLINE, token.NL):
                pieces.append("\n")
        # Tokens are re-joined with spaces, which would turn
        # `anthropic.APIStatusError` into `anthropic . APIStatusError`, so
        # close the gaps around the punctuation the checks below look through.
        rejoined = " ".join(pieces)
        return _TIGHTEN_PUNCT.sub(r"\1", rejoined)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return source

# Collapse the whitespace tokenize inserts around . [ ] ( ) so that dotted
# names and subscripts read the same as they do in the original source.
_TIGHTEN_PUNCT = re.compile(r"\s*([.\[\]()])\s*")

# R5: `except anthropic.SomethingError` or `except SomethingError` where the
# name is an SDK class. Deliberately does NOT match bare `except Exception:`
# or `except:` — catching narrowly is the thing being taught.
_SPECIFIC_ANTHROPIC_EXCEPT = re.compile(
    r"except\s*\(?\s*(?:[A-Za-z_][\w.]*\s*,\s*)*"
    r"(?:anthropic\.)?"
    r"(?:API(?:Status|Connection|Timeout|Response|Error)\w*|"
    r"RateLimitError|BadRequestError|AuthenticationError|PermissionDeniedError|"
    r"NotFoundError|UnprocessableEntityError|ConflictError|"
    r"InternalServerError|OverloadedError|AnthropicError)"
)

# R6: a `.type == "text"` style comparison, quote style and spacing tolerant.
_TYPE_TEXT_COMPARISON = re.compile(
    r"""(?:\.type|\[\s*['"]type['"]\s*\])\s*==\s*['"]text['"]"""
)

# R6 (negative): content[0].text — the pattern the whole course warns against.
# Tolerates whitespace inside the subscript (tokenised code is re-spaced).
_UNSAFE_INDEXING = re.compile(r"content\s*\[\s*0\s*\]\s*\.\s*text")


def _has_specific_anthropic_except(source: str) -> bool:
    return bool(_SPECIFIC_ANTHROPIC_EXCEPT.search(code_only(source)))


def _has_safe_text_extraction(source: str) -> bool:
    return bool(_TYPE_TEXT_COMPARISON.search(code_only(source)))


def _no_unsafe_indexing(source: str) -> bool:
    return not _UNSAFE_INDEXING.search(code_only(source))


SOURCE_CHECKS = CLIENT_SETUP_CHECKS + [
    (
        "claude-sonnet-5",
        "Your script doesn't use the claude-sonnet-5 model.",
        'Set model="claude-sonnet-5" on your create() calls — the whole course '
        "uses this one model so costs stay predictable.",
    ),
    (
        "input_schema",
        "Your script doesn't define a tool with an input_schema (requirement R2).",
        "Your tool needs a schema so Claude knows what arguments to send: "
        '{"name": "calculate", "description": "...", "input_schema": '
        '{"type": "object", "properties": {...}, "required": [...]}}.',
    ),
    (
        "tools",
        "Your script never passes a tools= argument to messages.create().",
        "Offer the tool on EVERY create() call: client.messages.create(..., "
        "tools=TOOLS, messages=messages) — including the call that follows a "
        "tool_result, or the API rejects the history.",
    ),
    (
        "tool_result",
        "Your script never builds a tool_result block (requirement R3).",
        "After running your function, send the answer back as a user turn: "
        '{"role": "user", "content": [{"type": "tool_result", "tool_use_id": '
        'block.id, "content": result}]}.',
    ),
    (
        "tool_use_id",
        "Your tool_result block is missing tool_use_id (requirement R3).",
        "The tool_result must echo the id of the tool_use block it answers: "
        '"tool_use_id": block.id. Without the matching id the API can\'t pair '
        "result to request and returns a 400.",
    ),
    (
        _has_specific_anthropic_except,
        "Your script doesn't catch a specific anthropic exception class "
        "(requirement R5).",
        "Wrap your create() calls in try/except and name the SDK's own class, "
        "e.g. 'except anthropic.APIStatusError as exc:' (or RateLimitError / "
        "APIConnectionError). A bare 'except:' or 'except Exception:' also "
        "swallows your own typos, so it doesn't count.",
    ),
    (
        _has_safe_text_extraction,
        "Your script doesn't use the safe text-extraction pattern "
        "(requirement R6).",
        "Loop over the blocks and filter by type: 'for block in "
        "response.content: if block.type == \"text\": return block.text'. "
        "Block order is not guaranteed, so position-based access is a coin flip.",
    ),
    (
        _no_unsafe_indexing,
        "Your script reads response.content[0].text — that's the unsafe "
        "pattern this course warns about (requirement R6).",
        "In this step Claude often returns a tool_use block first, so "
        "content[0] raises AttributeError. Replace it with a get_text(response) "
        'helper that loops for the first block whose .type == "text".',
    ),
]


def main() -> None:
    require_api_key()
    source = require_exercise(EXERCISE_PATH)
    check_source(source, SOURCE_CHECKS)

    stdout = run_exercise(
        EXERCISE_PATH,
        timeout=180,
        error_msg="Your capstone script raised an error when run:",
        error_hint=(
            "Check the last line of the stderr traceback. A 400 about tool_result "
            "means the assistant's tool_use turn wasn't appended to messages "
            "before the tool_result, or the tool_use_id doesn't match. An "
            "AttributeError about .text means you indexed content[0] instead of "
            "filtering on block.type. An EOFError means you called input() "
            "without guarding for CI — wrap it in sys.stdin.isatty() and fall "
            "back to a scripted list of questions."
        ),
        timeout_hint=(
            "Most likely an unguarded input() waiting for a keyboard that CI "
            "doesn't have — guard it with sys.stdin.isatty() and use scripted "
            "questions otherwise. Otherwise your tool loop never exits: cap it "
            "with 'for _ in range(5):' and stop when stop_reason != 'tool_use'."
        ),
    )

    require_labels(stdout, REQUIRED_LABELS, LABEL_HINTS)

    # --- R3: the tool was actually exercised, not just declared -----------
    if not contains(stdout, "stop_reason: tool_use"):
        fail(
            "No 'stop_reason: tool_use' in your output — Claude never actually "
            "called your tool. Got:",
            expected="stdout to contain the literal text 'stop_reason: tool_use'",
            actual=stdout,
            hint=(
                "Every stop_reason printed 'end_turn', so Claude answered from "
                "memory instead of using the tool. Pass tools=TOOLS on the call, "
                "make one of your questions clearly need the tool (e.g. 'What is "
                "127 * 8 + 40?'), and write a description that says when to use it."
            ),
        )

    # A tool_result round trip must be FOLLOWED by another call, otherwise the
    # learner printed the result and stopped without ever getting prose back.
    if not contains(stdout, "stop_reason: end_turn"):
        fail(
            "Your output has 'stop_reason: tool_use' but never "
            "'stop_reason: end_turn' — you stopped after running the tool "
            "instead of calling the API again. Got:",
            expected=(
                "stdout to contain BOTH 'stop_reason: tool_use' (Claude asks for "
                "the tool) AND a later 'stop_reason: end_turn' (Claude's answer "
                "after you send the tool_result back)"
            ),
            actual=stdout,
            hint=(
                "The tool_result you append is INPUT, not an answer. After "
                "appending it you must call client.messages.create() again with "
                "the grown messages list — loop while stop_reason == 'tool_use'."
            ),
        )

    # --- R2: the tool did real work ---------------------------------------
    tool_results = find_values(stdout, "tool result:", r"(.+)")
    non_empty = [value.strip() for value in tool_results if value.strip()]
    if not non_empty:
        fail(
            "Your 'tool result:' line printed nothing — the tool didn't return "
            "a value. Got:",
            expected="'tool result:' followed by the value your function returned",
            actual=stdout,
            hint=(
                "Call your Python function with block.input and print what comes "
                'back: result = calculate(**block.input); print("tool result:", '
                "result). A function that returns None prints an empty value here."
            ),
        )

    if all(value.lower().startswith("error") for value in non_empty):
        fail(
            "Every 'tool result:' looks like an error — your tool function "
            "rejected or failed on Claude's input. Got:",
            expected=(
                "at least one 'tool result:' with a real computed value "
                "(not starting with 'error')"
            ),
            actual=stdout,
            hint=(
                "Print block.input and check it matches what your function "
                "accepts. Usually the tool description or input_schema describes "
                "a different format than the code parses — tighten the schema "
                "description so Claude sends what you can handle."
            ),
        )

    # --- R4: multi-turn conversation --------------------------------------
    assistant_answers = find_values(stdout, "assistant:", r"(.*)")
    if len(assistant_answers) < MIN_ASSISTANT_TURNS:
        fail(
            f"Found {len(assistant_answers)} 'assistant:' line(s) — the capstone "
            f"needs at least {MIN_ASSISTANT_TURNS}, one per user question. Got:",
            expected=(
                f"at least {MIN_ASSISTANT_TURNS} lines starting with 'assistant:', "
                "proving the assistant answered more than one user turn"
            ),
            actual=stdout,
            hint=(
                "Requirement R4: ask at least two questions in one run, sharing "
                "ONE messages list. Loop over your questions and print "
                '"assistant:" once per completed turn — outside the tool branch, '
                "so it prints on both the tool and no-tool paths."
            ),
        )

    if not any(answer.strip() for answer in assistant_answers):
        fail(
            "Every 'assistant:' line is empty — get_text() found no text block. Got:",
            expected="'assistant:' followed by the text of Claude's reply",
            actual=stdout,
            hint=(
                "You're printing the reply to the tool_result call before making "
                "it, or your get_text() filters on the wrong type string. It must "
                'be block.type == "text" exactly, and you must print the reply '
                "from the call AFTER the tool_result was sent."
            ),
        )

    # --- R4: history actually accumulated ---------------------------------
    turns_match = search_value(stdout, "conversation turns:", r"(\d+)")
    if not turns_match:
        fail(
            "'conversation turns:' wasn't followed by a number. Got:",
            expected="'conversation turns:' followed by an integer, e.g. "
            "'conversation turns: 6'",
            actual=stdout,
            hint=(
                'print("conversation turns:", len(messages)) at the end — the '
                "grader reads the number to confirm history accumulated."
            ),
        )

    turns = int(turns_match.group(1))
    if turns < MIN_CONVERSATION_TURNS:
        fail(
            f"conversation turns: {turns} — too few. A two-question session with "
            f"one tool round trip has at least {MIN_CONVERSATION_TURNS} turns. Got:",
            expected=(
                f"'conversation turns:' to report {MIN_CONVERSATION_TURNS} or more "
                "(user, assistant tool_use, user tool_result, assistant, ...)"
            ),
            actual=stdout,
            hint=(
                "You're rebuilding messages for each question instead of growing "
                "one list, or you're not appending the round-trip turns. Append "
                "BOTH {'role': 'assistant', 'content': response.content} and the "
                "tool_result user turn to the same list the loop reuses."
            ),
        )

    print("✅ PASS: capstone assistant holds a conversation, calls a tool, and "
          "handles errors safely.")
    print(stdout)


if __name__ == "__main__":
    main()
