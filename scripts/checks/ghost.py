"""theGhost.md's shape: ids, fields, statuses, supersessions, See also, conflicts (test/test_ghost.py).

Carried from Neon Rain's scripts/checks/ghost.py (C-008). The prefix is read from the file: a project
stamped from the template writes its own letter and changes nothing here.
"""
import re
from pathlib import Path

from scripts.checks import pointers
from scripts.checks.common import tracked_files

FIELDS: tuple[str, ...] = ("Decision", "Why", "Held by", "Source", "Status", "subject")
PLAIN_STATUSES: tuple[str, ...] = ("proposed", "in force", "withdrawn", "refused")
CORE_LINE = "part of Ghost-Core; may not apply to every project, but a rule that appears in four projects is there for a reason."
HEADING = re.compile(r"^### ([A-Z]{1,3}-\d{3}): ", re.MULTILINE)
FIELD_LINE = re.compile(r"^- \*\*([^*]+):\*\* ?(.*)$", re.MULTILINE)
CONFLICTS = re.compile(r"^- \*\*conflicts-with:\*\* (.*)$", re.MULTILINE)
PARENT_TAG = r"\b(?:SB|KT|EE|NR):|\bIn the parents:"
TAG = re.compile(r"(\bCore:|" + PARENT_TAG + ")")
BACKTICKED = re.compile(r"`([^`\s]+)`")
FENCED = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)


def prose(text: str) -> str:
    """The text with every fenced code block blanked, so an example entry in one is not an entry."""
    return FENCED.sub("", text)


def prefix_of(text: str) -> str:
    """The letters before the dash in the first entry's id: "### C-001: x" gives "C"; no entry gives "C"."""
    match = HEADING.search(text)
    return match.group(1).split("-")[0] if match else "C"


def split_entries(text: str) -> dict[str, str]:
    """The entries by id, each its text up to the next heading; a duplicated id keeps its last text.

    For "### C-001: a\\nbody\\n### C-002: b\\n" it returns {"C-001": "### C-001: a\\nbody\\n", "C-002": ...}.
    """
    text = prose(text)
    headings = list(HEADING.finditer(text))
    bounds = [m.start() for m in headings] + [len(text)]
    return {m.group(1): text[bounds[i]:bounds[i + 1]] for i, m in enumerate(headings)}


def fields_of(entry: str) -> dict[str, str]:
    """An entry's `- **Name:** value` lines as {name: first line of value}."""
    return {m.group(1): m.group(2).strip() for m in FIELD_LINE.finditer(entry)}


def id_problems(text: str) -> list[str]:
    """Ids duplicated or out of sequence, per prefix: C-001, C-002, ... with no gap; a stamped project's own
    prefix starts its own sequence after the inherited C- entries, and no third prefix is allowed."""
    ids = HEADING.findall(prose(text))
    problems = [f"{rid} appears {ids.count(rid)} times" for rid in sorted(set(ids)) if ids.count(rid) > 1]
    prefixes: list[str] = []
    for rid in ids:
        if rid.split("-")[0] not in prefixes:
            prefixes.append(rid.split("-")[0])
    if len(prefixes) > 2:
        problems.append(f"three prefixes in one log: {prefixes}; the core's C- and the project's own are all there can be")
    for prefix in prefixes:
        own = [rid for rid in ids if rid.startswith(prefix + "-")]
        for position, rid in enumerate(own, start=1):
            if rid != f"{prefix}-{position:03d}":
                problems.append(f"entry {position} of {prefix}- is {rid}, expected {prefix}-{position:03d}")
                break
    return problems


def status_problem(rid: str, status: str, entries: dict[str, str]) -> str | None:
    """What is wrong with one entry's status, or None: one of the five words, a supersession two-sided."""
    if status in PLAIN_STATUSES:
        return None
    match = re.match(r"^superseded by ([A-Z]{1,3}-\d{3})$", status)
    if match is None:
        return f"{rid} has status {status!r}, not one of the five"
    successor = match.group(1)
    if successor not in entries:
        return f"{rid} is superseded by {successor}, which does not exist"
    if rid not in fields_of(entries[successor]).get("Supersedes", ""):
        return f"{rid} is superseded by {successor}, whose Supersedes line does not name it"
    return None


def see_also_problems(rid: str, fields: dict[str, str], entries: dict[str, str]) -> list[str]:
    """Each id a See also line names that is no entry: See also "C-009, C-099" with no C-099 gives one problem."""
    named = re.findall(r"[A-Z]{1,3}-\d{3}", fields.get("See also", ""))
    own_prefix = rid.split("-")[0]
    return [f"{rid} sees also {other}, which does not exist" for other in named if other.startswith(own_prefix) and other not in entries]


