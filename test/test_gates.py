"""scripts/commit.sh, the gated commit (C-037, C-024), proven on a scratch repository: it stages, scans the staged diff for
a key, keeps the tune-up rule and honours Ghost's deferral line, runs the fast loop, refuses a staged tree that is not the
gate's record unless a docs/-only change says so in its trailer, and commits the recorded tree by commit-tree, author
Ghost and committer Claude, on the parent it named, so a HEAD that moved refuses it; scripts/gate.sh ends with one
verdict line, and in a scratch repository writes the tree record only when every step passed on a tree that did not
change, logs its steps and times, and runs one at a time; no routing document names raw git commit; scripts/fast.sh
runs only the test modules it is given (C-032)."""
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.checks import gate_record
from test.support import ROOT
from test.support_git import attempt, gate, gated_repo, git_out, record, recorded, repo_with, run_commit

AUTHOR = "Ghost <118085043+ghost-in-the-kernel@users.noreply.github.com>"
COMMITTER = "Claude <noreply@anthropic.com>"
# A stub fast loop that commits on its own, as another agent would between commit.sh's staging and its commit.
MOVES_HEAD = "#!/usr/bin/env bash\ngit update-ref refs/heads/main \"$(git commit-tree 'HEAD^{tree}' -p HEAD -m moved)\"\n"


class TheTuneUpRule(unittest.TestCase):
    def test_a_plain_commit_passes_below_eight(self) -> None:
        result = attempt(repo_with(7), "plain 7")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("7 of 8 commits since the last tune-up", result.stdout)

    def test_a_plain_commit_is_refused_at_eight(self) -> None:
        root = repo_with(8)
        result = attempt(root, "plain 8")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout.splitlines()[-1], "commit: refused at the tune-up rule (a tune-up is due: 8 commits since the last, every 8: docs/when/tune-up.md)")
        self.assertEqual(git_out(root, ["log", "-1", "--format=%s"]), "plain 7")

    def test_a_tune_up_commit_is_accepted_at_any_count(self) -> None:
        root = repo_with(13)
        result = attempt(root, "tune-up: routing rows")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("tune-up accepted (13 commits since the last)", result.stdout)
        after = attempt(root, "plain again")
        self.assertEqual(after.returncode, 0, after.stdout)
        self.assertIn("0 of 8", after.stdout)

    def test_the_deferral_line_in_handoff_moves_the_count_to_after_its_commit(self) -> None:
        root = repo_with(9)
        fifth = git_out(root, ["rev-list", "--reverse", "HEAD"]).split()[4]
        (root / "docs" / "HANDOFF.md").write_text(f"- Tune-up deferred through {fifth[:10]} (Ghost)\n")
        result = attempt(root, "plain 9")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"4 of 8 commits since the last tune-up (counted after the deferral through {fifth[:10]})", result.stdout)

    def test_a_deferral_line_naming_no_commit_on_head_is_not_honoured(self) -> None:
        root = repo_with(8)
        (root / "docs" / "HANDOFF.md").write_text("Tune-up deferred through 0123456789abcdef\n")
        result = attempt(root, "plain 8")
        self.assertEqual(result.returncode, 1)
        self.assertIn("names 0123456789abcdef, not a commit on main's history; not honoured", result.stdout)
        self.assertIn("refused at the tune-up rule", result.stdout)

    def test_a_stamped_project_s_founding_commit_is_counted_from_not_toward(self) -> None:
        """4.2: nine plain commits, then "stamped from Ghost-Core", then two: the count is two, where nine alone refuse;
        a subject that only mentions the stamp later in its text does not move the start."""
        root = repo_with(9)
        empty = lambda subject: subprocess.run(["git", "-C", str(root), "commit", "-q", "--allow-empty", "-m", subject], check=True)  # noqa: E731
        for subject in ("stamped from Ghost-Core\n\nThe template's documents.", "one", "two"):
            empty(subject)
        result = attempt(root, "three")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("commit: 2 of 8 commits since the last tune-up", result.stdout)
        empty("a note on what was stamped from Ghost-Core")
        self.assertIn("commit: 4 of 8 commits since the last tune-up", attempt(root, "four").stdout)

    def test_a_red_fast_loop_refuses_the_commit(self) -> None:
        root = repo_with(1)
        (root / "scripts" / "fast.sh").write_text("#!/usr/bin/env bash\nexit 1\n")
        result = attempt(root, "plain, a gate change (C-039)")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout.splitlines()[-1], "commit: refused at the fast loop (the fast loop is red: scripts/fast.sh)")


