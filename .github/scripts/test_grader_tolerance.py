#!/usr/bin/env python3
"""Tests for grader matching tolerance (_report.normalise / contains).

Two halves:

  * Unit tests pin the exact tolerance contract: formatting variance is
    forgiven, semantic variance is not.
  * An end-to-end stub test runs a real grader (check_step1.py) as a
    subprocess against a fake exercise, proving a differently-cased and
    differently-spaced but semantically correct output PASSES, and that a
    semantically wrong output still FAILS with exit code 1.

check_step1 is used for the end-to-end half because it is the only grader
that neither requires ICA_API_KEY nor makes a network call, so this suite
runs offline in CI.

Run:  python3 -m unittest discover -s .github/scripts -p 'test_*.py'
  or:  python3 -m pytest .github/scripts/test_grader_tolerance.py
"""
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent.parent

sys.path.insert(0, str(SCRIPTS_DIR))
from _report import contains, find_values, flexible_regex, normalise, search_value  # noqa: E402


class TestNormalise(unittest.TestCase):
    def test_casefolds(self):
        self.assertEqual(normalise("Turn 1:"), normalise("TURN 1:"))

    def test_collapses_whitespace_runs(self):
        self.assertEqual(normalise("Turn  1"), normalise("Turn\t1"))

    def test_strips_space_around_colons(self):
        self.assertEqual(normalise("Turn 1 : x"), "turn 1:x")
        self.assertEqual(normalise("Turn 1:x"), "turn 1:x")

    def test_handles_none_and_empty(self):
        self.assertEqual(normalise(None), "")
        self.assertEqual(normalise("   \n "), "")


class TestContainsAcceptsFormattingVariance(unittest.TestCase):
    """Same meaning, different keyboard \u2014 must pass."""

    VARIANTS = [
        "Turn 1: hello",     # canonical
        "turn 1: hello",     # lowercased
        "TURN 1: HELLO",     # shouted
        "Turn 1 : hello",    # space before colon
        "Turn 1:hello",      # no space after colon
        "Turn  1:  hello",   # doubled spaces
        "Turn\t1:\thello",   # tabs
        "  Turn 1: hello  ",  # leading/trailing padding
    ]

    def test_all_variants_match_canonical_needle(self):
        for out in self.VARIANTS:
            with self.subTest(out=out):
                self.assertTrue(contains(out, "Turn 1:"), out)

    def test_variant_needles_match_canonical_output(self):
        for needle in ("turn 1 :", "TURN  1:", "Turn 1:"):
            with self.subTest(needle=needle):
                self.assertTrue(contains("Turn 1: hello", needle))

    def test_needle_spanning_a_line_break_in_output(self):
        # A wrapped print still means the same thing.
        self.assertTrue(contains("role:\nassistant", "role: assistant"))

    def test_real_grader_needles(self):
        cases = [
            ("STOP_REASON : End_Turn", "stop_reason: end_turn"),
            ("Age Type:INT", "age type: int"),
            ("has thinking block :   true", "has thinking block: True"),
            ("Client Type : Anthropic", "Client type: Anthropic"),
            ("PDF Created:  true", "pdf created: True"),
            ("file_id : file_abc123", "file_id: file_"),
        ]
        for out, needle in cases:
            with self.subTest(needle=needle):
                self.assertTrue(contains(out, needle))


class TestContainsRejectsSemanticVariance(unittest.TestCase):
    """Different meaning \u2014 must still fail. This is the guard rail."""

    def test_wrong_word(self):
        self.assertFalse(contains("stop_reason: max_tokens", "stop_reason: end_turn"))

    def test_wrong_boolean(self):
        self.assertFalse(contains("has thinking block: False", "has thinking block: True"))

    def test_wrong_type(self):
        self.assertFalse(contains("age type: str", "age type: int"))

    def test_missing_label_entirely(self):
        self.assertFalse(contains("hello world", "Turn 1:"))

    def test_wrong_number(self):
        self.assertFalse(contains("answer: 917", "918"))

    def test_number_must_not_match_a_longer_number(self):
        # '918' is not present in 9187 / 1918 / 918.5 \u2014 those are other numbers.
        for out in ("answer: 9187", "answer: 1918", "answer: 918.5", "answer: 0.9182"):
            with self.subTest(out=out):
                self.assertFalse(contains(out, "918"), out)

    def test_number_at_a_real_boundary_still_matches(self):
        for out in ("answer: 918", "answer is 918.", "(918)", "918, exactly", "x=918\n"):
            with self.subTest(out=out):
                self.assertTrue(contains(out, "918"), out)

    def test_decimal_value_is_not_matched_by_a_longer_decimal(self):
        self.assertTrue(contains("mean: 5.5", "5.5"))
        self.assertFalse(contains("mean: 5.55", "5.5"))
        self.assertFalse(contains("mean: 15.5", "5.5"))

    def test_secret_code_must_be_exact(self):
        self.assertTrue(contains("answer: the code is 4471", "4471"))
        self.assertFalse(contains("answer: the code is 44710", "4471"))

    def test_word_order_matters(self):
        self.assertFalse(contains("1 turn:", "Turn 1:"))


