"""The files a check reads: git's list, never the disk (C-001; LESSONS-2026-11 Part 2 row 18, Katana J-309).

A doc check that asked the disk passed on the gate's machine, where a corpus was hard-linked in, and failed on every
clean clone: CI was red for 44 runs over six days and nothing noticed. A check reads what a clone would hold, so a file
present on disk and absent from git is not read, and a pointer to it does not resolve.

tracked_files(root) answers from `git ls-files` (the index: what the next commit holds, since `scripts/commit.sh -a`
stages before its fast loop) when root is the top of a work tree; with `others=True` it adds the untracked files git
does not ignore. Outside git (no git, or root not a work tree's top: a fixture folder, a scratch root, a stamp made with
--no-git) it walks the tree, skipping `.git`, and prints nothing; the list's `source` says which answered.
"""
import fnmatch
import subprocess
from pathlib import Path


class Files(list):
    """Paths under a root, sorted, each a file on disk, with `source`: "git" when git's list answered, "disk" when the
    tree was walked. Files([Path("/r/a.md")], "git").source gives "git"."""

    def __init__(self, paths: list[Path], source: str) -> None:
        """The list of paths and where it came from."""
        super().__init__(paths)
        self.source = source


def git_listed(root: Path, others: bool) -> list[str] | None:
    """The names `git ls-files -z` prints under root (with --others --exclude-standard when others), or None when git is
    missing, fails, or root is not the top of a work tree: ["README.md", "docs/a.md"]."""
    if not (root / ".git").exists():
        return None
    extra = ["--others", "--exclude-standard"] if others else []
    try:
        listed = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--cached", *extra], capture_output=True)
    except FileNotFoundError:
        return None
    if listed.returncode != 0:
        return None
    return [name for name in listed.stdout.decode("utf-8", "replace").split("\0") if name]


def tracked_files(root: Path, others: bool = False) -> Files:
    """Every file git tracks under root that is on disk, as root / name, sorted; outside git every file under root but
    .git's. A file deleted from disk but still in the index is left out: a check reads files, and it is gone."""
    names = git_listed(root, others)
    if names is None:
        walked = [p for p in root.rglob("*") if p.is_file() and ".git" not in p.relative_to(root).parts]
        return Files(sorted(walked), "disk")
    return Files(sorted({root / name for name in names if (root / name).is_file()}), "git")


def parts_match(parts: tuple[str, ...], pattern: tuple[str, ...]) -> bool:
    """A relative path's parts against a glob's, as Path.glob reads it: `*` within one part, `**` any number of parts.
    parts_match(("docs", "a", "b.md"), ("docs", "**", "*.md")) gives True; ("docs", "*.md") gives False."""
    if not pattern:
        return not parts
    if pattern[0] == "**":
        return any(parts_match(parts[i:], pattern[1:]) for i in range(len(parts) + 1))
    return bool(parts) and fnmatch.fnmatchcase(parts[0], pattern[0]) and parts_match(parts[1:], pattern[1:])


def matching(files: list[Path], root: Path, pattern: str) -> list[Path]:
    """The files whose path relative to root matches a glob, in the list's order: matching(files, root, "docs/when/*.md")
    is what sorted(root.glob("docs/when/*.md")) gave, read from the list instead of the disk."""
    wanted = tuple(pattern.split("/"))
    return [path for path in files if parts_match(path.relative_to(root).parts, wanted)]
