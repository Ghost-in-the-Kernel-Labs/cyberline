"""Every backticked path in the routing documents exists, or an open TODO item names it (test/test_pointers.py; C-021).

Governs CLAUDE.md, docs/when/*.md and docs/paths/*.md: the files an agent is routed by. A path that
does not exist yet is allowed only while an open item of TODO.md names it in backticks; when the
item moves to DONE.md the allowance ends and the pointer must resolve.

The same check runs in every stamped project, which inherits these documents and every in-force
decision but none of this repository's TODO items, and lacks the files the stamp leaves behind. So a
routing document or a core decision names a parent's file, a Core-only file (the surveys) or a file a
Core item merely promises in plain text, never in backticks; only a path a stamped project will have is
a pointer. A stamped project's fast loop is where the difference shows (test/test_stamp.py).

It reads git's file list (scripts/checks/common.py; C-001): a routing document git does not track is not read, and a
pointer to a file on disk that git does not track does not resolve, since a clone would not hold it (Katana J-309).
"""
import re
from pathlib import Path

from scripts.checks.common import matching, tracked_files

# The one path grammar: this check reads it, and so does ghost.py's Held-by check (one list of endings, not two).
ENDINGS = "md|py|sh|json|yml|yaml|toml|txt|lock|mjs|ts|java"
FILE = r"(?:[\w.-]+/)*[\w-][\w.-]*\.(?:" + ENDINGS + ")"
PATH = re.compile(r"`(" + FILE + ")`")
PATH_TOKEN = re.compile(FILE + r"|(?:[\w-][\w.-]*/)+")
NOT_PATHS = ("origin/", "refs/", "@")


def is_path(token: str) -> bool:
    """A backticked token names a file or folder of a repository: "docs/a.md" and "docs/when/" are paths; a git ref
    ("origin/main"), a scoped package ("@scope/pkg"), a URL ("https://x/y.md") and a command ("npm test") are not."""
    if "://" in token or token.startswith(NOT_PATHS):
        return False
    return PATH_TOKEN.fullmatch(token) is not None


def routing_documents(root: Path, files: list[Path]) -> list[Path]:
    """Of the files given, CLAUDE.md if present, then every .md under docs/when/ and docs/paths/, sorted."""
    found = matching(files, root, "CLAUDE.md")
    for folder in ("when", "paths"):
        found += matching(files, root, f"docs/{folder}/*.md")
    return found


def pointed(text: str) -> list[str]:
    """The paths in backticks, each once, in order: "see `docs/a.md` and `docs/a.md`" gives ["docs/a.md"]."""
    seen: list[str] = []
    for path in PATH.findall(text):
        if path not in seen:
            seen.append(path)
    return seen


def promised(todo: str) -> set[str]:
    """The paths an open TODO item names: "Check: `scripts/gate.sh` ends…" gives {"scripts/gate.sh"}."""
    return set(PATH.findall(todo))


def problems(root: Path) -> list[str]:
    """Each pointer in a routing document to a file that git neither tracks nor an open TODO.md item promises."""
    todo = (root / "TODO.md").read_text() if (root / "TODO.md").is_file() else ""
    allowed = promised(todo)
    files = tracked_files(root)
    present = {path.relative_to(root).as_posix() for path in files}
    found: list[str] = []
    for document in routing_documents(root, files):
        for path in pointed(document.read_text()):
            if path not in present and path not in allowed:
                found.append(f"{document.relative_to(root)} points at {path}, which does not exist and no open TODO item promises")
    return found
