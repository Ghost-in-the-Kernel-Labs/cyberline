"""TODO.md holds as a chain; and each way it can break, planted, is caught (C-016, C-024)."""
import unittest

from scripts.checks import todo
from test.support import BROKEN, ROOT

CHAIN = "## Phase 0: x\n\n### 0.1 A step\n\nCheck: c\n\n### 0.2 Tune-up pass 0\n\nCheck: c\n\n## Phase 1: y\n\n### 1.1 Tune-up pass 1\n\nCheck: c\n"


class TheRepository(unittest.TestCase):
    def test_the_real_chain_holds(self) -> None:
        self.assertEqual(todo.problems((ROOT / "TODO.md").read_text(), (ROOT / "docs" / "DONE.md").read_text()), [])

    def test_the_planted_break_is_caught(self) -> None:
        found = todo.problems((BROKEN / "todo" / "TODO.md").read_text(), (BROKEN / "todo" / "docs" / "DONE.md").read_text())
        self.assertEqual(found, [
            "Phase 0's last item is 'A step', not a tune-up pass",
            "Phase 1 is reopened with 4 new items, more than 3; close it by a \"Tune-up pass\", not 'Tune-up commit'",
            "Phase 2 is reopened (DONE.md holds its tune-up pass); end it with a \"Tune-up commit\" or \"Tune-up pass\" item: its last item is 'New one'",
            "item 3.1 has a Waits on: line; move it to \"## Phase W: waiting on Ghost\" with a Moved: line",
            "item 3.4 is in the waiting phase without a Waits on: line",
            "item 3.5 is in the waiting phase without \"Moved: from Phase 3\"",
            "item 3.6 is in the waiting phase without \"Moved: from Phase 3\"",
            "item 3.7 waits on environment without its shape: `Waits on: environment (<what>)`",
            "item 3.8 waits on reference without its shape: `Waits on: reference (<what>)`",
            "the waiting phase is not the last phase: a numbered phase follows it",
            "waiting items out of order: ['3.4', '3.5', '3.6', '3.3', '3.7', '3.8']",
            "0.1 is in both TODO.md and DONE.md", "0.9 appears 2 times in DONE.md"])


class TheCheck(unittest.TestCase):
    def test_a_clean_chain_holds(self) -> None:
        self.assertEqual(todo.problems(CHAIN, ""), [])

    def test_items_out_of_order_are_caught(self) -> None:
        swapped = CHAIN.replace("### 0.1 A step", "### 0.3 A step")
        self.assertEqual(todo.problems(swapped, ""), ["items out of order: ['0.3', '0.2', '1.1']"])

    def test_an_item_under_the_wrong_phase_is_caught(self) -> None:
        self.assertIn("item 1.1 is not under Phase 1", todo.problems(CHAIN.replace("## Phase 1: y\n\n", ""), ""))

    def test_a_first_item_without_a_check_is_caught(self) -> None:
        self.assertEqual(todo.problems(CHAIN.replace("### 0.1 A step\n\nCheck: c\n", "### 0.1 A step\n"), ""), ["the first open item, 0.1, has no Check: line"])

    def test_a_phase_without_a_tune_up_is_caught(self) -> None:
        self.assertEqual(todo.problems(CHAIN.replace("### 0.2 Tune-up pass 0\n\nCheck: c\n\n", ""), ""), ["Phase 0's last item is 'A step', not a tune-up pass"])

    def test_a_tune_up_not_last_is_caught(self) -> None:
        moved = CHAIN.replace("### 0.1 A step", "### 0.1 Tune-up pass 0").replace("### 0.2 Tune-up pass 0", "### 0.2 A step")
        self.assertEqual(todo.problems(moved, ""), ["Phase 0's last item is 'A step', not a tune-up pass"])

    def test_an_item_both_open_and_done_is_caught(self) -> None:
        self.assertEqual(todo.problems(CHAIN, "### 0.1 A step\n"), ["0.1 is in both TODO.md and DONE.md"])

    def test_a_heading_twice_in_done_is_caught(self) -> None:
        done = "## Phase 0: x\n\n### 0.0 Before\n\n### 0.0 Before\n\nDone.\n\n### 0.0 Before\n"
        self.assertEqual(todo.problems(CHAIN, done), ["0.0 appears 3 times in DONE.md"])
        self.assertEqual(todo.problems(CHAIN, "### 0.0 Before\n\n### 1.0 Other\n"), [])


