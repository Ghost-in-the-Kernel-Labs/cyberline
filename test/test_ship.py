"""scripts/ship.sh, the only push (C-037, C-031), proven on a scratch clone of a bare remote: it ships a HEAD whose tree is
the gate's record as a fast-forward, prints one line, and refuses a stale record, a remote main that moved and an
uncommitted change, pushing nothing; a remote with no main takes the first ship. And no document or script names a raw
push but the ship itself and process.md's mention of it."""
import subprocess
import tempfile
import unittest
from pathlib import Path

from test.support import ROOT
from test.support_git import record

SHIP = ROOT / "scripts" / "ship.sh"
IDENTITY = ["-c", "user.name=Ghost", "-c", "user.email=g@example.invalid"]


def git(cwd: Path, args: list[str]) -> str:
    """git's output in cwd, stripped: git(clone, ["rev-parse", "HEAD"]) gives HEAD's SHA."""
    return subprocess.run(["git", "-C", str(cwd), *IDENTITY, *args], capture_output=True, text=True, check=True).stdout.strip()


def commit(clone: Path, name: str) -> None:
    """One commit in the clone that adds the file name, holding its own name."""
    (clone / name).write_text(name)
    git(clone, ["add", "-A"])
    git(clone, ["commit", "-q", "-m", name])


def remote_and_clone(seeded: bool = True) -> tuple[Path, Path]:
    """A bare remote and a clone of it holding a copy of scripts/ship.sh, committed; with seeded, main is on the remote."""
    top = Path(tempfile.mkdtemp(prefix="ghost-core-ship-"))
    remote, clone = top / "remote.git", top / "clone"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(remote)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(clone)], check=True)
    git(clone, ["remote", "add", "origin", str(remote)])
    (clone / "scripts").mkdir()
    (clone / "scripts" / "ship.sh").write_text(SHIP.read_text())
    commit(clone, "start")
    if seeded:
        git(clone, ["push", "-q", "origin", "main"])  # the scratch remote's seed, before any record exists
    return remote, clone


def ship(clone: Path) -> subprocess.CompletedProcess:
    """The clone's scripts/ship.sh, run as an agent runs it."""
    return subprocess.run(["bash", "scripts/ship.sh"], cwd=clone, capture_output=True, text=True)


class TheShip(unittest.TestCase):
    def test_a_recorded_head_ships_as_a_fast_forward(self) -> None:
        remote, clone = remote_and_clone()
        commit(clone, "work")
        record(clone)
        result = ship(clone)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, f"ship: {git(clone, ['rev-parse', '--short', 'HEAD'])} → origin/main\n")
        self.assertEqual(git(remote, ["rev-parse", "main"]), git(clone, ["rev-parse", "HEAD"]))

    def test_the_first_ship_to_a_remote_with_no_main(self) -> None:
        remote, clone = remote_and_clone(seeded=False)
        record(clone)
        self.assertEqual(ship(clone).returncode, 0)
        self.assertEqual(git(remote, ["rev-parse", "main"]), git(clone, ["rev-parse", "HEAD"]))

    def test_a_stale_or_absent_record_is_refused(self) -> None:
        remote, clone = remote_and_clone()
        before = git(remote, ["rev-parse", "main"])
        commit(clone, "work")
        absent = ship(clone)
        self.assertEqual((absent.returncode, absent.stdout), (1, "ship: refused at the record (gate first: no tree recorded; run scripts/gate.sh)\n"))
        record(clone)
        commit(clone, "after the gate")
        stale = ship(clone)
        self.assertEqual(stale.returncode, 1)
        self.assertRegex(stale.stdout, r"^ship: refused at the record \(gate first: HEAD's tree \w{10} is not the tree the gate passed on, \w{10}\)\n$")
        self.assertEqual(git(remote, ["rev-parse", "main"]), before)

    def test_a_remote_main_that_moved_is_refused(self) -> None:
        remote, clone = remote_and_clone()
        other = remote.parent / "other"
        subprocess.run(["git", "clone", "-q", str(remote), str(other)], check=True)
        commit(other, "theirs")
        git(other, ["push", "-q", "origin", "main"])
        commit(clone, "mine")
        record(clone)
        result = ship(clone)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "ship: refused at the fast-forward (fetch and rebuild: main moved; rebase onto origin/main, run scripts/gate.sh and commit again)\n")
        self.assertEqual(git(remote, ["log", "-1", "--format=%s", "main"]), "theirs")

    def test_an_uncommitted_change_is_refused(self) -> None:
        remote, clone = remote_and_clone()
        commit(clone, "work")
        record(clone)
        (clone / "loose.txt").write_text("not committed")
        result = ship(clone)
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stdout.startswith("ship: refused at the working tree (uncommitted changes"), result.stdout)


class TheOnlyPush(unittest.TestCase):
    def test_no_document_or_script_names_a_raw_push_but_the_ship_and_the_save(self) -> None:
        """The grep of TODO 3.8's check, widened by 4.10: the save pushes a session branch, never main (C-040). DONE.md's
        lines that quote those checks verbatim are a record of them, not a push."""
        found = subprocess.run(["grep", "-rn", "git push", "docs", "scripts", "README.md", "CLAUDE.md"], cwd=ROOT, capture_output=True, text=True).stdout
        files = {line.split(":", 1)[0] for line in found.splitlines() if not line.startswith("docs/DONE.md:") or "Check: " not in line}
        self.assertEqual(files, {"scripts/ship.sh", "scripts/save.sh", "docs/paths/process.md"}, found)
        code = "\n".join(line for line in (ROOT / "scripts" / "save.sh").read_text().splitlines() if not line.startswith("#"))
        self.assertIn("git push -q -u origin HEAD", code)
        self.assertNotIn("refs/heads/main", code)
        self.assertNotIn("--force", code)
