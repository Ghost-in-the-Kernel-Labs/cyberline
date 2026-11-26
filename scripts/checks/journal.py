"""The journal's entries: numbered in order across its files, a known class, every field present, every
open conflict listed for Ghost in docs/HANDOFF.md (test/test_journal.py; C-015, C-029)."""
import re
from pathlib import Path

from scripts.checks.common import matching, tracked_files

CLASSES: tuple[str, ...] = (
    "contradiction", "ambiguity", "failure-caught", "failure-missed", "decision", "measurement", "direction",
    "trial", "deferred", "conflict", "feature",
)
FIELDS: tuple[str, ...] = ("Who", "Class", "Intent", "Found", "Options", "Resolved", "Touched", "Caught by", "Cost")
HEADING = re.compile(r"^### (J-\d{3}) ", re.MULTILINE)
FIELD = re.compile(r"^- \*\*([^*]+)\*\*: ?(.*)$", re.MULTILINE)


def journal_text(root: Path) -> str:
    """The journal's files under docs/journal/ that git tracks (C-001), in name order, joined: J-000-099.md then J-100-199.md."""
    files = matching(tracked_files(root), root, "docs/journal/J-*.md")
    return "\n".join(path.read_text() for path in files)


def entries(journal: str) -> dict[str, dict[str, str]]:
    """Each entry's fields by id: "### J-001 x\\n- **Class**: trial\\n" gives {"J-001": {"Class": "trial"}}."""
    heads = list(HEADING.finditer(journal))
    bounds = [m.start() for m in heads] + [len(journal)]
    return {m.group(1): dict(FIELD.findall(journal[bounds[i]:bounds[i + 1]])) for i, m in enumerate(heads)}


def number_problems(journal: str) -> list[str]:
    """Ids J-001, J-002, ... each once, in order; the first break only."""
    for position, found in enumerate(HEADING.findall(journal), start=1):
        if found != f"J-{position:03d}":
            return [f"entry {position} is {found}, expected J-{position:03d}"]
    return []


def waiting_on_ghost(handoff: str) -> str:
    """The text of HANDOFF.md's "For Ghost" section, up to the next heading; "" if there is none."""
    return "".join(re.findall(r"^## For Ghost.*?(?=^## |\Z)", handoff, flags=re.MULTILINE | re.DOTALL))


# Decision: C-029 (a conflict goes to Ghost at once, both objectives stated; open until Ghost resolves it)
def conflict_problems(fields: dict[str, str], entry: str, queue: str) -> list[str]:
    """One conflict entry: both objectives written, and, unless Ghost resolved it, listed for Ghost."""
    found = [f"{entry} is a conflict with no {name} objective" for name in ("Mine", "Theirs") if not fields.get(name)]
    if "Ghost" not in str(fields.get("Resolved")) and entry not in queue:
        found.append(f"{entry} is an open conflict not listed in HANDOFF.md's For Ghost section")
    return found


def problems(journal: str, handoff: str) -> list[str]:
    """Everything wrong with the journal given the handoff; [] when it holds."""
    found = number_problems(journal)
    queue = waiting_on_ghost(handoff)
    for entry, fields in entries(journal).items():
        found += [f"{entry} has no {name} line" for name in FIELDS if not fields.get(name)]
        kind = fields.get("Class", "")
        if kind not in CLASSES:
            found.append(f"{entry} has class {kind!r}, not one of {len(CLASSES)}")
        if kind == "conflict":
            found += conflict_problems(fields, entry, queue)
    return found


def problems_in(root: Path) -> list[str]:
    """problems() for a repository root."""
    return problems(journal_text(root), (root / "docs" / "HANDOFF.md").read_text())
