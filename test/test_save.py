"""scripts/save.sh, a session's checkpoint on its own branch (C-040), proven on a scratch clone of a bare remote: it
stages everything, scans the staged diff for keys, commits as Ghost with committer Claude, pushes the branch, writes no
tree record and runs no gate; it refuses main, a key, and an empty message; without a remote it commits and says so."""
import subprocess
import unittest
from pathlib import Path

from scripts.checks import gate_record
from test.support import ROOT
from test.test_ship import commit, git, remote_and_clone

SAVE = ROOT / "scripts" / "save.sh"
SECRETS = ROOT / "scripts" / "checks" / "secrets.py"


def session_clone(branch: str = "claude/session") -> tuple[Path, Path]:
    """A bare remote and a clone on the branch given, holding scripts/save.sh and the key scan, committed on main first."""
    remote, clone = remote_and_clone()
    (clone / "scripts" / "checks").mkdir()
    (clone / "scripts" / "save.sh").write_text(SAVE.read_text())
    (clone / "scripts" / "checks" / "secrets.py").write_text(SECRETS.read_text())
    commit(clone, "tools")
    git(clone, ["checkout", "-q", "-b", branch])
    return remote, clone


def save(clone: Path, args: list[str], stdin: str | None = None) -> subprocess.CompletedProcess:
    """The clone's scripts/save.sh with the arguments given, run as an agent runs it: save(clone, ["-m", "wip"])."""
    return subprocess.run(["bash", "scripts/save.sh", *args], cwd=clone, input=stdin, capture_output=True, text=True)


class TheSave(unittest.TestCase):
    def test_a_save_commits_everything_as_ghost_pushes_the_branch_and_records_nothing(self) -> None:
        remote, clone = session_clone()
        main_before = git(remote, ["rev-parse", "main"])
        (clone / "work.txt").write_text("half done")
        (clone / "new" ).mkdir()
        (clone / "new" / "file.txt").write_text("untracked until now")
        result = save(clone, ["-m", "wip: half of 4.10"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        short = git(clone, ["rev-parse", "--short", "HEAD"])
        self.assertEqual(result.stdout, f"save: {short} → origin/claude/session\n")
        self.assertEqual(git(clone, ["log", "-1", "--format=%an <%ae>|%cn <%ce>|%s"]), "Ghost <118085043+ghost-in-the-kernel@users.noreply.github.com>|Claude <noreply@anthropic.com>|wip: half of 4.10")
        self.assertEqual(git(remote, ["rev-parse", "claude/session"]), git(clone, ["rev-parse", "HEAD"]))
        self.assertEqual(git(clone, ["status", "--porcelain"]), "")
        self.assertIsNone(gate_record.record(clone))
        self.assertEqual(git(remote, ["rev-parse", "main"]), main_before, "main is untouched")

    def test_a_message_on_stdin_and_a_second_save_with_nothing_new_that_still_pushes(self) -> None:
        remote, clone = session_clone()
        (clone / "work.txt").write_text("one")
        self.assertEqual(save(clone, ["-F", "-"], stdin="wip\n\nthe body\n").returncode, 0)
        self.assertEqual(git(clone, ["log", "-1", "--format=%B"]), "wip\n\nthe body")
        git(clone, ["commit", "-q", "--allow-empty", "-m", "made another way"])
        result = save(clone, ["-m", "nothing new"])
        self.assertEqual((result.returncode, result.stdout), (0, "save: nothing to commit; pushed claude/session\n"))
        self.assertEqual(git(remote, ["log", "-1", "--format=%s", "claude/session"]), "made another way")

    def test_a_save_on_main_is_refused_and_stages_nothing(self) -> None:
        _, clone = session_clone()
        git(clone, ["checkout", "-q", "main"])
        (clone / "work.txt").write_text("not for main this way")
        result = save(clone, ["-m", "wip"])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "save: refused at the branch (on main: a save goes to a session branch, claude/<session> or agent/<name>; main is landed through scripts/commit.sh and scripts/ship.sh)\n")
        self.assertEqual(git(clone, ["diff", "--cached", "--name-only"]), "")

    def test_a_key_is_refused_never_printed_and_nothing_is_committed_or_pushed(self) -> None:
        remote, clone = session_clone()
        key = "AKIA" + "IOSFODNN7" + "EXAMPLE"  # assembled, so no key-shaped literal exists in source
        (clone / "config.txt").write_text(f"aws_key = {key}\n")
        before = git(clone, ["rev-parse", "HEAD"])
        result = save(clone, ["-m", "wip"])
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stdout.startswith("save: refused at the key scan (the staged diff holds a secret: "), result.stdout)
        self.assertNotIn(key, result.stdout + result.stderr)
        self.assertEqual(git(clone, ["rev-parse", "HEAD"]), before)
        self.assertEqual(subprocess.run(["git", "-C", str(remote), "rev-parse", "-q", "--verify", "claude/session"], capture_output=True).returncode, 1)

    def test_no_message_and_an_empty_message_are_refused(self) -> None:
        _, clone = session_clone()
        self.assertEqual(save(clone, []).stdout, "save: refused at the arguments (no message; usage: scripts/save.sh -m msg | -F file)\n")
        self.assertEqual(save(clone, ["-m", "  "]).stdout, "save: refused at the arguments (the message is empty)\n")
        self.assertEqual(save(clone, ["-a"]).returncode, 1)

    def test_without_a_remote_the_save_commits_and_says_so(self) -> None:
        _, clone = session_clone("agent/worker")
        git(clone, ["remote", "remove", "origin"])
        (clone / "work.txt").write_text("offline")
        result = save(clone, ["-m", "wip"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout, f"save: {git(clone, ['rev-parse', '--short', 'HEAD'])} on agent/worker (no origin)\n")
        self.assertEqual(save(clone, ["-m", "again"]).stdout, "save: refused at the push (nothing to commit, and no remote origin to push to)\n")


class TheSaveIsNotALanding(unittest.TestCase):
    def test_save_sh_runs_no_gate_and_the_routing_documents_name_it(self) -> None:
        code = "\n".join(line for line in SAVE.read_text().splitlines() if not line.startswith("#"))
        for word in ("gate.sh", "fast.sh", "commit-tree", "ghost/tree", "tune-up"):
            self.assertNotIn(word, code, word)
        for name in ("CLAUDE.md", "docs/paths/process.md", "docs/when/coordinate.md", "docs/when/handoff.md"):
            self.assertIn("scripts/save.sh", (ROOT / name).read_text(), name)
