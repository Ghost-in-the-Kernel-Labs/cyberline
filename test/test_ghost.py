"""theGhost.md holds its shape, its index is current; and each way it can break, planted, is caught (C-008, C-013)."""
import subprocess
import sys
import unittest

from scripts import decisions_index
from scripts.checks import ghost
from test.support import BROKEN, ROOT, scratch


def entry(rid: str, status: str = "in force", subject: str = "method", see_also: str = "C-001", extra: str = "") -> str:
    """A complete entry, e.g. entry("C-001") is a well-formed in-force decision on 'method'."""
    return (
        f"### {rid}: a decision\n- **Decision:** d\n- **Why:** w\n- **Held by:** h\n- **Source:** s\n"
        f"- **Status:** {status}\n- **See also:** {see_also}\n- **subject:** {subject}\n{extra}\n"
    )


class TheRepository(unittest.TestCase):
    def test_the_real_file_holds(self) -> None:
        self.assertEqual(ghost.problems((ROOT / "theGhost.md").read_text(), ROOT), [])

    def test_every_core_entry_carries_the_core_line(self) -> None:
        entries = ghost.split_entries((ROOT / "theGhost.md").read_text())
        self.assertEqual([rid for rid, e in entries.items() if rid.startswith("C-") and "Core" not in ghost.fields_of(e)], [])

    def test_a_stamped_log_holds_the_core_and_its_own_prefix(self) -> None:
        text = entry("C-001") + entry("C-002") + entry("TP-001", see_also="Core C-001") + entry("TP-002", see_also="TP-001")
        self.assertEqual(ghost.problems(text), [])
        self.assertEqual(ghost.problems(text + entry("TP-004", see_also="TP-001")), ["entry 3 of TP- is TP-004, expected TP-003"])
        self.assertIn("three prefixes in one log", ghost.problems(text + entry("ZZ-001", see_also="ZZ-001"))[0])

    def test_the_index_is_current(self) -> None:
        result = subprocess.run([sys.executable, "-I", str(ROOT / "scripts" / "decisions_index.py"), "--check"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_the_planted_break_is_caught(self) -> None:
        found = ghost.problems((BROKEN / "ghost" / "theGhost.md").read_text())
        self.assertEqual(found, ["entry 2 of C- is C-003, expected C-002", "C-003 has no Why line"])


class TheCheck(unittest.TestCase):
    def test_a_clean_pair_holds(self) -> None:
        self.assertEqual(ghost.problems(entry("C-001") + entry("C-002")), [])

    def test_the_prefix_is_read_from_the_file(self) -> None:
        text = entry("NR-001", see_also="NR-001") + entry("NR-002", see_also="NR-001")
        self.assertEqual(ghost.prefix_of(text), "NR")
        self.assertEqual(ghost.problems(text), [])

    def test_a_duplicated_id_is_caught(self) -> None:
        self.assertIn("C-001 appears 2 times", ghost.problems(entry("C-001") + entry("C-001")))

    def test_a_gap_in_the_sequence_is_caught(self) -> None:
        self.assertEqual(ghost.problems(entry("C-001") + entry("C-003")), ["entry 2 of C- is C-003, expected C-002"])

    def test_a_missing_field_is_caught(self) -> None:
        broken = entry("C-001").replace("- **Held by:** h\n", "")
        self.assertEqual(ghost.problems(broken), ["C-001 has no Held by line"])

    def test_an_unknown_status_is_caught(self) -> None:
        self.assertEqual(ghost.problems(entry("C-001", status="maybe")), ["C-001 has status 'maybe', not one of the five"])

    def test_a_supersession_must_name_an_entry(self) -> None:
        self.assertEqual(ghost.problems(entry("C-001", status="superseded by C-009")), ["C-001 is superseded by C-009, which does not exist"])

    def test_a_supersession_must_be_named_back(self) -> None:
        text = entry("C-001", status="superseded by C-002") + entry("C-002")
        self.assertEqual(ghost.problems(text), ["C-001 is superseded by C-002, whose Supersedes line does not name it"])
        named_back = entry("C-001", status="superseded by C-002") + entry("C-002", extra="- **Supersedes:** C-001\n")
        self.assertEqual(ghost.problems(named_back), [])

    def test_an_example_entry_in_a_code_block_is_not_an_entry(self) -> None:
        text = "```text\n" + entry("C-000") + "```\n" + entry("C-001")
        self.assertEqual(ghost.problems(text), [])

    def test_a_dangling_see_also_is_caught(self) -> None:
        self.assertEqual(ghost.problems(entry("C-001", see_also="C-001, C-077")), ["C-001 sees also C-077, which does not exist"])

    def test_a_see_also_to_another_log_is_not_checked(self) -> None:
        self.assertEqual(ghost.problems(entry("C-001", see_also="Katana R-008")), [])

    def test_a_wrong_core_line_is_caught(self) -> None:
        self.assertEqual(ghost.problems(entry("C-001", extra="- **Core:** part of something else\n")), ["C-001 has a Core line that is not the Core sentence"])
        self.assertEqual(ghost.problems(entry("C-001", extra=f"- **Core:** {ghost.CORE_LINE}\n")), [])

    def test_two_in_force_decisions_that_conflict_are_caught(self) -> None:
        text = entry("C-001", extra="- **conflicts-with:** C-002\n") + entry("C-002")
        self.assertEqual(ghost.problems(text), ["C-001 and C-002 are both in force on 'method' and conflict"])

    def test_a_conflict_with_a_superseded_decision_is_fine(self) -> None:
        text = entry("C-001", status="superseded by C-002", extra="- **conflicts-with:** C-002\n") + entry("C-002", extra="- **Supersedes:** C-001\n")
        self.assertEqual(ghost.problems(text), [])

    def test_a_conflict_on_different_subjects_is_fine(self) -> None:
        text = entry("C-001", extra="- **conflicts-with:** C-002\n") + entry("C-002", subject="agents")
        self.assertEqual(ghost.problems(text), [])

    def test_the_index_renders_one_row_per_entry(self) -> None:
        rendered = decisions_index.render(entry("C-001") + entry("C-002", status="proposed", subject="agents"))
        self.assertIn("| C-001 | a decision | in force | method |", rendered)
        self.assertIn("| C-002 | a decision | proposed | agents |", rendered)


class HeldBy(unittest.TestCase):
    def held(self, line: str) -> str:
        """An in-force entry whose Held by line is `line`, e.g. held("`docs/x.md`")."""
        return entry("C-001").replace("- **Held by:** h", f"- **Held by:** {line}")

    def test_the_planted_missing_path_is_caught(self) -> None:
        root = BROKEN / "ghost" / "held_by"
        found = ghost.problems((root / "theGhost.md").read_text(), root)
        self.assertEqual(found, [
            "C-001 is held by docs/missing.md, which does not exist and no open TODO item promises",
            "C-002 is held by test/test_missing.py, which does not exist and no open TODO item promises",
        ])

    def test_an_existing_path_holds(self) -> None:
        root = scratch()
        (root / "docs" / "here.md").write_text("x\n")
        self.assertEqual(ghost.problems(self.held("`docs/here.md`"), root), [])

    def test_a_path_an_open_todo_item_promises_holds_until_it_is_done(self) -> None:
        root = scratch()
        (root / "TODO.md").write_text("### 0.1 x\n\nCheck: `docs/later.md` exists.\n")
        self.assertEqual(ghost.problems(self.held("`docs/later.md`"), root), [])
        (root / "TODO.md").write_text("")
        self.assertEqual(len(ghost.problems(self.held("`docs/later.md`"), root)), 1)

    def test_a_parents_path_and_a_command_are_not_checked(self) -> None:
        root = scratch()
        self.assertEqual(ghost.problems(self.held("`npm test`. SB: `src/a.ts`. In the parents: `x/y.java`"), root), [])
        self.assertEqual(ghost.held_paths("`a/b.md`, `x.sh`, `gradle test`. KT: `c/d.md`"), ["a/b.md", "x.sh"])

    def test_a_core_segment_after_a_parent_tag_is_ours(self) -> None:
        self.assertEqual(ghost.held_paths("SB: `src/a.ts`. Core: `test/t.py`, `docs/when/`. NR: `x/y.py`"), ["test/t.py", "docs/when/"])
        self.assertEqual(ghost.held_paths("`a.md`. KT: `b.md`. Core: `c.md`. In the parents: `d.md`. Core: `e.md`"), ["a.md", "c.md", "e.md"])

    def test_refs_scoped_packages_urls_and_commands_are_not_paths(self) -> None:
        line = "`origin/main`, `refs/heads/x`, `@stryker-mutator/core`, `https://x.org/a.md`, `npm test`, `gradle`, `test/test_<check>.py`"
        self.assertEqual(ghost.held_paths(line), [])
        self.assertEqual(ghost.held_paths("`security-manifest.lock`, `scripts/x.mjs`, `src/A.java`"), ["security-manifest.lock", "scripts/x.mjs", "src/A.java"])

    def test_the_core_entries_name_their_own_holders(self) -> None:
        entries = ghost.split_entries((ROOT / "theGhost.md").read_text())
        held = [rid for rid, e in entries.items() if ghost.fields_of(e).get("Status") == "in force" and ghost.held_paths(ghost.fields_of(e)["Held by"])]
        self.assertGreaterEqual(len(held), 31)

    def test_only_an_in_force_decision_is_held(self) -> None:
        root = scratch()
        text = entry("C-001", status="withdrawn").replace("- **Held by:** h", "- **Held by:** `docs/gone.md`")
        self.assertEqual(ghost.problems(text, root), [])
