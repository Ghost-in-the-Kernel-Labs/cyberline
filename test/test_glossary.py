"""No governed document uses an enforced alias; and a planted one is caught (C-011, C-013)."""
import unittest
from pathlib import Path

from scripts.checks import glossary
from test.support import BROKEN, ROOT, scratch

TABLE = "| Term | Means | Not |\n| --- | --- | --- |\n| **horizon** | a window | period, `timeframe` |\n"


def plant(text: str, glossary_text: str = TABLE) -> Path:
    """A scratch root with the glossary given and a ROADMAP.md of the text given."""
    root = scratch()
    (root / "docs" / "GLOSSARY.md").write_text(glossary_text)
    (root / "docs" / "ROADMAP.md").write_text(text)
    return root


class TheRepository(unittest.TestCase):
    def test_the_real_documents_hold(self) -> None:
        self.assertEqual(glossary.problems(ROOT), [])

    def test_the_real_glossary_enforces_something(self) -> None:
        self.assertNotEqual(glossary.enforced_aliases((ROOT / "docs" / "GLOSSARY.md").read_text()), [])

    def test_the_planted_break_is_caught(self) -> None:
        self.assertEqual(glossary.problems(BROKEN / "glossary"), ["ROADMAP.md uses 'timeframe' 1 times"])


class TheCheck(unittest.TestCase):
    def test_only_backticked_aliases_are_enforced(self) -> None:
        self.assertEqual(glossary.enforced_aliases(TABLE), ["timeframe"])

    def test_a_planted_alias_is_caught(self) -> None:
        self.assertEqual(glossary.problems(plant("Each Timeframe is tested.\n")), ["ROADMAP.md uses 'timeframe' 1 times"])

    def test_an_unenforced_alias_passes(self) -> None:
        self.assertEqual(glossary.problems(plant("Each period is tested.\n")), [])

    def test_a_quoted_alias_is_a_mention_not_a_use(self) -> None:
        self.assertEqual(glossary.problems(plant("Never write `timeframe`.\n```\ntimeframe = 3\n```\n")), [])

    def test_the_word_alone_in_double_quotes_is_named_not_used(self) -> None:
        self.assertEqual(glossary.uses('never "nn", never \u201cnn\u201d; an nn, "an nn"', "nn"), 2)

    def test_an_alias_in_capitals_matches_only_in_capitals(self) -> None:
        self.assertEqual(glossary.uses("an NN and HAR-nn", "NN"), 1)

    def test_a_word_containing_the_alias_is_not_it(self) -> None:
        self.assertEqual(glossary.problems(plant("timeframes and subtimeframe\n")), [])

    def test_root_documents_are_caught_and_the_glossary_is_not(self) -> None:
        root = plant("Each timeframe.\n", TABLE + "\nNever write timeframe.\n")
        (root / "README.md").write_text("A timeframe and a timeframe.\n")
        self.assertEqual(glossary.problems(root), ["README.md uses 'timeframe' 2 times", "ROADMAP.md uses 'timeframe' 1 times"])

    def test_subfolders_of_docs_are_governed(self) -> None:
        root = plant("fine\n")
        (root / "docs" / "when").mkdir()
        (root / "docs" / "when" / "x.md").write_text("a timeframe\n")
        self.assertEqual(glossary.problems(root), ["x.md uses 'timeframe' 1 times"])

    def test_a_not_governed_document_is_exempt(self) -> None:
        exempt = "Not governed: `docs/ROADMAP.md`.\n\n" + TABLE
        self.assertEqual(glossary.problems(plant("a timeframe\n", exempt)), [])
        self.assertEqual(glossary.not_governed(exempt), ["docs/ROADMAP.md"])

    def test_a_lowercase_alias_matches_any_case(self) -> None:
        self.assertEqual(glossary.uses("Timeframe TIMEFRAME timeframe", "timeframe"), 3)