# Phase 1 closed by its pass (1.1), so a Phase 1 heading in TODO.md is a reopened phase (3.11).
CLOSED = "## Phase 1: y\n\n### 1.1 Tune-up pass 1\n\nDone.\n"
REOPENED = "## Phase 1: y\n\n### 1.2 First\n\nCheck: c\n\n### 1.3 Second\n\n### 1.4 Third\n\n### 1.5 Tune-up commit\n"


class TheReopenedPhase(unittest.TestCase):
    """3.11: a reopened phase of at most three items closes by a tune-up commit; a fourth needs a pass."""

    def test_three_new_items_close_by_a_tune_up_commit(self) -> None:
        self.assertEqual(todo.problems(REOPENED, CLOSED), [])

    def test_a_tune_up_commit_closes_only_a_reopened_phase(self) -> None:
        self.assertEqual(todo.problems(REOPENED, ""), ["Phase 1's last item is 'Tune-up commit', not a tune-up pass"])

    def test_a_fourth_item_needs_a_pass(self) -> None:
        four = REOPENED.replace("### 1.5 Tune-up commit", "### 1.5 Fourth\n\n### 1.6 Tune-up commit")
        self.assertEqual(todo.problems(four, CLOSED), ["Phase 1 is reopened with 4 new items, more than 3; close it by a \"Tune-up pass\", not 'Tune-up commit'"])
        self.assertEqual(todo.problems(four.replace("Tune-up commit", "Tune-up pass 1, second close"), CLOSED), [])

    def test_items_done_since_the_reopening_count(self) -> None:
        done = CLOSED + "\n### 1.2 First\n\nDone.\n"
        rest = REOPENED.replace("### 1.2 First\n\nCheck: c\n\n### 1.3 Second", "### 1.3 Second\n\nCheck: c").replace("### 1.5 Tune-up commit", "### 1.5 Fourth\n\n### 1.6 Tune-up commit")
        self.assertEqual(todo.problems(rest, done), ["Phase 1 is reopened with 4 new items, more than 3; close it by a \"Tune-up pass\", not 'Tune-up commit'"])

    def test_a_reopened_phase_must_end_with_a_closer(self) -> None:
        self.assertEqual(todo.problems(REOPENED.replace("### 1.5 Tune-up commit\n", ""), CLOSED), [
            "Phase 1 is reopened (DONE.md holds its tune-up pass); end it with a \"Tune-up commit\" or \"Tune-up pass\" item: its last item is 'Third'"])

    def test_a_closed_reopening_starts_the_count_again(self) -> None:
        done = CLOSED + "\n### 1.2 a\n\n### 1.3 b\n\n### 1.4 Tune-up commit\n"
        later = REOPENED.replace("1.2 First", "1.5 First").replace("1.3 Second", "1.6 Second").replace("1.4 Third", "1.7 Third").replace("1.5 Tune-up commit", "1.8 Tune-up commit")
        self.assertEqual(todo.problems(later, done), [])


# Phase 1 keeps 1.1 and its pass; 1.2 waits and has moved to the waiting phase, its number kept (3.12).
WAITS = ("## Phase 0: x\n\n### 0.1 A step\n\nCheck: c\n\n### 0.3 Tune-up pass 0\n\n## Phase 1: y\n\n### 1.1 Now\n\n"
         "### 1.3 Tune-up pass 1\n\n## Phase W: waiting on Ghost\n\n### 0.2 Later\n\nWaits on: Ghost's ruling\n\n"
         "Moved: from Phase 0\n\n### 1.2 Approval\n\nWaits on: counsel\n\nMoved: from Phase 1\n")