class TestValueExtraction(unittest.TestCase):
    def test_flexible_regex_matches_spacing_variants(self):
        pattern = flexible_regex("chars streamed:")
        for out in ("chars streamed: 42", "Chars  Streamed :42", "chars\tstreamed:  42"):
            with self.subTest(out=out):
                match = search_value(out, "chars streamed:")
                self.assertIsNotNone(match, out)
                self.assertEqual(match.group(1), "42")
        self.assertIn(r"\s*:\s*", pattern)

    def test_value_comparisons_still_apply(self):
        # Tolerance is about finding the number, not about accepting a wrong one.
        match = search_value("chars streamed: 0", "chars streamed:")
        self.assertIsNotNone(match)
        self.assertEqual(int(match.group(1)), 0)

    def test_find_values_collects_every_occurrence(self):
        stdout = "Model: alpha\nmodel :beta\nMODEL:  gamma\n"
        self.assertEqual(find_values(stdout, "model:"), ["alpha", "beta", "gamma"])

    def test_id_prefix_check_is_tolerant(self):
        self.assertIsNotNone(search_value("ID : msg_01abc", "id:", r"(msg_\S+)"))


# --------------------------------------------------------------------------
# End-to-end stub run of a real grader
# --------------------------------------------------------------------------

# Text the grader statically requires in the learner's source. Included so the
# stub gets past check_source and reaches the stdout assertions under test.
_STUB_PREAMBLE = (
    "from dotenv import load_dotenv\n"
    "load_dotenv()\n"
    "import os\n"
    'key = os.environ.get("ICA_API_KEY")\n'
    '_ = "base_url=https://example.invalid"\n'
)


def run_step1_grader(prints: str):
    """Write a stub exercises/practice1.py that prints `prints`, grade it."""
    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        (workdir / "exercises").mkdir()
        (workdir / "exercises" / "practice1.py").write_text(_STUB_PREAMBLE + prints)
        return subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "check_step1.py")],
            cwd=workdir,
            capture_output=True,
            text=True,
            timeout=120,
        )


class TestGraderEndToEnd(unittest.TestCase):
    """The proof that matters: run the real grader on stub output."""

    def test_canonical_output_passes(self):
        result = run_step1_grader(
            'print("SDK version:", "0.125.0")\n'
            'print("Client type:", "Anthropic")\n'
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_differently_cased_and_spaced_output_passes(self):
        """Semantically identical, formatted differently \u2014 the whole point."""
        result = run_step1_grader(
            'print("sdk  version :", "0.125.0")\n'
            'print("CLIENT TYPE:Anthropic")\n'
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_semantically_wrong_output_still_fails(self):
        """Right shape, wrong value \u2014 must not be let through."""
        result = run_step1_grader(
            'print("SDK version:", "0.125.0")\n'
            'print("Client type:", "AsyncAnthropic")\n'  # wrong class
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("FAIL", result.stdout)

    def test_missing_label_still_fails(self):
        result = run_step1_grader('print("hello world")\n')
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("FAIL", result.stdout)


class TestNoGraderBypassesTheHelpers(unittest.TestCase):
    """Guard against a raw `"x" in stdout` check creeping back in.

    Every stdout assertion must go through contains()/require_*/search_value,
    otherwise that one grader silently keeps the old brittle behaviour.
    """

    BYPASS_PATTERNS = [
        re.compile(r"\bin stdout\b"),          # "x" in stdout / not in stdout
        re.compile(r"stdout\.lower\(\)"),      # ad-hoc case folding
        re.compile(r"re\.(search|findall|match)\(.*stdout"),  # hand-rolled grep
    ]

    @staticmethod
    def _code_lines(path: Path):
        """Yield (lineno, code) with comments and string literals blanked out.

        Hints and failure messages are prose that legitimately says things like
        "expected ... in stdout"; tokenize lets us lint only executable code.
        """
        import io
        import token
        import tokenize

        lines = path.read_text().splitlines()
        blanked = list(lines)
        readline = io.StringIO("\n".join(lines)).readline
        # Python 3.12+ splits f-strings into FSTRING_* tokens instead of STRING.
        string_types = {token.STRING, tokenize.COMMENT}
        for name in ("FSTRING_START", "FSTRING_MIDDLE", "FSTRING_END"):
            if hasattr(token, name):
                string_types.add(getattr(token, name))
        for tok in tokenize.generate_tokens(readline):
            if tok.type in string_types:
                (srow, scol), (erow, ecol) = tok.start, tok.end
                for row in range(srow, erow + 1):
                    line = blanked[row - 1]
                    start = scol if row == srow else 0
                    end = ecol if row == erow else len(line)
                    blanked[row - 1] = line[:start] + " " * (end - start) + line[end:]
        return list(enumerate(blanked, 1))

    def test_no_raw_stdout_matching(self):
        offenders = []
        for grader in sorted(SCRIPTS_DIR.glob("check_step*.py")):
            for lineno, code in self._code_lines(grader):
                for pattern in self.BYPASS_PATTERNS:
                    if pattern.search(code):
                        offenders.append(f"{grader.name}:{lineno}: {code.strip()}")
        self.assertEqual(offenders, [], "raw stdout matching found:\n" + "\n".join(offenders))


class TestAllGradersCompile(unittest.TestCase):
    def test_py_compile_every_grader(self):
        import py_compile

        graders = sorted(SCRIPTS_DIR.glob("check_step*.py")) + [SCRIPTS_DIR / "_report.py"]
        self.assertGreaterEqual(len(graders), 22)
        for grader in graders:
            with self.subTest(grader=grader.name):
                py_compile.compile(str(grader), doraise=True, cfile=None)


if __name__ == "__main__":
    unittest.main(verbosity=2)
