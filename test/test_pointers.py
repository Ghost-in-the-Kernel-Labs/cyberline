"""Every pointer in the routing documents resolves or is promised; and a planted dangling one is caught (C-021)."""
import unittest

from scripts.checks import pointers
from test.support import BROKEN, ROOT, scratch


class TheRepository(unittest.TestCase):
    def test_the_real_pointers_hold(self) -> None:
        self.assertEqual(pointers.problems(ROOT), [])

    def test_the_planted_break_is_caught(self) -> None:
        self.assertEqual(pointers.problems(BROKEN / "pointers"), ["docs/when/x.md points at docs/gone.md, which does not exist and no open TODO item promises"])


class TheCheck(unittest.TestCase):
    def test_a_pointer_to_an_existing_file_holds(self) -> None:
        root = scratch()
        (root / "docs" / "when").mkdir()
        (root / "docs" / "when" / "x.md").write_text("read `docs/y.md`\n")
        (root / "docs" / "y.md").write_text("y\n")
        self.assertEqual(pointers.problems(root), [])

    def test_a_promised_pointer_is_allowed_until_the_item_is_done(self) -> None:
        root = scratch()
        (root / "docs" / "when").mkdir()
        (root / "docs" / "when" / "x.md").write_text("run `scripts/gate.sh`\n")
        (root / "TODO.md").write_text("### 0.1 The gate\n\nCheck: `scripts/gate.sh` ends with a verdict.\n")
        self.assertEqual(pointers.problems(root), [])
        (root / "TODO.md").write_text("")
        self.assertEqual(pointers.problems(root), ["docs/when/x.md points at scripts/gate.sh, which does not exist and no open TODO item promises"])

    def test_claude_md_is_governed_when_present(self) -> None:
        root = scratch()
        (root / "CLAUDE.md").write_text("| a | `docs/nope.md` |\n")
        self.assertEqual(pointers.problems(root), ["CLAUDE.md points at docs/nope.md, which does not exist and no open TODO item promises"])

    def test_a_backticked_word_that_is_not_a_path_is_ignored(self) -> None:
        self.assertEqual(pointers.pointed("`tune-up:` and `scripts/commit.sh` and `python3 -I x.py`"), ["scripts/commit.sh"])
