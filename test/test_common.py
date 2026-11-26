"""A check answers from git's file list, never the disk (3.13, 4.3; C-001, Katana J-309): a file on disk that git does not
track is not read, and the same file tracked is refused. The planted breaks need a git repository, so each is built in
a scratch root here rather than under test/fixtures/broken/."""
import importlib.util
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

from scripts.checks import common, contract, ghost, glossary, journal, metrics, pointers, supply_chain
from test.support import ROOT, scratch

HAS_GIT = shutil.which("git") is not None
READABILITY = next((p for p in (ROOT / "scripts" / "checks" / "readability.py", ROOT / "stacks" / "python" / "starter" / "scripts" / "checks" / "readability.py") if p.is_file()), None)
IMPORTS = next((p for p in (ROOT / "scripts" / "checks" / "imports.py", ROOT / "stacks" / "python" / "starter" / "scripts" / "checks" / "imports.py") if p.is_file()), None)
GLOSSARY = "| Term | Means | Not |\n| --- | --- | --- |\n| **horizon** | a window | `timeframe` |\n"


def git(root: Path, args: list[str]) -> None:
    """Runs `git -C root <args>` quietly, failing the test on an error: git(root, ["add", "a.md"])."""
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True)


def repository() -> Path:
    """A scratch git repository whose docs/GLOSSARY.md is tracked and enforces `timeframe`."""
    root = scratch()
    (root / "docs" / "GLOSSARY.md").write_text(GLOSSARY)
    git(root, ["init", "-q"])
    git(root, ["add", "docs/GLOSSARY.md"])
    return root


class TheList(unittest.TestCase):
    def test_outside_git_the_tree_is_walked_but_dot_git(self) -> None:
        root = scratch()
        (root / "docs" / "a.md").write_text("a")
        (root / ".git").mkdir()
        (root / ".git" / "HEAD").write_text("ref")
        files = common.tracked_files(root)
        self.assertEqual((list(files), files.source), ([root / "docs" / "a.md"], "disk"))

    @unittest.skipUnless(HAS_GIT, "git is not installed")
    def test_in_git_only_the_tracked_files_on_disk(self) -> None:
        root = repository()
        (root / "untracked.md").write_text("u")
        (root / "gone.md").write_text("g")
        git(root, ["add", "gone.md"])
        (root / "gone.md").unlink()
        files = common.tracked_files(root)
        self.assertEqual((list(files), files.source), ([root / "docs" / "GLOSSARY.md"], "git"))
        self.assertEqual(list(common.tracked_files(root, others=True)), [root / "docs" / "GLOSSARY.md", root / "untracked.md"])

    @unittest.skipUnless(HAS_GIT, "git is not installed")
    def test_a_folder_inside_a_work_tree_is_walked(self) -> None:
        root = repository()
        (root / "docs" / "loose.md").write_text("l")
        self.assertEqual(common.tracked_files(root / "docs").source, "disk")

    def test_a_glob_reads_as_path_glob_does(self) -> None:
        root = Path("/r")
        files = [root / "CLAUDE.md", root / "docs" / "a.md", root / "docs" / "when" / "b.md", root / "docs" / "when" / "x" / "c.md"]
        self.assertEqual(common.matching(files, root, "*.md"), [root / "CLAUDE.md"])
        self.assertEqual(common.matching(files, root, "docs/when/*.md"), [root / "docs" / "when" / "b.md"])
        self.assertEqual(common.matching(files, root, "docs/**/*.md"), files[1:])


@unittest.skipUnless(HAS_GIT, "git is not installed")
class ThePlantedBreaks(unittest.TestCase):
    def test_an_untracked_alias_is_ignored_and_refused_once_tracked(self) -> None:
        root = repository()
        (root / "docs" / "NOTES.md").write_text("a timeframe\n")
        self.assertEqual(glossary.problems(root), [])
        git(root, ["add", "docs/NOTES.md"])
        self.assertEqual(glossary.problems(root), ["NOTES.md uses 'timeframe' 1 times"])

    def test_a_pointer_to_an_untracked_file_does_not_resolve(self) -> None:
        root = repository()
        (root / "CLAUDE.md").write_text("Read `docs/RULES.md`.\n")
        (root / "docs" / "RULES.md").write_text("r")
        git(root, ["add", "CLAUDE.md"])
        self.assertEqual(pointers.problems(root), ["CLAUDE.md points at docs/RULES.md, which does not exist and no open TODO item promises"])
        git(root, ["add", "docs/RULES.md"])
        self.assertEqual(pointers.problems(root), [])

    def test_an_untracked_workflow_is_ignored_and_refused_once_tracked(self) -> None:
        root = repository()
        (root / ".github" / "workflows").mkdir(parents=True)
        (root / ".github" / "workflows" / "ci.yml").write_text("on:\n  workflow_dispatch:\npermissions:\n  contents: read\njobs:\n")
        self.assertEqual(supply_chain.workflow_problems(root), [])
        git(root, ["add", ".github"])
        self.assertEqual(supply_chain.workflow_problems(root), [])
        (root / ".github" / "workflows" / "push.yml").write_text("on:\n  push:\npermissions:\n  contents: read\njobs:\n")
        self.assertEqual(supply_chain.workflow_problems(root), [])
        git(root, ["add", ".github"])
        self.assertEqual(supply_chain.workflow_problems(root), [".github/workflows/push.yml runs on push, not by hand only"])