class TheGatedCommit(unittest.TestCase):
    def test_a_passing_commit_is_the_recorded_tree_authored_by_ghost_committed_by_claude(self) -> None:
        root = repo_with(1)
        result = attempt(root, "1.1 a change")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(result.stdout.splitlines()[-1], f"commit: {git_out(root, ['rev-parse', '--short', 'HEAD'])} 1.1 a change")
        self.assertEqual(git_out(root, ["log", "-1", "--format=%an <%ae>/%cn <%ce>"]), f"{AUTHOR}/{COMMITTER}")
        self.assertEqual(git_out(root, ["rev-parse", "HEAD^{tree}"]), gate_record.record(root))
        self.assertTrue(gate_record.matches(root), "the record must still match the tree after the commit")
        self.assertEqual(git_out(root, ["status", "--porcelain"]), "")

    def test_a_message_on_stdin_reaches_the_commit_whole(self) -> None:
        root = repo_with(1)
        (root / "next.txt").write_text("x")
        record(root)
        result = run_commit(root, ["-a", "-F", "-"], stdin="plain subject\n\nbody line\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(git_out(root, ["log", "-1", "--format=%B"]), "plain subject\n\nbody line")

    def test_only_the_named_paths_are_staged_and_the_record_must_still_match(self) -> None:
        root = repo_with(1)
        (root / "a.txt").write_text("a")
        (root / "b.txt").write_text("b")
        record(root)
        result = run_commit(root, ["a.txt", "-m", "only a"])
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("commit: refused at the record (the staged tree", result.stdout)
        self.assertEqual(git_out(root, ["diff", "--cached", "--name-only"]), "", "a refusal leaves the index as it was")

    def test_a_stale_or_absent_record_is_refused(self) -> None:
        root = repo_with(1)
        (root / "next.txt").write_text("x")
        absent = run_commit(root, ["-a", "-m", "no gate"])
        self.assertEqual(absent.returncode, 1)
        self.assertRegex(absent.stdout.splitlines()[-1], r"^commit: refused at the record \(no tree recorded in .*: run scripts/gate.sh --fast first\)$")
        record(root)
        (root / "next.txt").write_text("changed after the gate")
        stale = run_commit(root, ["-a", "-m", "stale gate"])
        self.assertEqual(stale.returncode, 1)
        self.assertRegex(stale.stdout.splitlines()[-1], r"^commit: refused at the record \(the staged tree \w{10} is not the tree the gate passed on, \w{10}: run scripts/gate.sh --fast first\)$")
        self.assertEqual(git_out(root, ["log", "-1", "--format=%s"]), "plain 0")

    def test_a_docs_only_change_is_committed_without_the_record_and_says_so(self) -> None:
        for args, env in ((["--docs-only"], {}), ([], {"GHOST_GATE": "skip"})):
            with self.subTest(args=args, env=env):
                root = repo_with(1)
                (root / "docs" / "note.md").write_text("a note")
                result = run_commit(root, ["-a", "-m", "a note", *args], env=env)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual(git_out(root, ["log", "-1", "--format=%B"]), "a note\n\nGate: fast loop only")

    def test_a_docs_only_flag_on_a_path_outside_docs_is_refused(self) -> None:
        root = repo_with(1)
        (root / "docs" / "note.md").write_text("a note")
        (root / "README.md").write_text("not under docs")
        result = run_commit(root, ["-a", "-m", "mixed", "--docs-only"])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout.splitlines()[-1], "commit: refused at the record (--docs-only, but README.md is not under docs/: run scripts/gate.sh --fast first)")

    def test_a_key_in_the_staged_diff_is_refused_and_never_printed(self) -> None:
        root = repo_with(1)
        key = "AK" + "IA" + "QWERTYUIOP" + "ASDFGH"
        (root / "config.txt").write_text(f"id = {key}\n")
        record(root)
        result = run_commit(root, ["-a", "-m", "a config"])
        self.assertEqual(result.returncode, 1)
        self.assertTrue(result.stdout.splitlines()[-1].startswith("commit: refused at the secret scan (the staged diff holds a secret: config.txt:1 aws access key"), result.stdout)
        self.assertNotIn(key, result.stdout + result.stderr)
        self.assertEqual(git_out(root, ["log", "-1", "--format=%s"]), "plain 0")

    def test_nothing_staged_is_refused(self) -> None:
        root = repo_with(1)
        record(root)
        result = run_commit(root, ["-a", "-m", "empty"])
        self.assertEqual(result.stdout.splitlines()[-1], "commit: refused at staging (nothing is staged: the paths hold no change)")

    def test_a_head_that_moved_after_staging_refuses_the_commit(self) -> None:
        root = repo_with(1)
        (root / "scripts" / "fast.sh").write_text(MOVES_HEAD)
        (root / "next.txt").write_text("x")
        record(root)
        result = run_commit(root, ["-a", "-m", "mine, a gate change (C-039)"])
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertRegex(result.stdout.splitlines()[-1], r"^commit: refused at the commit \(HEAD moved since staging: main is no longer \w{10}; nothing committed\)$")
        self.assertEqual(git_out(root, ["log", "-1", "--format=%s"]), "moved")


