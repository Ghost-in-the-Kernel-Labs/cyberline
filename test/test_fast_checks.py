"""The fast checks and the count on main (C-040): `scripts/gate.sh --fast` is the landing checkpoint, recording the tree
with kind `fast`, which scripts/commit.sh accepts and names in a trailer; the key scan refuses both runs; and the tune-up
count runs along main's first-parent line only, so a session branch's saves are never counted. Scratch repositories from
test/support_git.py, as test/test_gates.py uses them."""
import os
import re
import subprocess
import unittest
from pathlib import Path

from scripts.checks import gate_record
from test.support_git import attempt, gate, gated_repo, git_out, record, recorded, repo_with, run_commit

FAST_STEPS = ["the fast loop", "the key scan", "docs/decisions.md", "docs/journal/INDEX.md"]


class TheFastChecks(unittest.TestCase):
    """scripts/gate.sh --fast, the landing checkpoint (C-040): the fast loop, the key scan and the generated files; no slow
    tests, no stack gate, no metrics; it records the tree with kind `fast`, and commit.sh accepts that record with the
    trailer `Gate: fast checks`."""

    def fast(self, root: Path) -> subprocess.CompletedProcess:
        """The scratch repository's fast checks, `scripts/gate.sh --fast`, warm."""
        env = {k: v for k, v in os.environ.items() if k != "GHOST_COLD"}
        return subprocess.run(["bash", "scripts/gate.sh", "--fast"], cwd=root, capture_output=True, text=True, env=env)

    def test_the_fast_checks_run_their_steps_record_the_tree_and_say_fast(self) -> None:
        root = gated_repo()
        (root / "loose.txt").write_text("not yet committed")
        result = self.fast(root)
        lines = result.stdout.splitlines()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual([re.sub(r"\(\d+\.\d\d s\)", "(N s)", line) for line in lines[:-1]], [f"== {s}: passed (N s)" for s in FAST_STEPS])
        self.assertRegex(lines[-1], r"^gate \(fast\): passed; fast loop \d+\.\d\ds, \d+\.\d\d min, 1 commits since the last tune-up$")
        self.assertEqual(recorded(root), gate_record.tree(root))
        self.assertEqual((root / ".git" / "ghost" / "kind").read_text().strip(), "fast")
        self.assertTrue((root / "build" / "gate-fast.log").exists())
        self.assertEqual([line.split(" ", 1)[1] for line in (root / "build" / "gate-fast-times.txt").read_text().splitlines()], FAST_STEPS)
        self.assertFalse((root / "build" / "gate.log").exists(), "the full gate's log is left alone")

    def test_the_full_gate_says_full_and_a_fast_run_replaces_an_earlier_record_s_kind(self) -> None:
        root = gated_repo()
        gate(root)
        self.assertEqual((root / ".git" / "ghost" / "kind").read_text().strip(), "full")
        self.assertEqual(self.fast(root).returncode, 0)
        self.assertEqual((root / ".git" / "ghost" / "kind").read_text().strip(), "fast")

    def test_a_key_in_the_tree_s_changes_refuses_both_runs_and_names_no_value(self) -> None:
        root = gated_repo()
        key = "AKIA" + "IOSFODNN7" + "EXAMPLE"  # assembled, so no key-shaped literal exists in source
        (root / "config.txt").write_text(f"aws_key = {key}\n")
        for result in (self.fast(root), gate(root)):
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout.splitlines()[-1].split(": ", 1)[1], "refused at the key scan (a secret in the tree's changes: build/gate.log names its fingerprint)")
            self.assertNotIn(key, result.stdout)
        self.assertNotIn(key, (root / "build" / "gate-fast.log").read_text())
        self.assertIsNone(recorded(root))

    def test_a_cold_fast_run_and_an_unknown_argument_are_refused(self) -> None:
        root = gated_repo()
        cold = subprocess.run(["bash", "scripts/gate.sh", "--fast"], cwd=root, capture_output=True, text=True, env=dict(os.environ, GHOST_COLD="1"))
        self.assertEqual((cold.returncode, cold.stdout), (1, "gate: refused at the arguments (the cold run is the full gate's: GHOST_COLD=1 scripts/gate.sh)\n"))
        other = self.fast(root)
        self.assertEqual(other.returncode, 0)
        unknown = subprocess.run(["bash", "scripts/gate.sh", "--slow"], cwd=root, capture_output=True, text=True)
        self.assertEqual((unknown.returncode, unknown.stdout), (1, "gate: refused at the arguments (unknown argument --slow; usage: scripts/gate.sh [--fast])\n"))

    def test_commit_sh_accepts_a_fast_record_and_says_so_in_a_trailer(self) -> None:
        root = repo_with(1)
        (root / "next.txt").write_text("landed on the fast checks")
        sha = record(root)
        (root / ".git" / "ghost" / "kind").write_text("fast\n")
        result = run_commit(root, ["-a", "-m", "4.10 a landing"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(git_out(root, ["rev-parse", "HEAD^{tree}"]), sha)
        self.assertEqual(git_out(root, ["log", "-1", "--format=%B"]), "4.10 a landing\n\nGate: fast checks")
        (root / "next.txt").write_text("landed on the full gate")
        record(root)
        (root / ".git" / "ghost" / "kind").write_text("full\n")
        self.assertEqual(run_commit(root, ["-a", "-m", "4.10 another"]).returncode, 0)
        self.assertEqual(git_out(root, ["log", "-1", "--format=%B"]), "4.10 another")


class TheCountOnMain(unittest.TestCase):
    """The tune-up count runs along main's first-parent line only (C-040): a session branch's saves are never counted, by
    commit.sh and by the gate's verdict alike."""

    def test_saves_on_a_branch_are_not_counted_by_commit_sh(self) -> None:
        root = repo_with(7)
        subprocess.run(["git", "-C", str(root), "checkout", "-q", "-b", "claude/session"], check=True)
        for n in range(3):
            subprocess.run(["git", "-C", str(root), "commit", "-q", "--allow-empty", "-m", f"save {n}"], check=True)
        subprocess.run(["git", "-C", str(root), "checkout", "-q", "main"], check=True)
        result = attempt(root, "the eighth landing")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("commit: 7 of 8 commits since the last tune-up", result.stdout)

    def test_the_gate_s_verdict_counts_main_from_a_branch(self) -> None:
        root = gated_repo()
        for subject in ("stamped from Ghost-Core", "one"):
            subprocess.run(["git", "-C", str(root), "commit", "-q", "--allow-empty", "-m", subject], check=True)
        subprocess.run(["git", "-C", str(root), "checkout", "-q", "-b", "agent/worker"], check=True)
        for n in range(4):
            subprocess.run(["git", "-C", str(root), "commit", "-q", "--allow-empty", "-m", f"save {n}"], check=True)
        self.assertRegex(gate(root).stdout.splitlines()[-1], r", 1 commits since the last tune-up$")