def load_imports() -> object:
    """The Python stack's imports check from wherever it lives (the starter, or a Python project's scripts/checks/), as test_readability loads readability."""
    spec = importlib.util.spec_from_file_location("stack_imports", IMPORTS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@unittest.skipUnless(HAS_GIT, "git is not installed")
class TheLastDiskReaders(unittest.TestCase):
    """4.3: the five readers that still asked the disk read git's list; each planted untracked file changes the result."""

    def test_an_untracked_held_by_target_does_not_resolve(self) -> None:
        root = repository()
        entries = {"C-001": "### C-001: x\n- **Status:** in force\n- **Held by:** `docs/RULES.md`, `docs/when/`\n"}
        (root / "docs" / "when").mkdir()
        (root / "docs" / "when" / "a.md").write_text("a")
        (root / "docs" / "RULES.md").write_text("r")
        self.assertEqual(ghost.held_by_problems(entries, root), [
            "C-001 is held by docs/RULES.md, which does not exist and no open TODO item promises",
            "C-001 is held by docs/when/, which does not exist and no open TODO item promises"])
        git(root, ["add", "docs"])
        self.assertEqual(ghost.held_by_problems(entries, root), [])

    def test_an_untracked_journal_file_is_not_indexed(self) -> None:
        root = repository()
        (root / "docs" / "journal").mkdir()
        (root / "docs" / "journal" / "J-000-099.md").write_text("### J-001 tracked\n")
        (root / "docs" / "journal" / "J-100-199.md").write_text("### J-002 untracked\n")
        git(root, ["add", "docs/journal/J-000-099.md"])
        self.assertEqual(list(journal.entries(journal.journal_text(root))), ["J-001"])
        git(root, ["add", "docs/journal"])
        self.assertEqual(list(journal.entries(journal.journal_text(root))), ["J-001", "J-002"])

    def test_an_untracked_source_file_is_not_counted(self) -> None:
        root = repository()
        (root / "scripts").mkdir()
        (root / "scripts" / "small.py").write_text("x = 1\n")
        (root / "scripts" / "big.py").write_text("x = 1\n" * 500)
        git(root, ["add", "scripts/small.py"])
        self.assertEqual((metrics.largest(root), [p.name for p in metrics.source_files(root, ["scripts"])]), (1, ["small.py"]))
        git(root, ["add", "scripts"])
        self.assertEqual(metrics.largest(root), 500)

    def test_an_untracked_contract_reference_is_not_seen(self) -> None:
        root = repository()
        leaf = root / "src" / "leaf"
        leaf.mkdir(parents=True)
        (leaf / "a.py").write_text("# XX-01\n")
        (leaf / "b.py").write_text("# XX-09\n")
        git(root, ["add", "src/leaf/a.py"])
        document = "## XX-01 one\n"
        self.assertEqual(contract.reference_problems(document, leaf, held=True, root=root), [])
        git(root, ["add", "src"])
        self.assertEqual(contract.reference_problems(document, leaf, held=True, root=root), ["leaf/ names XX-09, which the contract does not have"])

    @unittest.skipIf(IMPORTS is None, "not a Python-stack project: the imports check is the stack's")
    def test_an_untracked_import_is_not_read(self) -> None:
        imports = load_imports()
        root = repository()
        (root / "scripts").mkdir()
        (root / "scripts" / "a.py").write_text("import os\n")
        (root / "scripts" / "b.py").write_text("import numpy\n")
        git(root, ["add", "scripts/a.py"])
        self.assertEqual(imports.problems(root), [])
        git(root, ["add", "scripts"])
        self.assertEqual(imports.problems(root), ["scripts/b.py imports numpy, which requirements.lock does not hold"])


@unittest.skipIf(READABILITY is None, "not a Python-stack project: the readability rules are the stack's")
class TheStampedReadability(unittest.TestCase):
    def test_readability_runs_as_a_script_from_a_stamped_root(self) -> None:
        root = scratch()
        (root / "scripts" / "checks").mkdir(parents=True)
        for name in ("scripts/__init__.py", "scripts/checks/__init__.py", "scripts/checks/common.py"):
            shutil.copy(ROOT / name, root / name)
        shutil.copy(READABILITY, root / "scripts" / "checks" / "readability.py")
        ran = subprocess.run([sys.executable, "-I", "scripts/checks/readability.py"], cwd=root, capture_output=True, text=True)
        self.assertEqual((ran.returncode, ran.stdout.strip()), (0, "readability: clean"), ran.stderr)

    @unittest.skipIf(IMPORTS is None, "not a Python-stack project: the imports check is the stack's")
    def test_imports_runs_as_a_script_from_a_stamped_root(self) -> None:
        root = scratch()
        (root / "scripts" / "checks").mkdir(parents=True)
        for name in ("scripts/__init__.py", "scripts/checks/__init__.py", "scripts/checks/common.py"):
            shutil.copy(ROOT / name, root / name)
        shutil.copy(IMPORTS, root / "scripts" / "checks" / "imports.py")
        ran = subprocess.run([sys.executable, "-I", "scripts/checks/imports.py"], cwd=root, capture_output=True, text=True)
        self.assertEqual((ran.returncode, ran.stdout.strip()), (0, "imports: all locked"), ran.stderr)
