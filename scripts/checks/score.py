"""Each open TODO.md item placed at a grade from facts, with no model (scripts/score.py prints it; test/test_score.py;
C-036, the working set of C-022).

The facts come from the item's own text and the routing: the files it names (backticked paths); the routing rows
whose Start-here or Tests paths cover one of them, in CLAUDE.md's table and in the workpath tables CLAUDE.md's rows
start at (`docs/paths/<name>.md`); the working set, characters / 4 of those rows' Start-here files plus the named
files, each file once; the code layers it names (a module folder `docs/modules.json` names, or `scripts/`); a
decision id (the core's C- or the project's own prefix), an invariant id, or a protected file (one whose change is Ghost's: theGhost.md, the roadmap, the contract, the module map, the agents, the workflows); a `Check:` line naming
something runnable; and whether it waits on Ghost. The points, the grades' most points, their models and tool-call
limits, and the floor are read from `docs/when/grades.md` (provisional there). Every function here is pure over text
and a map of file sizes; the command line reads the files. Carried from Neon Rain's scripts/checks/token_score.py.
"""
import re
from dataclasses import dataclass

from scripts.checks import contract, ghost, metrics, tables, todo

NAME = re.compile(r"`([^`]+)`")
PATH = re.compile(r"^[\w.<>*-]+(?:/[\w.<>*-]*)*$")
EXTENSION = re.compile(r"\.(?:py|md|json|tsv|toml|lock|sh|mjs|ts|java|txt|yml)$")
WILDCARD = re.compile(r"<[^<>/]+>|\*")
# Decision: C-036 (Ghost waits: Neon Rain's two patterns, R-039, as they are)
WAITS = re.compile(r"\b(?:waits? on|asks?|goes to) Ghost\b|\bGhost(?:'s)? (?:call|decides|word|answer|approval|approves|choice)\b")
RUNNABLE = re.compile(r"^(?:test/|scripts/)")
FLOOR = re.compile(r"^Floor: (\w+)\s*$", re.MULTILINE)
GRADE_HEADER = ("Grade", "Model")
POINTS_HEADER = ("Fact", "Per", "Points")
FACTS: tuple[str, ...] = ("working set", "layer", "contract", "mechanical")
CHARS_PER_TOKEN = 4
# Decision: C-008, C-012, C-032, C-034 (a change to one of these is a decision, a contract or a supply-chain change)
PROTECTED: tuple[str, ...] = ("theGhost.md", "docs/ROADMAP.md", "docs/CONTRACT.md", "docs/modules.json", ".claude/", ".github/")


@dataclass(frozen=True)
class Grade:
    """One row of the grade map that takes items; most_points and tool_calls are None for "no limit"."""

    name: str
    model: str
    most_points: int | None
    tool_calls: int | None


@dataclass(frozen=True)
class GradeMap:
    """The grade map as the score reads it: the grades that take items, cheapest first; the points per fact by
    FACTS' names ("working set" is points per `per` tokens); the floor's name, None when the file has none."""

    ladder: tuple[Grade, ...]
    points: dict[str, int]
    per: int
    floor: str | None


@dataclass(frozen=True)
class Facts:
    """What the score reads of one item; rows are the routing rows' tasks, tokens the working set's size."""

    files: tuple[str, ...]
    rows: tuple[str, ...]
    tokens: int
    layers: tuple[str, ...]
    contracts: tuple[str, ...]
    protected: tuple[str, ...]
    mechanical: bool
    waits: bool


def number(cell: str) -> int | None:
    """A cell's whole number, sign kept: "1,200" gives 1200, "−2" gives -2; "no limit" or "—" gives None."""
    digits = cell.replace(",", "").replace("−", "-").strip()
    return int(digits) if re.fullmatch(r"-?\d+", digits) else None


def ladder(rows: list[list[str]]) -> tuple[Grade, ...]:
    """The grades that take items, from the map's rows under its header: a row whose Most points cell is a number
    or "no limit" ("| ruling | Claude Fable | — | — |" takes none and is left out)."""
    kept = [row for row in rows if len(row) > 3 and (number(row[2]) is not None or row[2] == "no limit")]
    return tuple(Grade(row[0].lower(), row[1], number(row[2]), number(row[3])) for row in kept)


def grade_map(text: str) -> GradeMap:
    """docs/when/grades.md read: the table headed Grade | Model, the table headed Fact | Per | Points, the Floor line.
    A missing table gives an empty ladder or no points; map_problems names what is missing."""
    grades = next((ladder(table.rows) for table in tables.headed(text, GRADE_HEADER)), ())
    rows = next((table.rows for table in tables.headed(text, POINTS_HEADER)), [])
    points = {row[0].lower(): number(row[2]) for row in rows if len(row) > 2 and number(row[2]) is not None}
    per = next((number(row[1].split()[0]) for row in rows if row[0].lower() == "working set" and row[1]), None)
    floor = FLOOR.search(text)
    return GradeMap(grades, points, per or 0, floor.group(1).lower() if floor else None)


