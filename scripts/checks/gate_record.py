"""The tree record (C-037): the SHA of the working tree the gate last passed on, in .git/ghost/tree, never committed.

    python3 -I scripts/checks/gate_record.py          prints `record: <sha> matches`, `record: <sha> stale` or
                                                      `record: absent`; exits 0 only when the record matches the tree
    python3 -I scripts/checks/gate_record.py --tree   prints the working tree's SHA, as scripts/gate.sh takes it before
                                                      its first step and after its last

The working tree's SHA is `git write-tree` from a temporary index holding every file git does not ignore (a copy of the
real index brought up to date by `git add -A`, so an untracked file counts and a tracked one stays); the real index is
never touched. scripts/gate.sh writes the record; scripts/commit.sh (TODO 3.7) and scripts/ship.sh (TODO 3.8) read it.
"""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def git(root: Path, args: list[str], index: Path | None = None) -> str:
    """git's output, stripped, run in root with an optional index file: git(ROOT, ["rev-parse", "--git-dir"]) gives ".git"."""
    env = dict(os.environ, GIT_INDEX_FILE=str(index)) if index else None
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True, env=env).stdout.strip()


def ghost_dir(root: Path) -> Path:
    """The folder that holds the record and the lock: /repo/.git/ghost for a repository at /repo."""
    return (root / git(root, ["rev-parse", "--git-dir"])).resolve() / "ghost"


def tree(root: Path) -> str:
    """The SHA of every file git does not ignore, as it stands on disk; the real index is left as it was."""
    scratch = Path(tempfile.mkdtemp(prefix="ghost-tree-"))
    try:
        index = scratch / "index"
        real = root / git(root, ["rev-parse", "--git-path", "index"])
        if real.is_file():
            shutil.copyfile(real, index)  # its stat cache saves rehashing; `add -A` brings it up to date
        git(root, ["add", "-A"], index)
        return git(root, ["write-tree"], index)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)


def record(root: Path) -> str | None:
    """The SHA the last passing gate recorded, or None when there is none (a red, interrupted or never-run gate)."""
    path = ghost_dir(root) / "tree"
    text = path.read_text().strip() if path.is_file() else ""
    return text or None


def matches(root: Path) -> bool:
    """Whether the record is the tree as it stands now: False when absent, or when a file changed since the gate passed."""
    recorded = record(root)
    return recorded is not None and recorded == tree(root)


def main(argv: list[str]) -> int:
    """The command line: `--tree` prints the tree's SHA; no argument prints the record's state, exit 0 only on `matches`."""
    if argv == ["--tree"]:
        print(tree(ROOT))
        return 0
    recorded = record(ROOT)
    if recorded is None:
        print("record: absent")
        return 1
    state = "matches" if recorded == tree(ROOT) else "stale"
    print(f"record: {recorded} {state}")
    return 0 if state == "matches" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
