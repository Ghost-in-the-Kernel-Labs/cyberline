"""Findings and escalations hold; and planted breaks in each are caught (C-014, C-028)."""
import unittest

from scripts.checks import registers
from test.support import BROKEN, ROOT

FINDINGS = "| Id | Finding | Evidence | Qualifies | Status |\n| --- | --- | --- | --- | --- |\n"
ESCALATIONS = "| Date | Task | Kind | Route taken | What the next grade found | Open |\n| --- | --- | --- | --- | --- | --- |\n"


def finding(rid: str, status: str = "open") -> str:
    """One findings row: finding("F-001") gives "| F-001 | f | e | q | open |"."""
    return f"| {rid} | f | e | q | {status} |\n"


def escalation(kind: str, open_: str = "yes") -> str:
    """One escalations row of the kind given, open unless told otherwise."""
    return f"| 2026-10-23 | t | {kind} | r | w | {open_} |\n"


class TheRepository(unittest.TestCase):
    def test_the_real_registers_hold(self) -> None:
        docs = ROOT / "docs"
        self.assertEqual(registers.finding_problems((docs / "FINDINGS.md").read_text()), [])
        self.assertEqual(registers.escalation_problems((docs / "ESCALATIONS.md").read_text(), (docs / "HANDOFF.md").read_text()), [])

    def test_the_planted_breaks_are_caught(self) -> None:
        docs = BROKEN / "registers" / "docs"
        self.assertEqual(registers.finding_problems((docs / "FINDINGS.md").read_text()), ["finding 2 is F-003, expected F-002"])
        found = registers.escalation_problems((docs / "ESCALATIONS.md").read_text(), "")
        self.assertEqual(found, ["escalation on d has kind 'conflict', not one of 7", "3 open escalations of kind 'not-read' and no For Ghost item names it"])


class TheCheck(unittest.TestCase):
    def test_findings_in_order_hold(self) -> None:
        self.assertEqual(registers.finding_problems(FINDINGS + finding("F-001") + finding("F-002", "resolved 2026-10-23 by Ghost")), [])

    def test_a_bad_finding_status_is_caught(self) -> None:
        self.assertEqual(registers.finding_problems(FINDINGS + finding("F-001", "maybe")), ["F-001 has status 'maybe', not open or resolved"])

    def test_an_empty_cell_is_caught(self) -> None:
        self.assertEqual(registers.finding_problems(FINDINGS + "| F-001 | f |  | q | open |\n"), ["F-001 has an empty cell"])

    def test_an_unknown_kind_is_caught(self) -> None:
        self.assertEqual(registers.escalation_problems(ESCALATIONS + escalation("vibes"), ""), ["escalation on 2026-10-23 has kind 'vibes', not one of 7"])

    def test_no_advisor_is_a_kind_and_conflict_is_not(self) -> None:
        self.assertEqual(registers.escalation_problems(ESCALATIONS + escalation("no-advisor"), ""), [])
        self.assertEqual(registers.escalation_problems(ESCALATIONS + escalation("conflict", "no"), ""), ["escalation on 2026-10-23 has kind 'conflict', not one of 7"])

    def test_two_open_of_a_kind_are_fine_and_three_are_raised(self) -> None:
        two = ESCALATIONS + escalation("hard") * 2
        self.assertEqual(registers.escalation_problems(two, ""), [])
        three = two + escalation("hard")
        self.assertEqual(registers.escalation_problems(three, ""), ["3 open escalations of kind 'hard' and no For Ghost item names it"])
        self.assertEqual(registers.escalation_problems(three, "## For Ghost\n\n1. hard: routing pass\n"), [])

    def test_closed_rows_do_not_count(self) -> None:
        self.assertEqual(registers.escalation_problems(ESCALATIONS + escalation("hard", "no") * 3, ""), [])
