"""A landing is made from a session branch (C-049), proven on a scratch repository with a bare remote: scripts/commit.sh
on `main` is refused where origin exists; from a session branch it refuses an unsaved change, lands the saved tree on
main's tip as one commit, joins the branch to it, and with --ship pushes main and then the branch in the same step."""
import subprocess
import tempfile
import unittest
from pathlib import Path

from test.support import ROOT
from test.support_git import git_out, record, repo_with, run_commit

BRANCH = "claude/session"


def with_origin(root: Path) -> Path:
    """A bare remote beside the scratch repository, named origin, holding its main, and scripts/ship.sh and scripts/save.sh copied in
    and committed on main: with_origin(repo_with(1)) gives the remote's path."""
    remote = Path(tempfile.mkdtemp(prefix="ghost-core-remote-")) / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(remote)], check=True)
    for name in ("ship.sh", "save.sh"):
        (root / "scripts" / name).write_text((ROOT / "scripts" / name).read_text())
        (root / "scripts" / name).chmod(0o755)
    for args in (["add", "-A"], ["commit", "-q", "-m", "the ship"], ["remote", "add", "origin", str(remote)], ["push", "-q", "origin", "main"]):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)
    return remote


def saved(root: Path, name: str) -> None:
    """One file written and committed on the session branch, as scripts/save.sh leaves it: saved(root, "a") adds a.txt."""
    (root / f"{name}.txt").write_text(name)
    for args in (["add", "-A"], ["commit", "-q", "-m", f"save {name}"]):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def session(commits: int = 1) -> tuple[Path, Path]:
    """A scratch repository with a remote, checked out on a session branch off main: (root, remote)."""
    root = repo_with(commits)
    remote = with_origin(root)
    subprocess.run(["git", "-C", str(root), "checkout", "-q", "-b", BRANCH], check=True)
    return root, remote


class TheLanding(unittest.TestCase):
    def test_a_commit_on_main_is_refused_where_origin_exists(self) -> None:
        root = repo_with(1)
        with_origin(root)
        (root / "a.txt").write_text("a")
        record(root)
        result = run_commit(root, ["-a", "-m", "on main"])
        self.assertEqual(result.returncode, 1)
        self.assertIn("refused at the branch (main is not worked on where origin exists", result.stdout)
        self.assertEqual(git_out(root, ["log", "-1", "--format=%s"]), "the ship")

    def test_an_unsaved_change_on_the_branch_is_refused(self) -> None:
        root, _ = session()
        saved(root, "a")
        (root / "b.txt").write_text("b")
        record(root)
        result = run_commit(root, ["-a", "-m", "unsaved"])
        self.assertEqual(result.returncode, 1)
        self.assertIn(f"refused at the working tree (unsaved changes on {BRANCH}: scripts/save.sh first", result.stdout)
        self.assertEqual(git_out(root, ["log", "-1", "--format=%s", "main"]), "the ship")

    def test_the_saved_tree_lands_on_main_as_one_commit_and_the_branch_joins_it(self) -> None:
        root, _ = session()
        saved(root, "a")
        saved(root, "b")
        before = git_out(root, ["rev-parse", "main"])
        record(root)
        result = run_commit(root, ["-a", "-m", "two files"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(git_out(root, ["log", "-1", "--format=%s %an %P", "main"]), f"two files Ghost {before}")
        self.assertEqual(git_out(root, ["rev-parse", "main^{tree}"]), git_out(root, ["rev-parse", "HEAD^{tree}"]))
        self.assertEqual(git_out(root, ["rev-parse", "HEAD^2"]), git_out(root, ["rev-parse", "main"]))
        self.assertEqual(git_out(root, ["status", "--porcelain"]), "")

    def test_a_second_landing_is_read_against_the_first(self) -> None:
        root, _ = session()
        saved(root, "a")
        record(root)
        run_commit(root, ["-a", "-m", "first"])
        saved(root, "b")
        record(root)
        result = run_commit(root, ["-a", "-m", "second"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(git_out(root, ["log", "--first-parent", "--format=%s", "-3", "main"]).splitlines(), ["second", "first", "the ship"])
        self.assertEqual(git_out(root, ["diff", "--name-only", "main~1", "main"]), "b.txt")

    def test_nothing_new_on_the_branch_is_nothing_to_land(self) -> None:
        root, _ = session()
        record(root)
        result = run_commit(root, ["-a", "-m", "nothing"])
        self.assertEqual(result.returncode, 1)
        self.assertIn("refused at staging (nothing is staged", result.stdout)

    def test_with_ship_main_and_the_branch_are_pushed_in_the_same_step(self) -> None:
        root, remote = session()
        saved(root, "a")
        record(root)
        result = run_commit(root, ["-a", "-m", "shipped", "--ship"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("ship: ", result.stdout)
        self.assertEqual(git_out(remote, ["rev-parse", "main"]), git_out(root, ["rev-parse", "main"]))
        self.assertEqual(git_out(remote, ["rev-parse", BRANCH]), git_out(root, ["rev-parse", "HEAD"]))

    def test_a_docs_only_landing_from_the_branch_needs_no_record(self) -> None:
        root, _ = session()
        (root / "docs" / "note.md").write_text("a note\n")
        for args in (["add", "-A"], ["commit", "-q", "-m", "save a note"]):
            subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)
        result = run_commit(root, ["-a", "-m", "a note", "--docs-only"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Gate: fast loop only", git_out(root, ["log", "-1", "--format=%B", "main"]))
