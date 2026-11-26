"""A comment says what and gives no reason in its own words; a planted reason is caught (C-042)."""
import unittest

from scripts.checks import comments
from test.support import BROKEN, ROOT, scratch



class TheRepository(unittest.TestCase):
    def test_no_comment_gives_a_reason(self) -> None:
        self.assertEqual(comments.problems(ROOT), [])

    def test_the_planted_break_is_caught(self) -> None:
        tail = "; say what, and refer to a decision by id (C-042)"
        self.assertEqual(comments.problems(BROKEN / "comments"), [
            "scripts/x.py:4 gives a reason in a comment (because)" + tail,
            "scripts/x.py:6 gives a reason in a comment (J-080)" + tail,
            "scripts/y.sh:2 gives a reason in a comment (2026-11-26)" + tail,
            "stacks/z.mjs:3 gives a reason in a comment (since, G-290)" + tail])


class TheCheck(unittest.TestCase):
    def test_a_reason_word_a_date_and_a_record_id_are_named_once_each(self) -> None:
        self.assertEqual(comments.markers("Sorted, because J-080 said so on 2026-11-18, because of J-080.", ["C"]), ["because", "2026-11-18", "J-080"])

    def test_a_decision_an_invariant_a_range_of_ids_and_the_heading_pass(self) -> None:
        self.assertEqual(comments.markers("C-042 and AGT-05 hold it; docs/journal/J-000-099.md; the Why column; SHA-256.", ["C"]), [])

    def test_a_decision_of_another_log_is_a_record(self) -> None:
        self.assertEqual(comments.markers("As P-002 says.", ["C"]), ["P-002"])
        self.assertEqual(comments.markers("As P-002 says.", ["C", "P"]), [])

    def test_text_between_quotes_or_backticks_is_a_value(self) -> None:
        self.assertEqual(comments.markers('gives "J-001 because" and `since 2026-11-18`', ["C"]), [])

    def test_python_docstrings_and_hash_comments_by_line(self) -> None:
        source = "\"\"\"m\"\"\"\n\n\ndef f() -> int:\n    \"\"\"d\"\"\"\n    # one\n    # two\n    return 1  # three\n"
        self.assertEqual(comments.python_comments(source), [(1, "m"), (4, "d"), (6, "one two three")])
        self.assertEqual(comments.python_comments("def f(:\n"), [])

    def test_a_hash_file_skips_its_first_line_and_code(self) -> None:
        self.assertEqual(comments.hash_comments("#!/bin/sh\n# a\n# b\nx=1 # c\n# d\n"), [(2, "a b"), (5, "d")])

    def test_a_slash_file_reads_line_comments_and_blocks(self) -> None:
        self.assertEqual(comments.slash_comments("// a\nx();\n/* b\n * c */\ny(); // d\n/* e */\n"), [(1, "a"), (3, "b c"), (6, "e")])

    def test_runs_join_consecutive_lines(self) -> None:
        self.assertEqual(comments.runs([(3, "a"), (4, "b"), (9, "c")]), [(3, "a b"), (9, "c")])

    def test_only_code_under_the_folders_is_read_and_fixtures_are_not(self) -> None:
        root = scratch()
        for place in ("scripts/a.sh", "src/b.ts", "test/c.py", "test/fixtures/d.sh", "docs/e.sh", "f.sh", "scripts/g.json"):
            (root / place).parent.mkdir(parents=True, exist_ok=True)
            (root / place).write_text("# kept because\n" if not place.endswith((".ts", ".py")) else "// kept because\n" if place.endswith(".ts") else "# kept because\n")
        self.assertEqual([problem.split(":")[0] for problem in comments.problems(root)], ["scripts/a.sh", "src/b.ts", "test/c.py"])
