#!/usr/bin/env python3
"""End-to-end proof of the matching-tolerance change.

Unlike test_grader_tolerance.py (which unit-tests the helpers), this runs the
REAL grader scripts as subprocesses against stub exercise files, in a throwaway
repo layout. It proves the two properties that matter:

    1. FORMATTING variance now PASSES  — "turn 1 :" instead of "Turn 1:"
    2. SEMANTIC variance still FAILS   — wrong numbers, wrong names, missing
                                         labels, and cheat attempts

Stub exercises print canned text and never touch the network, so this suite is
offline and fast. ICA_API_KEY is faked because require_api_key() only checks
that the variable is set (non-empty), never that it works.

Run: python3 -m pytest .github/scripts/test_grader_stub_runs.py -v
"""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent


def run_grader(grader: str, exercise_rel: str, exercise_body: str):
    """Run a grader in a temp repo containing one stub exercise.

    Returns (exit_code, combined_output). Exit 0 == learner passed.
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        # Graders resolve exercises relative to cwd, and import _report from
        # their own directory — so copy the scripts dir in and run from tmp.
        shutil.copytree(SCRIPTS_DIR, tmp_path / "scripts")
        exercise = tmp_path / exercise_rel
        exercise.parent.mkdir(parents=True, exist_ok=True)
        exercise.write_text(exercise_body)

        env = dict(os.environ, ICA_API_KEY="stub-key-for-offline-grader-test")
        proc = subprocess.run(
            [sys.executable, str(tmp_path / "scripts" / grader)],
            cwd=tmp_path,
            capture_output=True,
            text=True,
            timeout=120,
            env=env,
        )
        return proc.returncode, proc.stdout + proc.stderr


# Graders also run check_source() for CLIENT_SETUP_CHECKS (load_dotenv(),
# ICA_API_KEY, base_url=). These lines satisfy those so each test isolates the
# thing under test: stdout matching. Kept unreachable so nothing executes.
CLIENT_SETUP_BOILERPLATE = '''
    import os
    import anthropic
    from dotenv import load_dotenv
    load_dotenv()
    client = anthropic.Anthropic(
        api_key=os.environ.get("ICA_API_KEY"),
        base_url="https://example.invalid",
    )
'''

STEP4_SOURCE_BOILERPLATE = CLIENT_SETUP_BOILERPLATE + '''
    messages = []
    messages.append({"role": "user", "content": "hi"})
    client.messages.create(model="m", max_tokens=100, messages=messages)
'''


def step4_stub(turn1_label, turn2_label, count_label, name="Zara") -> str:
    """Build a stub practice4 exercise with caller-controlled label formatting."""
    return f'''"""Stub exercise for grader testing — no network calls."""
if False:
{STEP4_SOURCE_BOILERPLATE}

print("{turn1_label} Nice to meet you, {name}!")
print("{turn2_label} Your name is {name}.")
print("{count_label}")
'''


class TestFormattingVarianceNowPasses(unittest.TestCase):
    """Semantically correct answers must pass despite cosmetic differences."""

    EXERCISE = "exercises/practice4_multiturn.py"

    def assert_passes(self, body, label):
        code, out = run_grader("check_step4.py", self.EXERCISE, body)
        self.assertEqual(code, 0, f"{label} should PASS but exited {code}:\n{out}")
        self.assertIn("PASS", out)

    def test_canonical_formatting_passes(self):
        """Baseline: the exact documented format still passes."""
        self.assert_passes(
            step4_stub("Turn 1:", "Turn 2:", "Messages in list: 4"),
            "canonical formatting",
        )

    def test_lowercase_labels_pass(self):
        self.assert_passes(
            step4_stub("turn 1:", "turn 2:", "messages in list: 4"),
            "lowercased labels",
        )

    def test_uppercase_labels_pass(self):
        self.assert_passes(
            step4_stub("TURN 1:", "TURN 2:", "MESSAGES IN LIST: 4"),
            "uppercased labels",
        )

    def test_space_before_colon_passes(self):
        """The exact case the maintainer hit: 'turn 1 :'."""
        self.assert_passes(
            step4_stub("turn 1 :", "turn 2 :", "messages in list : 4"),
            "space before colon",
        )

    def test_double_space_after_colon_passes(self):
        self.assert_passes(
            step4_stub("Turn  1:", "Turn  2:", "Messages in list:  4"),
            "doubled internal spaces",
        )

    def test_no_space_after_colon_passes(self):
        self.assert_passes(
            step4_stub("Turn 1:", "Turn 2:", "Messages in list:4"),
            "no space after colon",
        )

    def test_tabs_instead_of_spaces_pass(self):
        self.assert_passes(
            step4_stub("Turn\\t1:", "Turn\\t2:", "Messages in list:\\t4"),
            "tab separators",
        )

    def test_mixed_case_name_passes(self):
        self.assert_passes(
            step4_stub("Turn 1:", "Turn 2:", "Messages in list: 4", name="ZARA"),
            "uppercased name",
        )


class TestSemanticVarianceStillFails(unittest.TestCase):
    """Wrong answers must still fail. This is the guardrail on the change."""

    EXERCISE = "exercises/practice4_multiturn.py"

    def assert_fails(self, body, label):
        code, out = run_grader("check_step4.py", self.EXERCISE, body)
        self.assertNotEqual(code, 0, f"{label} should FAIL but PASSED:\n{out}")
        return out

    def test_wrong_message_count_fails(self):
        """3 != 4 — numbers must still match exactly."""
        out = self.assert_fails(
            step4_stub("Turn 1:", "Turn 2:", "Messages in list: 3"),
            "wrong count (3 not 4)",
        )
        self.assertIn("Messages in list: 4", out)

    def test_wrong_count_with_tolerant_formatting_still_fails(self):
        """Tolerant formatting must not smuggle a wrong value through."""
        self.assert_fails(
            step4_stub("turn 1 :", "turn 2 :", "messages in list : 7"),
            "wrong count in tolerant formatting",
        )

    def test_digit_substring_does_not_satisfy_count(self):
        """'40' must not satisfy a required '4' via loose matching."""
        self.assert_fails(
            step4_stub("Turn 1:", "Turn 2:", "Messages in list: 40"),
            "count 40 instead of 4",
        )

    def test_wrong_name_fails(self):
        """Forgetting history => wrong name. Semantic failure, must fail."""
        self.assert_fails(
            step4_stub("Turn 1:", "Turn 2:", "Messages in list: 4", name="Bob"),
            "wrong name",
        )

    def test_missing_label_fails(self):
        body = f'''"""Stub exercise for grader testing."""
if False:
{STEP4_SOURCE_BOILERPLATE}

print("Turn 1: Nice to meet you, Zara!")
print("Messages in list: 4")
'''
        out = self.assert_fails(body, "missing Turn 2 label")
        self.assertIn("Turn 2:", out)

    def test_empty_output_fails(self):
        body = f'''"""Stub exercise for grader testing."""
if False:
{STEP4_SOURCE_BOILERPLATE}
'''
        self.assert_fails(body, "no output at all")

    def test_missing_append_source_check_still_fails(self):
        """Output tolerance must not bypass source checks."""
        # NB: this stub must not mention the appending call anywhere, not even
        # in a docstring — check_source() greps the raw file text.
        body = f'''"""Stub with correct output but history never accumulated."""
if False:
{CLIENT_SETUP_BOILERPLATE}
    client.messages.create(model="m", max_tokens=1, messages=[])

print("Turn 1: Nice to meet you, Zara!")
print("Turn 2: Your name is Zara.")
print("Messages in list: 4")
'''
        self.assert_fails(body, "missing .append() in source")


class TestNumericGraderStillExact(unittest.TestCase):
    """search_value() tolerates label spacing but not wrong numbers."""

    EXERCISE = "exercises/practice13_token_counting.py"

    STEP13_BOILERPLATE = CLIENT_SETUP_BOILERPLATE + '''
    client.messages.count_tokens(model="m", messages=[])
'''

    def stub(self, short_label, long_label, short_val, long_val) -> str:
        return f'''"""Stub exercise for grader testing."""
if False:
{self.STEP13_BOILERPLATE}

print("{short_label} {short_val}")
print("{long_label} {long_val}")
'''

    def test_tolerant_labels_with_valid_numbers_pass(self):
        code, out = run_grader(
            "check_step13.py",
            self.EXERCISE,
            self.stub("SHORT_TOKENS :", "long_tokens  :", 10, 500),
        )
        self.assertEqual(code, 0, f"tolerant labels + valid numbers should PASS:\n{out}")

    def test_inverted_numbers_fail(self):
        """long must exceed short — a real semantic relationship."""
        code, out = run_grader(
            "check_step13.py",
            self.EXERCISE,
            self.stub("short_tokens:", "long_tokens:", 500, 10),
        )
        self.assertNotEqual(code, 0, f"inverted token counts should FAIL:\n{out}")


# ---------------------------------------------------------------------------
# Step 22 — the capstone grader.
#
# Unlike steps 4/13 the capstone is graded on BEHAVIOUR plus source-level
# requirements, so the stubs below fake the printed transcript of a working
# tool round trip while carrying real (if unreachable) source lines to satisfy
# check_source(). Each failure test mutates exactly one requirement so a
# regression points at a single cause.
# ---------------------------------------------------------------------------

STEP22_SOURCE = CLIENT_SETUP_BOILERPLATE + '''
    TOOLS = [{"name": "calculate", "description": "math",
              "input_schema": {"type": "object",
                               "properties": {"expression": {"type": "string"}},
                               "required": ["expression"]}}]
    response = client.messages.create(model="claude-sonnet-5", max_tokens=100,
                                      tools=TOOLS, messages=messages)
    messages.append({"role": "assistant", "content": response.content})
    messages.append({"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": block.id, "content": "1056"}]})
    try:
        pass
    except anthropic.APIStatusError as exc:
        print(exc)
    for block in response.content:
        if block.type == "text":
            print(block.text)
'''

# The transcript a correct capstone run produces: a tool_use round trip that
# is followed by another call (end_turn), two answered questions, >= 4 turns.
STEP22_GOOD_TRANSCRIPT = [
    'print("capstone: start")',
    'print("stop_reason: tool_use")',
    'print("tool name: calculate")',
    'print("tool input: {\'expression\': \'127 * 8 + 40\'}")',
    'print("tool result: 1056")',
    'print("stop_reason: end_turn")',
    'print("assistant: 127 * 8 + 40 is 1056.")',
    'print("stop_reason: end_turn")',
    'print("assistant: Paris is the capital of France.")',
    'print("conversation turns: 6")',
    'print("capstone: done")',
]


def step22_stub(transcript=None, source=STEP22_SOURCE) -> str:
    """Build a stub capstone exercise from a list of print statements."""
    lines = STEP22_GOOD_TRANSCRIPT if transcript is None else transcript
    return '"""Stub capstone for grader testing — no network calls."""\n' \
           "if False:\n" + source + "\n" + "\n".join(lines) + "\n"


class TestStep22CapstoneGrader(unittest.TestCase):
    """The capstone grader passes a correct run and rejects each broken one."""

    EXERCISE = "exercises/practice22_capstone.py"

    def run_stub(self, **kwargs):
        return run_grader("check_step22.py", self.EXERCISE, step22_stub(**kwargs))

    def test_correct_capstone_passes(self):
        code, out = self.run_stub()
        self.assertEqual(code, 0, f"correct capstone should PASS but exited {code}:\n{out}")
        self.assertIn("PASS", out)

    def test_tolerant_label_formatting_passes(self):
        """Cosmetic spacing/case variance must not fail a correct capstone."""
        sloppy = [
            line.replace("capstone: start", "CAPSTONE : start")
                .replace("tool result:", "tool result :")
                .replace("conversation turns:", "Conversation Turns :")
            for line in STEP22_GOOD_TRANSCRIPT
        ]
        code, out = self.run_stub(transcript=sloppy)
        self.assertEqual(code, 0, f"tolerant label formatting should PASS:\n{out}")

    def test_missing_tool_use_fails(self):
        """R3: Claude answering from memory is not a tool round trip."""
        no_tool = [l.replace("stop_reason: tool_use", "stop_reason: end_turn")
                   for l in STEP22_GOOD_TRANSCRIPT]
        code, out = self.run_stub(transcript=no_tool)
        self.assertNotEqual(code, 0, f"missing tool_use should FAIL:\n{out}")

    def test_stopping_after_tool_result_fails(self):
        """R3: printing the tool result without calling back is incomplete."""
        no_end_turn = [l for l in STEP22_GOOD_TRANSCRIPT
                       if "end_turn" not in l]
        code, out = self.run_stub(transcript=no_end_turn)
        self.assertNotEqual(code, 0, f"no end_turn after tool_result should FAIL:\n{out}")

    def test_errored_tool_result_fails(self):
        """R2: a tool that only ever errors did no real work."""
        errored = [l.replace("tool result: 1056", "tool result: Error: bad input")
                   for l in STEP22_GOOD_TRANSCRIPT]
        code, out = self.run_stub(transcript=errored)
        self.assertNotEqual(code, 0, f"all-error tool results should FAIL:\n{out}")

    def test_single_assistant_turn_fails(self):
        """R4: the capstone requires more than one answered question."""
        one_answer = [l for l in STEP22_GOOD_TRANSCRIPT
                      if "Paris" not in l]
        code, out = self.run_stub(transcript=one_answer)
        self.assertNotEqual(code, 0, f"single assistant turn should FAIL:\n{out}")

    def test_too_few_conversation_turns_fails(self):
        """R4: history must actually accumulate."""
        few = [l.replace("conversation turns: 6", "conversation turns: 2")
               for l in STEP22_GOOD_TRANSCRIPT]
        code, out = self.run_stub(transcript=few)
        self.assertNotEqual(code, 0, f"too few turns should FAIL:\n{out}")

    def test_bare_except_fails(self):
        """R5: 'except Exception' swallows the learner's own bugs."""
        bare = STEP22_SOURCE.replace(
            "except anthropic.APIStatusError as exc:", "except Exception as exc:")
        code, out = self.run_stub(source=bare)
        self.assertNotEqual(code, 0, f"bare except should FAIL:\n{out}")

    def test_unsafe_content_indexing_fails(self):
        """R6: content[0].text is the anti-pattern the course warns against."""
        unsafe = STEP22_SOURCE.replace(
            'if block.type == "text":\n            print(block.text)',
            "print(response.content[0].text)")
        code, out = self.run_stub(source=unsafe)
        self.assertNotEqual(code, 0, f"content[0].text should FAIL:\n{out}")

    def test_anti_pattern_in_comment_still_passes(self):
        """code_only(): documenting the anti-pattern must not fail the learner."""
        commented = STEP22_SOURCE + "\n    # never write response.content[0].text\n"
        code, out = self.run_stub(source=commented)
        self.assertEqual(
            code, 0,
            f"content[0].text inside a COMMENT should still PASS:\n{out}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