def core_problem(rid: str, fields: dict[str, str]) -> str | None:
    """A Core line that is present but not the one sentence, or None."""
    if "Core" in fields and fields["Core"] != CORE_LINE:
        return f"{rid} has a Core line that is not the Core sentence"
    return None


def entry_problems(entries: dict[str, str]) -> list[str]:
    """Missing fields, bad statuses, dangling See also and wrong Core lines, entry by entry."""
    problems: list[str] = []
    for rid, entry in entries.items():
        fields = fields_of(entry)
        problems += [f"{rid} has no {name} line" for name in FIELDS if name not in fields]
        problem = status_problem(rid, fields["Status"], entries) if "Status" in fields else None
        problems += [problem] if problem else []
        problems += see_also_problems(rid, fields, entries)
        problem = core_problem(rid, fields)
        problems += [problem] if problem else []
    return problems


# Decision: C-008 (two in-force decisions on one subject that say they conflict cannot both stand)
def conflict_problems(entries: dict[str, str]) -> list[str]:
    """In-force pairs on one subject where one names the other on a `conflicts-with:` line; a name that is no entry."""
    problems: list[str] = []
    for rid, entry in entries.items():
        fields = fields_of(entry)
        named = [other for line in CONFLICTS.findall(entry) for other in re.findall(r"[A-Z]{1,3}-\d{3}", line)]
        for other in named:
            if other not in entries:
                problems.append(f"{rid} conflicts with {other}, which does not exist")
                continue
            both = fields.get("Status") == fields_of(entries[other]).get("Status") == "in force"
            if both and fields_of(entries[other]).get("subject") == fields.get("subject"):
                problems.append(f"{rid} and {other} are both in force on {fields.get('subject')!r} and conflict")
    return problems


def our_segments(held_by: str) -> list[str]:
    """The segments of a Held by line that name this repository's files: the text before the first tag, and each
    segment after a `Core:` tag up to the next tag; a parent's segment (SB:, KT:, EE:, NR:, "In the parents:") is not ours.

    "`a.md`. SB: `b.ts`. Core: `c.py`. NR: `d.py`" gives ["`a.md`. ", " `c.py`. "].
    """
    parts = TAG.split(held_by)
    return [parts[0]] + [parts[i + 1] for i in range(1, len(parts) - 1, 2) if parts[i] == "Core:"]


def held_paths(held_by: str) -> list[str]:
    """The paths of this repository a Held by line names: each backticked token in one of our segments that
    pointers.py's grammar reads as a path (git refs, scoped packages, URLs and commands are not paths).

    "`docs/x.md`, `npm test`, `origin/main`. SB: `src/a.ts`. Core: `test/t.py`" gives ["docs/x.md", "test/t.py"].
    """
    return [t for segment in our_segments(held_by) for t in BACKTICKED.findall(segment) if pointers.is_path(t)]


def tracked_paths(root: Path) -> set[str]:
    """Every file git tracks under root and every folder above one, relative and without a trailing slash (C-001: a clone's
    files, never the disk's): a tracked docs/journal/J-000-099.md gives {"docs/journal/J-000-099.md", "docs/journal", "docs"}."""
    found: set[str] = set()
    for path in tracked_files(root):
        rel = path.relative_to(root)
        found |= {rel.as_posix(), *(parent.as_posix() for parent in rel.parents if parent.parts)}
    return found


# Decision: C-008 (every file a Held by names exists, or an open TODO item promises it)
def held_by_problems(entries: dict[str, str], root: Path) -> list[str]:
    """Each path an in-force entry's Held by names that is neither under root nor promised by an open TODO item."""
    todo = (root / "TODO.md").read_text() if (root / "TODO.md").is_file() else ""
    allowed = pointers.promised(todo)
    present = tracked_paths(root)
    found: list[str] = []
    for rid, entry in entries.items():
        fields = fields_of(entry)
        if fields.get("Status") != "in force":
            continue
        for path in held_paths(fields.get("Held by", "")):
            if path.rstrip("/") not in present and path not in allowed:
                found.append(f"{rid} is held by {path}, which does not exist and no open TODO item promises")
    return found


def problems(text: str, root: Path | None = None) -> list[str]:
    """Everything wrong with theGhost.md's text; [] when it holds. With a root, the Held by paths are checked too."""
    entries = split_entries(text)
    found = id_problems(text) + entry_problems(entries) + conflict_problems(entries)
    return found + (held_by_problems(entries, root) if root is not None else [])