def surface_repo() -> Path:
    """A scratch repository with a committed scripts/gate.sh, the only surface it holds."""
    root = repo_with(1)
    (root / "scripts" / "gate.sh").write_text("echo gate\n")
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "the gate"], check=True)
    return root


class TheCommitCheck(unittest.TestCase):
    """4.9 (C-039): a staged change to a surface needs a decision id in the message; nothing is pinned to a hash."""

    def test_a_surface_changed_without_a_decision_id_is_refused(self) -> None:
        root = surface_repo()
        (root / "scripts" / "gate.sh").write_text("echo changed\n")
        record(root)
        result = run_commit(root, ["-a", "-m", "a gate change"])
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout.splitlines()[-1], "commit: refused at the commit check (scripts/gate.sh runs code by itself: "
                         "a change to it names the decision it carries, as C-nnn, in the message; C-039)")
        self.assertEqual(git_out(root, ["log", "-1", "--format=%s"]), "the gate")

    def test_a_decision_id_anywhere_in_the_message_lets_it_through(self) -> None:
        for message in ("a gate change (C-039)\n", "a gate change\n\nWhy, under XY-012.\n"):
            with self.subTest(message=message):
                root = surface_repo()
                (root / "scripts" / "gate.sh").write_text("echo changed\n")
                record(root)
                result = run_commit(root, ["-a", "-F", "-"], stdin=message)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_every_surface_kind_is_checked_and_nothing_else_is(self) -> None:
        for path in ("stacks/x/gate.sh", ".claude/agents/a.md", ".github/workflows/w.yml"):
            with self.subTest(path=path):
                root = repo_with(1)
                (root / path).parent.mkdir(parents=True, exist_ok=True)
                (root / path).write_text("x\n")
                record(root)
                self.assertIn("refused at the commit check", run_commit(root, ["-a", "-m", "a surface"]).stdout)
        root = repo_with(1)
        (root / "scripts" / "checks").mkdir(parents=True, exist_ok=True)
        (root / "scripts" / "checks" / "x.py").write_text("x\n")
        self.assertEqual(attempt(root, "a check, not a surface").returncode, 0)

    def test_no_lock_exists_and_no_hash_is_read(self) -> None:
        self.assertFalse((ROOT / "security-manifest.lock").exists())
        self.assertNotIn("Manifest:", (ROOT / "scripts" / "commit.sh").read_text())


class TheRecipes(unittest.TestCase):
    def test_no_routing_document_names_raw_git_commit(self) -> None:
        documents = [ROOT / "CLAUDE.md"] + sorted((ROOT / "docs" / "when").glob("*.md")) + sorted((ROOT / "docs" / "paths").glob("*.md"))
        naming = [str(d.relative_to(ROOT)) for d in documents if re.search(r"(?<![`/\w])git commit(?!`)", d.read_text())]
        self.assertEqual(naming, [])

    def test_the_gate_ends_with_one_verdict_line(self) -> None:
        text = (ROOT / "scripts" / "gate.sh").read_text()
        self.assertEqual(text.count('verdict "gate: passed'), 1)
        self.assertIn('stop() { verdict "gate: refused at $1"; exit 1; }', text)