def map_problems(found: GradeMap) -> list[str]:
    """What the score cannot place by: no grades, a fact with no points, no tokens per point, a floor that is not a
    grade; [] for a whole map."""
    problems = [] if found.ladder else ["the grade map has no table headed Grade | Model with a grade that takes items"]
    problems += [f"the grade map gives no points for {fact!r} (a row of the table Fact | Per | Points)" for fact in FACTS if fact not in found.points]
    problems += [] if found.per > 0 else ["the grade map's working set row gives no tokens per point in its Per cell"]
    names = [grade.name for grade in found.ladder]
    problems += [] if found.floor in names else [f"the grade map's Floor line names {found.floor!r}, not one of {names}"]
    return problems


def paths(text: str) -> list[str]:
    """The backticked names in text that are paths, in order, each once: "`scripts/x/` and `TODO.md`, `-v`" gives
    ["scripts/x/", "TODO.md"]."""
    named = [name for name in NAME.findall(text) if PATH.match(name) and ("/" in name or EXTENSION.search(name))]
    return list(dict.fromkeys(named))


def pattern(name: str) -> re.Pattern[str]:
    """A routing name as a pattern, each `<word>` one path segment's part and each `*` any part of one, empty included:
    "stacks/<language>/README.md" matches "stacks/java/README.md", "docs/when/*.md" matches "docs/when/tune-up.md"."""
    parts = re.split(r"(<[^<>/]+>|\*)", name)
    return re.compile("".join(("[^/]*" if part == "*" else "[^/]+") if WILDCARD.fullmatch(part) else re.escape(part) for part in parts))


def covers(row_name: str, path: str) -> bool:
    """A routing row's name covers a named path: the same (wildcards read), one inside the other's folder, the same
    file name ("README.md" covers "a/README.md"), or, for a pattern row naming a file, its folder and the files directly
    in it: "stacks/<language>/README.md" covers "stacks/java/" and "stacks/java/gate.sh", "docs/when/*.md" covers
    "docs/when/" and "docs/when/tune-up.md", and neither covers a level further down."""
    if pattern(row_name).fullmatch(path) or path.endswith(f"/{row_name}"):
        return True
    inside = pattern(row_name[: row_name.rindex("/") + 1]).match(path) if WILDCARD.search(row_name) and "/" in row_name else None
    if inside and "/" not in path[inside.end():]:
        return True
    return (row_name.endswith("/") and path.startswith(row_name)) or (path.endswith("/") and row_name.startswith(path))


def routing_rows(text: str) -> list[tuple[str, list[str], list[str]]]:
    """Each routing row of a document's tables headed Task | Start here (metrics.ROUTING, as AGT-04 reads them):
    (task, its Start-here paths, its Start-here and Tests paths together)."""
    found = []
    for table in tables.headed(text, metrics.ROUTING):
        for row in table.rows:
            start = paths(row[1]) if len(row) > 1 else []
            found.append((row[0], start, start + (paths(row[3]) if len(row) > 3 else [])))
    return found


def workpaths(claude: str) -> list[str]:
    """The workpath files CLAUDE.md's rows start at, whose own rows are routing too: ["docs/paths/process.md"]."""
    return list(dict.fromkeys(p for _, start, _ in routing_rows(claude) for p in start if re.fullmatch(r"docs/paths/[\w.-]+\.md", p)))


def files_of(name: str, sizes: dict[str, int]) -> list[str]:
    """The files a name opens: a file itself; a folder the files directly in it; a pattern or a name not yet built
    nothing (the pattern's files are the item's own named ones, counted as named)."""
    if name in sizes:
        return [name]
    folder = name.rstrip("/") + "/"
    return sorted(k for k in sizes if k.startswith(folder) and "/" not in k[len(folder):]) if not WILDCARD.search(name) else []


def layer(path: str, folders: list[str]) -> str | None:
    """The code layer a path is in: a module's folder ("src/leaf/a.py" with folders ["src/leaf"] gives "src/leaf"),
    or "scripts" for a file under scripts/; tests and documents none."""
    inside = [folder for folder in folders if path == folder or path.startswith(folder.rstrip("/") + "/")]
    if inside:
        return inside[0]
    return "scripts" if path.startswith("scripts/") and path != "scripts/" else None


def check_names(body: str) -> list[str]:
    """The backticked names of the item's `Check:` line and the lines continuing it; [] without one."""
    found = re.search(r"^Check:.*?(?=^\S+:|\Z)", body, flags=re.MULTILINE | re.DOTALL)
    return NAME.findall(found.group(0)) if found else []


def contract_ids(body: str, prefixes: list[str]) -> tuple[str, ...]:
    """The decision and invariant ids the body names, each once: "C-036 and XX-02" with ["C", "XX"] gives both."""
    if not prefixes:
        return ()
    return tuple(dict.fromkeys(re.findall(rf"\b(?:{'|'.join(map(re.escape, prefixes))})-\d+\b", body)))


