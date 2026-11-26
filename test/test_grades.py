"""No instruction names a model; only the grade map does; and a planted model name is caught (C-036)."""
import unittest

from scripts.checks import grades
from test.support import BROKEN, ROOT, scratch


class TheRepository(unittest.TestCase):
    def test_no_instruction_names_a_model(self) -> None:
        self.assertEqual(grades.problems(ROOT), [])

    def test_the_map_names_every_grade_and_a_floor(self) -> None:
        text = (ROOT / grades.MAP).read_text()
        for row in ("| small | Claude Haiku |", "| mid | Claude Sonnet |", "| strong | Claude Opus |", "| ruling | Claude Fable |"):
            self.assertIn(row, text)
        self.assertRegex(text, r"(?m)^Floor: (small|mid|strong)$")

    def test_the_planted_break_is_caught(self) -> None:
        self.assertEqual(grades.problems(BROKEN / "grades"), ["docs/when/handoff.md:3 names Sonnet; name the grade (docs/when/grades.md)"])


class TheCheck(unittest.TestCase):
    def test_a_name_in_any_case_and_a_whole_word_only(self) -> None:
        self.assertEqual(grades.named("an OPUS\nsonnets and opuses\nhaiku."), [(1, "OPUS"), (3, "haiku")])

    def test_a_code_span_or_a_fenced_block_is_a_value(self) -> None:
        self.assertEqual(grades.named("`model: \"opus\"` and ``Fable``\n```\nSonnet\n```\nOpus"), [(5, "Opus")])

    def test_every_governed_place_is_read_and_a_record_is_not(self) -> None:
        root = scratch()
        for place in ("CLAUDE.md", "README.md", "docs/AGENT.md", "docs/HANDOFF.md", "docs/paths/p.md", "scripts/stamp_templates/T.md",
                      "theGhost.md", "docs/journal/J-000-099.md", "docs/NAVIGATION-LOG.md", "docs/LESSONS-2026-11.md"):
            (root / place).parent.mkdir(parents=True, exist_ok=True)
            (root / place).write_text("Ask Opus.\n")
        found = [problem.split(":")[0] for problem in grades.problems(root)]
        self.assertEqual(found, ["CLAUDE.md", "README.md", "docs/AGENT.md", "docs/HANDOFF.md", "docs/paths/p.md", "scripts/stamp_templates/T.md"])

    def test_the_map_itself_is_not_read(self) -> None:
        root = scratch()
        (root / "docs" / "when").mkdir()
        (root / "docs" / "when" / "grades.md").write_text("| mid | Claude Sonnet |\n")
        self.assertEqual(grades.problems(root), [])
