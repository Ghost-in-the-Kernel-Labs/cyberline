"""Writes docs/journal/INDEX.md, one line per journal entry, so an entry is found without reading the files (C-015).

Run: python3 -I scripts/journal_index.py          (writes)
     python3 -I scripts/journal_index.py --check  (exit 1 when stale)
     python3 -I scripts/journal_index.py --help   prints this and writes nothing
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.checks import journal  # noqa: E402
from scripts.checks.common import matching, tracked_files  # noqa: E402

HEADER = "# Journal: the index\n\nWritten from `docs/journal/` by `scripts/journal_index.py`; do not edit by hand. The fields and the rules are in `docs/JOURNAL.md`.\n\n| Entry | Title | Class | File |\n| --- | --- | --- | --- |\n"


def render(root: Path) -> str:
    """The index: one row per entry across the journal's files git tracks (C-001; as journal.py reads them), in id order."""
    lines = []
    for path in matching(tracked_files(root), root, "docs/journal/J-*.md"):
        text = path.read_text()
        for rid, fields in journal.entries(text).items():
            title = re.search(rf"^### {rid} (.*)$", text, re.MULTILINE).group(1)
            lines.append(f"| {rid} | {title} | {fields.get('Class', '')} | `{path.name}` |")
    return HEADER + "\n".join(lines) + "\n"


def current(root: Path) -> bool:
    """True when root's docs/journal/INDEX.md holds exactly what render(root) gives; reads, never writes."""
    index = root / "docs" / "journal" / "INDEX.md"
    return index.exists() and index.read_text() == render(root)


def main(argv: list[str]) -> int:
    """Writes the index, or with --check compares it: 0 when current, 1 when stale."""
    if "-h" in argv or "--help" in argv:
        print(__doc__.strip())
        return 0
    root = Path(__file__).resolve().parent.parent
    if "--check" in argv:
        fresh = current(root)
        print("journal INDEX.md is current" if fresh else "journal INDEX.md is stale: run scripts/journal_index.py")
        return 0 if fresh else 1
    index = root / "docs" / "journal" / "INDEX.md"
    index.write_text(render(root))
    print(f"wrote {index}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