def loop_with(modules: tuple[str, ...]) -> Path:
    """A scratch folder holding a copy of scripts/fast.sh and a test package of one-test modules: loop_with(("a", "b")) gives
    test/test_a.py and test/test_b.py, each a passing test named for its module."""
    root = Path(tempfile.mkdtemp(prefix="ghost-core-loop-"))
    (root / "scripts").mkdir()
    (root / "scripts" / "fast.sh").write_text((ROOT / "scripts" / "fast.sh").read_text())
    (root / "test").mkdir()
    (root / "test" / "__init__.py").write_text("")
    for name in modules:
        (root / "test" / f"test_{name}.py").write_text(f"import unittest\n\n\nclass T(unittest.TestCase):\n    def test_{name}(self) -> None:\n        pass\n")
    return root


def loop(root: Path, args: list[str]) -> subprocess.CompletedProcess:
    """The scratch fast loop run with the arguments given: loop(root, ["test.test_a"]) runs `scripts/fast.sh test.test_a`."""
    return subprocess.run(["bash", str(root / "scripts" / "fast.sh"), *args], capture_output=True, text=True)


class TheFastLoop(unittest.TestCase):
    def test_no_argument_runs_every_module(self) -> None:
        result = loop(loop_with(("a", "b")), [])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Ran 2 tests", result.stderr)

    def test_a_module_argument_runs_that_module_only(self) -> None:
        root = loop_with(("a", "b"))
        for spelling in ("test.test_a", "test_a", "test/test_a.py"):
            with self.subTest(spelling=spelling):
                result = loop(root, [spelling])
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("Ran 1 test in", result.stderr)

    def test_two_module_arguments_run_both(self) -> None:
        result = loop(loop_with(("a", "b", "c")), ["test.test_a", "test.test_c"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr.count("Ran 1 test in"), 2)

    def test_a_module_that_does_not_exist_is_red(self) -> None:
        result = loop(loop_with(("a",)), ["test.test_typo"])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("NO TESTS RAN", result.stderr)

    def test_a_failing_module_is_red_though_a_later_one_passes(self) -> None:
        root = loop_with(("a",))
        (root / "test" / "test_red.py").write_text("import unittest\n\n\nclass T(unittest.TestCase):\n    def test_red(self) -> None:\n        self.fail()\n")
        self.assertNotEqual(loop(root, ["test.test_red", "test.test_a"]).returncode, 0)


# The steps a scratch gate (test/support_git.py gated_repo) prints, the slow tests among them when Core's gate has them.
SLOW = "test.test_stamp" in (ROOT / "scripts" / "gate.sh").read_text()
GATE_STEPS = ["the fast loop", "the key scan"] + (["the slow tests"] if SLOW else []) + ["docs/decisions.md", "docs/journal/INDEX.md", "the metrics"]


class TheTreeRecord(unittest.TestCase):
    def test_a_passing_gate_records_the_tree_it_passed_on_an_untracked_file_included(self) -> None:
        root = gated_repo()
        (root / "untracked.txt").write_text("not yet added, not ignored: it counts")
        result = gate(root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(recorded(root), gate_record.tree(root))
        self.assertTrue(gate_record.matches(root))
        head_tree = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD^{tree}"], capture_output=True, text=True).stdout.strip()
        self.assertNotEqual(recorded(root), head_tree)
        self.assertEqual(subprocess.run(["git", "-C", str(root), "status", "--porcelain"], capture_output=True, text=True).stdout, "?? untracked.txt\n")

    def test_the_terminal_shows_only_the_step_lines_and_the_verdict(self) -> None:
        root = gated_repo()
        lines = gate(root).stdout.splitlines()
        self.assertEqual([re.sub(r"\(\d+\.\d\d s\)", "(N s)", line) for line in lines[:-1]], [f"== {s}: passed (N s)" for s in GATE_STEPS])
        self.assertRegex(lines[-1], r"^gate: passed; fast loop \d+\.\d\ds, \d+\.\d\d min, 1 commits since the last tune-up$")
        log = (root / "build" / "gate.log").read_text()
        self.assertEqual("stub fast loop ran test.test_stamp" in log, SLOW)
        self.assertEqual(log.count("stub step ran"), 3)
        self.assertTrue(log.endswith(lines[-1] + "\n"))

    def test_the_verdict_counts_from_a_founding_commit_as_commit_sh_does(self) -> None:
        """4.4's leftover: "start", "stamped from Ghost-Core", "one", "two": the verdict counts two, where it counted four."""
        root = gated_repo()
        for subject in ("stamped from Ghost-Core", "one", "two"):
            subprocess.run(["git", "-C", str(root), "-c", "user.name=Ghost", "-c", "user.email=g@example.invalid", "commit", "-q", "--allow-empty", "-m", subject], check=True)
        self.assertRegex(gate(root).stdout.splitlines()[-1], r", 2 commits since the last tune-up$")

    def test_the_times_file_has_one_line_per_step(self) -> None:
        root = gated_repo()
        gate(root)
        lines = (root / "build" / "gate-times.txt").read_text().splitlines()
        self.assertEqual([line.split(" ", 1)[1] for line in lines], GATE_STEPS)
        self.assertTrue(all(re.fullmatch(r"\d+\.\d\d", line.split(" ", 1)[0]) for line in lines), lines)

    def test_a_tree_that_changes_during_the_run_is_not_recorded(self) -> None:
        root = gated_repo()
        (root / "touch-me").write_text("")
        result = gate(root)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout.splitlines()[-1], "gate: refused at the record (the tree changed while the gate ran: nothing recorded; run it again)")
        self.assertIsNone(recorded(root))

    def test_a_red_step_records_nothing_removes_an_earlier_record_and_frees_the_lock(self) -> None:
        root = gated_repo()
        self.assertEqual(gate(root).returncode, 0)
        self.assertIsNotNone(recorded(root))
        (root / "red").write_text("")
        result = gate(root)
        self.assertEqual(result.stdout.splitlines()[-1], "gate: refused at the fast loop")
        self.assertIsNone(recorded(root))
        self.assertFalse((root / ".git" / "ghost" / "lock").exists())
        self.assertEqual(len((root / "build" / "gate-times.txt").read_text().splitlines()), 1)

    def test_a_held_lock_refuses_a_second_gate_and_is_left_to_its_holder(self) -> None:
        root = gated_repo()
        (root / ".git" / "ghost" / "lock").mkdir(parents=True)
        result = gate(root)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(len(result.stdout.splitlines()), 1)
        self.assertTrue(result.stdout.startswith("gate: refused at the lock (.git/ghost/lock is held"), result.stdout)
        self.assertTrue((root / ".git" / "ghost" / "lock").is_dir())
        self.assertIsNone(recorded(root))

    def test_a_log_git_does_not_ignore_is_refused(self) -> None:
        root = gated_repo()
        (root / ".gitignore").write_text("")
        result = gate(root)
        self.assertEqual(result.stdout.splitlines()[-1], "gate: refused at the log (git does not ignore build/, so the gate's own log would change the tree)")


class TheRecordReader(unittest.TestCase):
    def cli(self, root: Path) -> subprocess.CompletedProcess:
        """gate_record.py's command line as the copy in the scratch repository runs it."""
        return subprocess.run(["python3", "-I", "scripts/checks/gate_record.py"], cwd=root, capture_output=True, text=True)

    def test_absent_matches_and_stale(self) -> None:
        root = gated_repo()
        self.assertEqual((self.cli(root).stdout, self.cli(root).returncode), ("record: absent\n", 1))
        gate(root)
        sha = recorded(root)
        self.assertEqual((self.cli(root).stdout, self.cli(root).returncode), (f"record: {sha} matches\n", 0))
        (root / "build" / "ignored.txt").write_text("ignored: no change to the tree")
        self.assertEqual(self.cli(root).returncode, 0)
        (root / "new.txt").write_text("a change")
        self.assertEqual((self.cli(root).stdout, self.cli(root).returncode), (f"record: {sha} stale\n", 1))
        self.assertFalse(gate_record.matches(root))

    def test_the_real_index_is_left_as_it_was(self) -> None:
        root = gated_repo()
        (root / "new.txt").write_text("untracked")
        before = (root / ".git" / "index").read_bytes()
        gate_record.tree(root)
        self.assertEqual((root / ".git" / "index").read_bytes(), before)