def prefixes(ghost_text: str, contract_text: str) -> list[str]:
    """The id prefixes a contract id may carry: the core's C, the project's own from theGhost.md's headings, and the
    invariants' from the contract document: a log with "### NR-001: x" and a contract with "## HAR-01 y" gives
    ["C", "NR", "HAR"]."""
    own = [rid.split("-")[0] for rid in ghost.HEADING.findall(ghost_text)]
    return list(dict.fromkeys(["C"] + own + [contract.prefix_of(contract_text)]))


def facts(body: str, rows: list[tuple[str, list[str], list[str]]], sizes: dict[str, int], folders: list[str], prefixes: list[str]) -> Facts:
    """The facts of one item from its body (heading to the next heading), the routing rows, the files' sizes in
    characters, the module folders and the id prefixes."""
    named = paths(body)
    matched = [(task, start) for task, start, every in rows if any(covers(n, p) for n in every for p in named)]
    opened = [f for _, start in matched for name in start for f in files_of(name, sizes)] + [f for name in named for f in files_of(name, sizes)]
    tokens = sum(sizes[f] for f in dict.fromkeys(opened)) // CHARS_PER_TOKEN
    layers = tuple(dict.fromkeys(found for found in (layer(p, folders) for p in named) if found))
    protected = tuple(p for p in named if any(covers(pin, p) or p.startswith(pin) for pin in PROTECTED))
    runnable = any(RUNNABLE.match(name) for name in check_names(body))
    return Facts(tuple(named), tuple(task for task, _ in matched), tokens, layers, contract_ids(body, prefixes), protected,
                 runnable, bool(WAITS.search(body)))


def score(found: Facts, rules: GradeMap) -> tuple[int, list[str]]:
    """The points, floored at 0, and the parts that made them: "working set 12,000 tokens (+1)" and the like."""
    parts = [(f"working set {found.tokens:,} tokens", found.tokens // rules.per * rules.points["working set"]),
             (f"layers {', '.join(found.layers)}", max(0, len(found.layers) - 1) * rules.points["layer"]),
             (f"contract {', '.join(found.contracts + found.protected)}", rules.points["contract"] if found.contracts or found.protected else 0),
             ("a runnable Check: line", rules.points["mechanical"] if found.mechanical else 0)]
    kept = [(why, points) for why, points in parts if points]
    return max(0, sum(points for _, points in kept)), [f"{why} ({points:+d})" for why, points in kept]


def placed(points: int, waits: bool, rules: GradeMap) -> tuple[Grade, str | None]:
    """The lowest grade whose most points holds the points (the last when it waits on Ghost), raised to the floor;
    with the grade it was raised from, or None when the floor did not move it."""
    grades = list(rules.ladder)
    fits = [g for g in grades if not waits and g.most_points is not None and points <= g.most_points]
    grade = fits[0] if fits else grades[-1]
    floor = next((g for g in grades if g.name == rules.floor), grades[0])
    return (floor, grade.name) if grades.index(floor) > grades.index(grade) else (grade, None)


def items(todo_text: str) -> list[tuple[str, str]]:
    """Each open item's number and body, its heading to the next heading of level two or three: [("2.6", "### 2.6 ...")]."""
    found = []
    for match in todo.ITEM.finditer(todo_text):
        rest = todo_text[match.end():]
        following = re.search(r"^#{2,3} ", rest, flags=re.MULTILINE)
        found.append((f"{match.group(1)}.{match.group(2)}", todo_text[match.start(): match.end() + (following.start() if following else len(rest))]))
    return found


def line(item: str, found: Facts, rules: GradeMap) -> str:
    """One item's line: "2.6 mid (Claude Sonnet, 120 tool calls), 5 points — working set ... (+5); rows: ..."."""
    if not found.files:
        return f"{item} unplaced — names no file: a mid-grade agent places it and writes the facts it used"
    points, parts = score(found, rules)
    grade, raised = placed(points, found.waits, rules)
    limit = f"{grade.tool_calls} tool calls" if grade.tool_calls else "no tool-call limit"
    notes = parts + (["waits on Ghost"] if found.waits else []) + ([f"raised to the floor from {raised}"] if raised else [])
    rows = "; ".join(task.split(" (")[0].split(":")[0] for task in found.rows) or "none"
    return f"{item} {grade.name} ({grade.model}, {limit}), {points} points — {', '.join(notes) or 'nothing'}; rows: {rows}"


def report(todo_text: str, rules: GradeMap, rows: list[tuple[str, list[str], list[str]]], sizes: dict[str, int],
           folders: list[str], prefixes: list[str]) -> list[str]:
    """One line per open item of the TODO text, in its order."""
    return [line(item, facts(body, rows, sizes, folders, prefixes), rules) for item, body in items(todo_text)]
