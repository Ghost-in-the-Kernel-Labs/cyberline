"""The next free id of a numbered record, after fetching main so two sessions do not take the same one (C-008, C-015).

Run: python3 -I scripts/next_id.py decision   → C-035
     python3 -I scripts/next_id.py journal    → J-005
     python3 -I scripts/next_id.py --help     prints this and does nothing else

Only a heading counts (`### J-009 title`, `### C-035: title`); an id named in a sentence, a header line or a
"J-001 to J-099" range is a mention and never raises the answer (ASB J-007: a mention made it answer J-100).
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def highest(text: str, prefix: str) -> int:
    """The largest number in a `### prefix-nnn` heading: highest("### C-003: a\\n### C-010: b", "C") gives 10; none gives 0."""
    found = [int(n) for n in re.findall(rf"^### {prefix}-(\d+)", text, re.MULTILINE)]
    return max(found) if found else 0


def next_id(kind: str, text: str) -> str:
    """The id after the highest in the text: next_id("journal", "### J-004 x") gives "J-005"."""
    prefix = "J" if kind == "journal" else re.search(r"^### ([A-Z]{1,3})-\d{3}:", text, re.MULTILINE).group(1)
    return f"{prefix}-{highest(text, prefix) + 1:03d}"


def main(argv: list[str]) -> int:
    """Fetches origin/main, reads the record from it, prints the next id."""
    if "-h" in argv or "--help" in argv:
        print(__doc__.strip())
        return 0
    kind = argv[0] if argv else "decision"
    subprocess.run(["git", "-C", str(ROOT), "fetch", "-q", "origin", "main"], check=False)
    paths = ["theGhost.md"] if kind == "decision" else sorted(str(p.relative_to(ROOT)) for p in (ROOT / "docs" / "journal").glob("J-*.md"))
    text = "\n".join(subprocess.run(["git", "-C", str(ROOT), "show", f"origin/main:{p}"], capture_output=True, text=True).stdout for p in paths)
    text += "\n".join((ROOT / p).read_text() for p in paths)
    print(next_id(kind, text))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
