"""The journal holds, its index is current; and each way it can break, planted, is caught (C-015, C-029)."""
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import journal_index, next_id
from scripts.checks import journal
from test.support import BROKEN, ROOT

FOR_GHOST = "## For Ghost: waiting on you\n\n1. J-002: conflict.\n\n## Trials\n"


def entry(rid: str, kind: str = "decision", extra: str = "") -> str:
    """A complete entry of the class given, e.g. entry("J-001")."""
    lines = "".join(f"- **{name}**: x\n" for name in journal.FIELDS if name != "Class")
    return f"### {rid} a title\n- **Class**: {kind}\n{lines}{extra}\n"


class TheRepository(unittest.TestCase):
    def test_the_real_journal_holds(self) -> None:
        self.assertEqual(journal.problems_in(ROOT), [])

    def test_the_index_is_current(self) -> None:
        """The written index against a fresh rendering in memory; the file is read, never written (1.25)."""
        index = ROOT / "docs" / "journal" / "INDEX.md"
        self.assertEqual(index.read_text(), journal_index.render(ROOT), "stale: run python3 -I scripts/journal_index.py")

    def test_a_stale_index_is_refused_in_memory(self) -> None:
        self.assertFalse(journal_index.current(BROKEN / "journal_index"))
        self.assertNotEqual((BROKEN / "journal_index" / "docs" / "journal" / "INDEX.md").read_text(), journal_index.render(BROKEN / "journal_index"))

    def test_a_stale_index_is_refused_by_the_script(self) -> None:
        """journal_index.py --check run in a scratch copy holding the planted stale index: exit 1, the file untouched."""
        copy = Path(tempfile.mkdtemp(prefix="ghost-core-index-"))
        self.addCleanup(shutil.rmtree, copy)
        for name in ("scripts/__init__.py", "scripts/journal_index.py", "scripts/checks/__init__.py", "scripts/checks/journal.py", "scripts/checks/common.py"):
            (copy / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / name, copy / name)
        shutil.copytree(BROKEN / "journal_index" / "docs", copy / "docs")
        before = (copy / "docs" / "journal" / "INDEX.md").read_bytes()
        result = subprocess.run([sys.executable, "-I", str(copy / "scripts" / "journal_index.py"), "--check"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("stale", result.stdout)
        self.assertEqual((copy / "docs" / "journal" / "INDEX.md").read_bytes(), before)

    def test_the_planted_break_is_caught(self) -> None:
        found = journal.problems_in(BROKEN / "journal")
        self.assertEqual(found, ["J-002 has no Cost line", "J-002 has class 'oops', not one of 11"])


class TheCheck(unittest.TestCase):
    def test_a_clean_pair_holds(self) -> None:
        self.assertEqual(journal.problems(entry("J-001") + entry("J-002"), ""), [])

    def test_every_class_docs_journal_md_lists_is_accepted(self) -> None:
        """3.9: `feature` was listed in docs/JOURNAL.md and refused by the check."""
        listed = re.findall(r"`([a-z-]+)`", (ROOT / "docs" / "JOURNAL.md").read_text().split("- **Class**: one of", 1)[1].split("\n- **Intent**", 1)[0])
        self.assertIn("feature", listed)
        self.assertEqual(set(listed), set(journal.CLASSES))
        self.assertEqual(journal.problems(entry("J-001", "feature"), ""), [])

    def test_a_gap_is_caught(self) -> None:
        self.assertEqual(journal.problems(entry("J-001") + entry("J-003"), ""), ["entry 2 is J-003, expected J-002"])

    def test_a_missing_field_is_caught(self) -> None:
        broken = entry("J-001").replace("- **Found**: x\n", "")
        self.assertEqual(journal.problems(broken, ""), ["J-001 has no Found line"])

    def test_an_unknown_class_is_caught(self) -> None:
        self.assertEqual(journal.problems(entry("J-001", kind="vibe"), ""), ["J-001 has class 'vibe', not one of 11"])

    def test_a_conflict_needs_both_objectives(self) -> None:
        found = journal.problems(entry("J-001", kind="conflict"), FOR_GHOST.replace("J-002", "J-001"))
        self.assertEqual(found, ["J-001 is a conflict with no Mine objective", "J-001 is a conflict with no Theirs objective"])

    def test_an_open_conflict_must_be_listed_for_ghost(self) -> None:
        text = entry("J-001") + entry("J-002", kind="conflict", extra="- **Mine**: a\n- **Theirs**: b\n")
        self.assertEqual(journal.problems(text, ""), ["J-002 is an open conflict not listed in HANDOFF.md's For Ghost section"])
        self.assertEqual(journal.problems(text, FOR_GHOST), [])

    def test_a_conflict_ghost_resolved_need_not_be_listed(self) -> None:
        resolved = entry("J-001", kind="conflict", extra="- **Mine**: a\n- **Theirs**: b\n").replace("- **Resolved**: x", "- **Resolved**: Ghost chose a")
        self.assertEqual(journal.problems(resolved, ""), [])

    def test_the_next_id_follows_the_highest(self) -> None:
        self.assertEqual(next_id.next_id("journal", "### J-004 x\n### J-002 y"), "J-005")
        self.assertEqual(next_id.next_id("decision", "### C-034: x\nSee also C-012"), "C-035")
        self.assertEqual(next_id.next_id("journal", ""), "J-001")


HEADER_RANGE = "# Journal\n\nThis file holds J-001 to J-099; see J-100 onward in the next file.\n\n### J-008 a\nbody names J-050\n### J-009 b\n"


class TheIdScripts(unittest.TestCase):
    def test_a_header_range_and_a_mention_never_raise_the_answer(self) -> None:
        self.assertEqual(next_id.next_id("journal", HEADER_RANGE), "J-010")
        self.assertEqual(next_id.next_id("decision", "Decisions C-001 to C-099\n### C-034: x\nSee also C-090\n"), "C-035")

    def run_script(self, name: str, flag: str) -> subprocess.CompletedProcess:
        """A script run with no PATH, so it could not start git: the help must need nothing else."""
        return subprocess.run([sys.executable, "-I", str(ROOT / "scripts" / name), flag], capture_output=True, text=True, env={"PATH": ""})

    def test_help_prints_usage_and_runs_nothing(self) -> None:
        for name in ("next_id.py", "journal_index.py"):
            for flag in ("--help", "-h"):
                with self.subTest(script=name, flag=flag):
                    result = self.run_script(name, flag)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn("python3 -I scripts/" + name, result.stdout)
                    self.assertIn("--help", result.stdout)

    def test_journal_index_help_writes_nothing(self) -> None:
        """The real index is compared before and after, never touched or regenerated (1.25)."""
        index = ROOT / "docs" / "journal" / "INDEX.md"
        before = (index.stat().st_mtime_ns, index.read_bytes())
        self.run_script("journal_index.py", "--help")
        self.assertEqual((index.stat().st_mtime_ns, index.read_bytes()), before)
