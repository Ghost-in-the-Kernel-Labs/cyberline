"""Writes docs/decisions.md, one line per decision of theGhost.md, so an agent finds one without reading the log (C-008, C-013).

Run: python3 -I scripts/decisions_index.py          (writes the index)
     python3 -I scripts/decisions_index.py --check  (exit 1 when the index is stale; test/test_ghost.py uses this)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.checks import ghost  # noqa: E402

HEADER = "# Decisions, one line each\n\nWritten by `scripts/decisions_index.py` from `theGhost.md`; do not edit here. Search `### C-012` in theGhost.md for the entry.\n\n| Id | Decision | Status | subject |\n| --- | --- | --- | --- |\n"


def render(text: str) -> str:
    """The index for theGhost.md's text: a header and one table row per entry, in id order."""
    rows = []
    for rid, entry in ghost.split_entries(text).items():
        title = entry.split("\n", 1)[0].split(": ", 1)[1]
        fields = ghost.fields_of(entry)
        rows.append(f"| {rid} | {title} | {fields.get('Status', '')} | {fields.get('subject', '')} |")
    return HEADER + "\n".join(rows) + "\n"


def main(argv: list[str]) -> int:
    """Writes the index, or with --check compares it: 0 when current, 1 when stale."""
    root = Path(__file__).resolve().parent.parent
    wanted = render((root / "theGhost.md").read_text())
    index = root / "docs" / "decisions.md"
    if "--check" in argv:
        current = index.exists() and index.read_text() == wanted
        print("decisions.md is current" if current else "decisions.md is stale: run scripts/decisions_index.py")
        return 0 if current else 1
    index.write_text(wanted)
    print(f"wrote {index} with {wanted.count(chr(10)) - 6} rows")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