class TheWaitingPhase(unittest.TestCase):
    """3.12: an item that waits moves to the last phase with Waits on: and Moved:; that phase needs no pass."""

    def test_a_waiting_phase_without_a_pass_holds(self) -> None:
        self.assertEqual(todo.problems(WAITS, ""), [])

    def test_a_phase_whose_every_item_waits_takes_its_pass_with_it(self) -> None:
        emptied = WAITS.replace("## Phase 1: y\n\n### 1.1 Now\n\n### 1.3 Tune-up pass 1\n\n", "")
        moved = emptied + "\n### 1.3 Tune-up pass 1\n\nWaits on: 1.2\n\nMoved: from Phase 1\n"
        self.assertEqual(todo.problems(moved, ""), [])

    def test_a_waiting_item_left_in_the_chain_is_caught(self) -> None:
        left = WAITS.replace("### 1.1 Now\n", "### 1.1 Now\n\nWaits on: Ghost\n")
        self.assertEqual(todo.problems(left, ""), ["item 1.1 has a Waits on: line; move it to \"## Phase W: waiting on Ghost\" with a Moved: line"])

    def test_a_waiting_item_without_its_lines_is_caught(self) -> None:
        self.assertEqual(todo.problems(WAITS.replace("Waits on: counsel\n\n", ""), ""), ["item 1.2 is in the waiting phase without a Waits on: line"])
        self.assertEqual(todo.problems(WAITS.replace("Moved: from Phase 1\n", ""), ""), ["item 1.2 is in the waiting phase without \"Moved: from Phase 1\""])
        self.assertEqual(todo.problems(WAITS.replace("Moved: from Phase 1", "Moved: from Phase 0"), ""), ["item 1.2 is in the waiting phase without \"Moved: from Phase 1\""])

    def test_the_environment_and_reference_kinds_hold_with_what_they_wait_on(self) -> None:
        """4.7: what a session lacks is a kind with a shape; Ghost, counsel and the items a pass waits on stay words."""
        kinds = WAITS.replace("Waits on: Ghost's ruling", "Waits on: environment (tuf-repo-cdn.sigstore.dev, api.osv.dev)").replace(
            "Waits on: counsel", "Waits on: reference (the IBM Enterprise COBOL manuals, on a private mount)")
        self.assertEqual(todo.problems(kinds, ""), [])
        self.assertEqual(todo.problems(WAITS, ""), [])

    def test_a_shaped_kind_without_its_shape_is_caught(self) -> None:
        for line, kind in (("Waits on: environment", "environment"), ("Waits on: environment ()", "environment"),
                           ("Waits on: Reference (the manuals)", "reference"), ("Waits on: reference (x) and more", "reference")):
            with self.subTest(line=line):
                self.assertEqual(todo.problems(WAITS.replace("Waits on: counsel", line), ""),
                                 [f"item 1.2 waits on {kind} without its shape: `Waits on: {kind} (<what>)`"])
        self.assertEqual(todo.problems(WAITS.replace("Waits on: counsel", "Waits on: environmental review"), ""), [])

    def test_the_waiting_phase_is_last(self) -> None:
        after = WAITS + "\n## Phase 2: z\n\n### 2.1 Tune-up pass 2\n"
        self.assertEqual(todo.problems(after, ""), ["the waiting phase is not the last phase: a numbered phase follows it"])

    def test_waiting_items_keep_numeric_order(self) -> None:
        swapped = WAITS.replace("### 0.2 Later", "### 1.4 Later")
        self.assertEqual(todo.problems(swapped, ""), ["item 1.4 is in the waiting phase without \"Moved: from Phase 1\"", "waiting items out of order: ['1.4', '1.2']"])
