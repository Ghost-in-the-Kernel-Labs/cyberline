"""Place each open TODO.md item at a grade from facts, with no model: one line per item (C-036).

    python3 -I scripts/score.py

Each line: `<n.n> <grade> (<model>, <tool calls>), <points> points — <facts>; rows: <routing rows>`, or
`<n.n> unplaced — ...` for an item that names no file. The points, the grades and the floor are docs/when/grades.md's;
the logic is scripts/checks/score.py. Exits 1, naming what is missing, when the grade map cannot place.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.checks import metrics, score  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SKIPPED: tuple[str, ...] = (".git", "node_modules", ".venv", "build", "__pycache__", "mutants", ".stryker-tmp", "dist")


def text_of(relative: str) -> str:
    """A file's text under the root, or "" when it does not exist: text_of("docs/CONTRACT.md")."""
    path = ROOT / relative
    return path.read_text(errors="replace") if path.is_file() else ""


def sizes(root: Path) -> dict[str, int]:
    """Every file's size in characters by its path from the root, skipping vendored, built and cached folders:
    {"TODO.md": 2412, ...}."""
    found: dict[str, int] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if path.is_file() and not any(part in SKIPPED for part in relative.parts):
            found[relative.as_posix()] = len(path.read_text(errors="replace"))
    return found


def main() -> int:
    """Prints one line per open item; 1 when the grade map is missing a table, a fact's points or a floor."""
    rules = score.grade_map(text_of("docs/when/grades.md"))
    problems = score.map_problems(rules)
    for problem in problems:
        print(f"score: {problem}")
    if problems:
        return 1
    claude = text_of("CLAUDE.md")
    rows = score.routing_rows(claude) + [row for path in score.workpaths(claude) for row in score.routing_rows(text_of(path))]
    prefixes = score.prefixes(text_of("theGhost.md"), text_of("docs/CONTRACT.md"))
    for line in score.report(text_of("TODO.md"), rules, rows, sizes(ROOT), metrics.source_dirs(ROOT), prefixes):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
