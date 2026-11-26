"""CLAUDE.md holds its shape, its ceiling, its five supply-chain triggers and its canary line; docs/SUPPLY-CHAIN.md holds the thirteen rules with the six credential bullets (C-037) verbatim; and planted breaks are caught (C-020, C-021, C-022, C-034, C-036, C-041)."""
import unittest

from scripts.checks import claude_md
from test.support import BROKEN, ROOT

RULES = "\n".join(claude_md.TRIGGERS) + "\n\n" + claude_md.CANARY + "\n"
VERBATIM = "# S\n\n## The rules, verbatim\n\n" + "\n".join(claude_md.BINDING_RULES) + "\n"
GOOD = "# X\n\n## Where to start\n\n| Task | Start here |\n| --- | --- |\n| a | `docs/a.md` |\n\n## When X happens, read Y\n\n- x: `docs/when/x.md`\n\n" + RULES


class TheRepository(unittest.TestCase):
    def test_the_real_file_holds(self) -> None:
        self.assertEqual(claude_md.problems((ROOT / "CLAUDE.md").read_text()), [])

    def test_the_real_file_has_headroom(self) -> None:
        self.assertLess(claude_md.words((ROOT / "CLAUDE.md").read_text()), claude_md.WORD_CEILING)

    def test_the_real_rules_are_verbatim(self) -> None:
        self.assertEqual(claude_md.rules_problems((ROOT / "docs" / "SUPPLY-CHAIN.md").read_text()), [])

    def test_the_planted_break_is_caught(self) -> None:
        found = claude_md.problems((BROKEN / "claude_md" / "CLAUDE.md").read_text())
        self.assertEqual(found, ["row 'wide' opens 6 files, more than 5", "supply-chain trigger missing or reworded: '- You add, update, remove or install a dependency,'…", "supply-chain trigger missing or reworded: '- You handle a key, token, password, credential fi'…", "the Context Canary line is missing or reworded"])

    def test_the_planted_rules_break_is_caught(self) -> None:
        found = claude_md.rules_problems((BROKEN / "claude_md" / "SUPPLY-CHAIN.md").read_text())
        self.assertEqual(found, ["binding rule missing or reworded: '- Never add or remove a dependency without a one-l'…", "binding rule missing or reworded: '- A secret found in the tree, the history, a log o'…"])


class TheCheck(unittest.TestCase):
    def test_a_good_file_holds(self) -> None:
        self.assertEqual(claude_md.problems(GOOD), [])

    def test_over_the_ceiling_is_caught(self) -> None:
        self.assertIn("words, over 1200", claude_md.problems(GOOD + "word " * 1200)[0])

    def test_a_missing_when_section_is_caught(self) -> None:
        self.assertEqual(claude_md.problems(GOOD.replace("## When X happens, read Y", "## Later")), ["CLAUDE.md has no 'When X happens, read Y' section"])

    def test_a_reworded_trigger_is_caught(self) -> None:
        self.assertEqual(len(claude_md.problems(GOOD.replace("do not revoke tokens.", "revoke tokens."))), 1)
        self.assertEqual(len(claude_md.TRIGGERS), 5)

    def test_a_reworded_binding_rule_is_caught(self) -> None:
        self.assertEqual(claude_md.rules_problems(VERBATIM), [])
        self.assertEqual(len(claude_md.rules_problems(VERBATIM.replace("Do not revoke tokens.", "Revoke tokens."))), 1)

    def test_the_six_credential_bullets_are_held(self) -> None:
        self.assertEqual(len(claude_md.BINDING_RULES), 13)
        for phrase in ("Never dump the environment", "a dummy value, never a real one", "never read into context unless Ghost asks",
                       "report its file and line only (never the value)", "assembled at runtime from fragments", "matches a key pattern"):
            with self.subTest(phrase=phrase):
                rule = next(r for r in claude_md.BINDING_RULES if phrase in r)
                self.assertEqual(len(claude_md.rules_problems(VERBATIM.replace(rule, ""))), 1)

    def test_a_missing_or_reworded_canary_is_caught(self) -> None:
        self.assertEqual(claude_md.problems(GOOD.replace(claude_md.CANARY, "")), ["the Context Canary line is missing or reworded"])
        self.assertEqual(claude_md.problems(GOOD.replace("Context Canary", "Canary")), ["the Context Canary line is missing or reworded"])

    def test_a_row_with_six_files_is_caught(self) -> None:
        wide = GOOD.replace("| a | `docs/a.md` |", "| a | " + " ".join(f"`docs/{i}.md`" for i in range(6)) + " |")
        self.assertEqual(claude_md.problems(wide), ["row 'a' opens 6 files, more than 5"])
