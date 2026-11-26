"""The navigation log holds; and a planted incomplete debrief is caught (C-025)."""
import unittest

from scripts.checks import navigation
from test.support import BROKEN, ROOT

HEAD = "# Log\n\nLast review: 59a8474 (2026-10-23)\n\n## Entries\n\n"
DEBRIEF = "### 2026-10-23 · a task · sonnet\n- **Task**: t\n- **Opened**: a, b\n- **Complaints**: none\n- **Suggestions**: none\n"


class TheRepository(unittest.TestCase):
    def test_the_real_log_holds(self) -> None:
        self.assertEqual(navigation.problems((ROOT / "docs" / "NAVIGATION-LOG.md").read_text()), [])

    def test_the_planted_break_is_caught(self) -> None:
        found = navigation.problems((BROKEN / "navigation" / "docs" / "NAVIGATION-LOG.md").read_text())
        self.assertEqual(found, ["debrief '2026-10-23 · a task · sonnet' has no Suggestions"])


class TheCheck(unittest.TestCase):
    def test_a_complete_debrief_holds(self) -> None:
        self.assertEqual(navigation.problems(HEAD + DEBRIEF), [])

    def test_a_missing_last_review_is_caught(self) -> None:
        self.assertEqual(navigation.problems("# Log\n\n## Entries\n"), ["not exactly one 'Last review: <commit> (…)' line"])

    def test_two_last_review_lines_are_caught(self) -> None:
        self.assertEqual(navigation.last_review(HEAD + "Last review: abcdef0 (x)\n"), "")

    def test_an_empty_field_is_caught(self) -> None:
        self.assertEqual(navigation.problems(HEAD + DEBRIEF.replace("- **Complaints**: none", "- **Complaints**:")), ["debrief '2026-10-23 · a task · sonnet' has no Complaints"])

    def test_the_field_description_above_entries_is_not_a_debrief(self) -> None:
        self.assertEqual(navigation.debriefs(HEAD + "- **Task**: what\n\n" + DEBRIEF)[0][0], DEBRIEF.splitlines()[0][4:])
