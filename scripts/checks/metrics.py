"""The agent's metrics of docs/AGENT.md, measured from the files (scripts/metrics.py, test/test_metrics.py; C-022)."""
import json
import re
import subprocess
import sys
from pathlib import Path

from scripts.checks import ghost, journal, tables
from scripts.checks.common import matching, tracked_files

SOURCE_SUFFIXES: tuple[str, ...] = (".py", ".java", ".ts", ".tsx", ".js", ".cpp", ".cc", ".hpp", ".h", ".cs", ".go", ".rs")
TOOL_DIRS: tuple[str, ...] = ("scripts", "test")
SKIP_DIRS: tuple[str, ...] = (".git", "node_modules", ".venv", "build", "third_party", "stacks")
GENERATED: tuple[str, ...] = ("scripts/decisions_index.py", "scripts/journal_index.py")
ROUTING = ("Task", "Start here")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
DONE_LINE = re.compile(r"^Done (\d{4}-\d{2}-\d{2})(?: \(([^)]*)\))?", re.MULTILINE)
GRADE = re.compile(r"\b(?:small|mid|strong)\b")
TOOL_CALLS = re.compile(r"(?<![~\w,.])(?<!about )\d[\d,]* tool calls")


def source_dirs(root: Path) -> list[str]:
    """The project's own source folders: docs/modules.json's modules' folders; [] while there are none."""
    path = root / "docs" / "modules.json"
    if not path.is_file():
        return []
    modules = json.loads(path.read_text()).get("modules", {})
    return [entry["folder"] for entry in modules.values() if isinstance(entry, dict) and "folder" in entry]


def source_files(root: Path, tops: list[str]) -> list[Path]:
    """Every source file git tracks under the given top-level folders (C-001), skipping vendored and generated folders."""
    found: list[Path] = []
    files = tracked_files(root)
    for top in tops:
        for path in matching(files, root, f"{top}/**/*"):
            skipped = any(part in SKIP_DIRS for part in path.relative_to(root).parts)
            if path.suffix in SOURCE_SUFFIXES and not skipped:
                found.append(path)
    return found


def lines(path: Path) -> int:
    """A file's line count: a three-line file gives 3."""
    return len(path.read_text(errors="replace").splitlines())


def largest(root: Path) -> int:
    """The longest source file in lines across the modules and the tool folders; 0 when there is none."""
    return max((lines(p) for p in source_files(root, source_dirs(root) + list(TOOL_DIRS))), default=0)


def routing_files(claude: str) -> int:
    """The most files one routing row opens, counting its "Start here" cell's backticked paths; 0 with no table."""
    found = tables.headed(claude, ROUTING)
    if not found:
        return 0
    return max((len(re.findall(r"`[^`]+`", row[1])) if len(row) > 1 else 0 for row in found[0].rows), default=0)


def without_see_also(ghost_text: str) -> int:
    """Decisions whose See also line is missing or empty."""
    return sum(1 for entry in ghost.split_entries(ghost_text).values() if not ghost.fields_of(entry).get("See also"))


def stale_generated(root: Path) -> int:
    """How many generated files are stale: each generator's --check that exits non-zero."""
    stale = 0
    for script in GENERATED:
        result = subprocess.run([sys.executable, "-I", str(root / script), "--check"], capture_output=True, text=True)
        stale += result.returncode != 0
    return stale


def docs_per_source(root: Path) -> float | None:
    """Lines of the documents (root and docs/ .md) per line of the modules' source, to one decimal (3 document lines over 7 source lines gives 0.4); None while there is no source."""
    source = sum(lines(p) for p in source_files(root, source_dirs(root)))
    if source == 0:
        return None
    files = tracked_files(root)
    documents = matching(files, root, "*.md") + matching(files, root, "docs/**/*.md")
    return round(sum(lines(p) for p in documents) / source, 1)


def thresholds_set(grades: str) -> str | None:
    """The date in the first paragraph under grades.md's "## Provisional" heading, "2026-11-06"; None with none."""
    section = grades.split("\n## Provisional\n", 1)
    if len(section) < 2:
        return None
    match = DATE.search(section[1].strip().split("\n\n", 1)[0])
    return match.group(0) if match else None


def done_dates(done: str) -> dict[str, str]:
    """Each journal id DONE.md cites, with the date of the line citing it: "Done 2026-11-06 (J-043)" gives {"J-043": "2026-11-06"}."""
    dates: dict[str, str] = {}
    for match in DONE_LINE.finditer(done):
        for rid in re.findall(r"J-\d{3}", match.group(2) or ""):
            dates.setdefault(rid, match.group(1))
    return dates


def is_cost_row(cost: str) -> bool:
    """A Cost line that names a grade and an exact tool-call count: "strong grade; 52 tool calls" is one;
    "about 30 tool calls", "~40 tool calls" and "12 tool calls" with no grade are not."""
    return bool(GRADE.search(cost) and TOOL_CALLS.search(cost))


# Decision: C-036 (the grade limits and points move only by a decision made from the project's Cost rows)
def cost_rows(entries: dict[str, dict[str, str]], dates: dict[str, str], since: str | None) -> int | None:
    """Journal entries since the thresholds were set whose Cost line is a Cost row; one entry is one row, whatever
    table it carries. The window opens at the first entry, in journal order, that DONE.md dates on or after
    `since` (the journal is newest last, so every later entry is inside it); None while no date is set."""
    if since is None:
        return None
    ids = list(entries)
    start = next((i for i, rid in enumerate(ids) if dates.get(rid, "") >= since), len(ids))
    return sum(1 for rid in ids[start:] if is_cost_row(entries[rid].get("Cost", "")))


def cost_rows_in(root: Path) -> int | None:
    """cost_rows() for a repository root: its journal, docs/DONE.md and docs/when/grades.md."""
    grades, done = root / "docs" / "when" / "grades.md", root / "docs" / "DONE.md"
    since = thresholds_set(grades.read_text()) if grades.is_file() else None
    dates = done_dates(done.read_text()) if done.is_file() else {}
    return cost_rows(journal.entries(journal.journal_text(root)), dates, since)


def measure(root: Path, fast_loop: float | None, gate: float | None) -> dict[str, float | None]:
    """Every metric by its name in AGENT.md's table; the two timings are measured by the gate and passed in."""
    return {
        "Mandatory context (words)": len((root / "CLAUDE.md").read_text().split()),
        "Fast loop (s)": fast_loop,
        "Gate (min)": gate,
        "Largest source file (lines)": largest(root),
        "Files a routing row opens": routing_files((root / "CLAUDE.md").read_text()),
        "Decisions without `See also`": without_see_also((root / "theGhost.md").read_text()),
        "Stale generated files": stale_generated(root),
        "Docs lines per source line": docs_per_source(root),
        "Cost rows since the thresholds were set": cost_rows_in(root),
    }
