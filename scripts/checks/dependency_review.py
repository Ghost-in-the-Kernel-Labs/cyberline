"""The dependency-review posture's files hold their shape: the reviewer's tools line is exactly Read, Grep, Glob;
docs/REVIEWED-VERSIONS.md has ten columns with a known verdict, reputation and decision in each row; and every pin the
repository holds has a row (test/test_patch_reviewer.py, test/test_reviewed_versions.py; C-035).

A pin is what fixes one version of something fetched, read from git's file list (C-001), fixtures under test/fixtures/
left out: each entry of a `package-lock.json` (its `packages`, the root and workspace links skipped) and of a
`requirements.lock` (`name==version`); each `uses: owner/repo@<40-hex SHA>` in a workflow; each `FROM image@sha256:<hex>`
in a Dockerfile; each row of a `third_party/MANIFEST.md` whose last cell is a SHA-256. A pin is recorded when a row's
Package and To are its name and version. On adoption every pin already held gets an "unreviewed baseline" row (Kind
`baseline`, From, Verdict and Reputation `—`); a baseline row for a package that already has a row is refused, since an
update of a held package is read, never baselined. `python3 -I scripts/checks/dependency_review.py --baseline J-nnn`
prints the baseline rows for the pins with none, for the adopting commit only; it writes nothing.
"""
import json
import re
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.checks.common import matching, tracked_files  # noqa: E402

REVIEWER_TOOLS = "tools: Read, Grep, Glob"
VERDICTS: tuple[str, ...] = ("SAFE", "UNSAFE", "UNSURE")
REPUTATIONS: tuple[str, ...] = ("CLEAN", "CONCERN")
COLUMNS = 10
BASELINE = "unreviewed baseline"
NONE = "—"
RECORD = Path("docs") / "REVIEWED-VERSIONS.md"
FIXTURES = Path("test") / "fixtures"


def reviewer_problems(text: str) -> list[str]:
    """The agent file's front matter: a tools line that is exactly the three read-only tools, and nothing granting more."""
    front = text.split("---")[1] if text.startswith("---") and text.count("---") >= 2 else ""
    tools = [line.strip() for line in front.splitlines() if line.strip().startswith("tools:")]
    if tools != [REVIEWER_TOOLS]:
        return [f"patch-reviewer's tools line is {tools!r}, not exactly [{REVIEWER_TOOLS!r}]: its tools are its privileges"]
    return []


def rows(table: str) -> list[list[str]]:
    """The body rows of the record's table: each row its stripped cells; the header and the rule skipped."""
    found: list[list[str]] = []
    for line in table.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells[0] in ("Date", "---") or cells[0].startswith("---"):
            continue
        found.append(cells)
    return found


def record_problems(text: str) -> list[str]:
    """Each row of the record with the wrong width, an unknown verdict or reputation, an UNSAFE taken, or a decision that is neither automatic nor Ghost's."""
    found: list[str] = []
    seen: set[str] = set()
    for cells in rows(text):
        where = f"{cells[0]} {cells[1] if len(cells) > 1 else ''}".strip()
        if len(cells) != COLUMNS:
            found.append(f"row {where!r} has {len(cells)} cells, not {COLUMNS}")
            continue
        if cells[7] == BASELINE:
            found += baseline_problems(cells, where, cells[1] in seen)
            seen.add(cells[1])
            continue
        seen.add(cells[1])
        if cells[5] not in VERDICTS:
            found.append(f"row {where!r} has verdict {cells[5]!r}")
        if cells[6] not in REPUTATIONS:
            found.append(f"row {where!r} has reputation {cells[6]!r}")
        if cells[7] == "automatic" and (cells[5] != "SAFE" or cells[6] != "CLEAN"):
            found.append(f"row {where!r} was automatic without SAFE and CLEAN")
        if cells[7] != "automatic" and not cells[7].startswith("Ghost:"):
            found.append(f"row {where!r} has decision {cells[7]!r}, neither automatic nor Ghost's")
        if cells[5] == "UNSAFE" and not cells[7].startswith("Ghost: refused") and cells[7] != "refused":
            found.append(f"row {where!r} is UNSAFE and not refused")
        if not re.fullmatch(r"J-\d{3}", cells[8]):
            found.append(f"row {where!r} has no journal entry")
    return found


def baseline_problems(cells: list[str], where: str, held: bool) -> list[str]:
    """An "unreviewed baseline" row's own shape: Kind baseline, From, Verdict and Reputation "—", a journal entry, and a
    package with no row above it (an update of a held package is read, never baselined)."""
    found = [f"row {where!r} is a baseline row but its {name} is {cells[i]!r}, not {want!r}"
             for i, name, want in ((4, "Kind", "baseline"), (2, "From", NONE), (5, "Verdict", NONE), (6, "Reputation", NONE)) if cells[i] != want]
    if held:
        found.append(f"row {where!r} baselines a package that already has a row: an update is read, never baselined")
    if not re.fullmatch(r"J-\d{3}", cells[8]):
        found.append(f"row {where!r} has no journal entry")
    return found


def lock_entries(path: Path) -> list[tuple[str, str]]:
    """(name, version) for each entry of a package-lock.json's packages or a requirements.lock's `name==version` lines:
    {"packages": {"": {}, "node_modules/a": {"version": "1.0.0"}}} gives [("a", "1.0.0")]."""
    text = path.read_text(errors="replace")
    if path.name == "requirements.lock":
        return re.findall(r"^([A-Za-z0-9][A-Za-z0-9._-]*)==([^\s;\\]+)", text, re.MULTILINE)
    packages = json.loads(text).get("packages", {})
    return [(entry.get("name") or key.rsplit("node_modules/", 1)[-1], entry["version"])
            for key, entry in packages.items() if key and not entry.get("link") and "version" in entry]


def file_pins(path: Path, rel: str) -> list[tuple[str, str]]:
    """The pins one file holds, (name, version), by its kind (the module docstring); a file of no kind holds none."""
    name = path.name
    if name in ("package-lock.json", "requirements.lock"):
        return lock_entries(path)
    text = path.read_text(errors="replace")
    if matching([Path(rel)], Path(), ".github/workflows/*.y*ml"):
        return re.findall(r"uses:\s*([\w.-]+/[\w./-]+)@([0-9a-f]{40})\b", text)
    if name.startswith("Dockerfile"):
        return re.findall(r"^FROM\s+(?:--platform=\S+\s+)?(\S+?)@(sha256:[0-9a-f]{64})\b", text, re.MULTILINE | re.IGNORECASE)
    if rel.endswith("third_party/MANIFEST.md"):
        cells = [[c.strip().strip("`") for c in line.strip().strip("|").split("|")] for line in text.splitlines() if line.startswith("|")]
        return [(row[0], row[-1]) for row in cells if len(row) > 1 and re.fullmatch(r"[0-9a-f]{64}", row[-1])]
    return []


def pins(root: Path) -> list[tuple[str, str, str]]:
    """Every pin the repository holds, (file, name, version), in file order; fixtures left out."""
    found = []
    for path in tracked_files(root):
        rel = path.relative_to(root)
        if not rel.is_relative_to(FIXTURES):
            found += [(rel.as_posix(), name, version) for name, version in file_pins(path, rel.as_posix())]
    return found


def unrecorded(root: Path) -> list[tuple[str, str, str]]:
    """The pins with no row whose Package and To are their name and version."""
    record = root / RECORD
    have = {(cells[1], cells[3]) for cells in rows(record.read_text())} if record.is_file() else set()
    return [pin for pin in pins(root) if pin[1:] not in have]


# Decision: C-035 (no version enters a lockfile or a vendored manifest unread; the baseline is how a pin held before is named)
def pin_problems(root: Path) -> list[str]:
    """Each pin with no row in docs/REVIEWED-VERSIONS.md: "package-lock.json: a 1.0.1 has no row ..."."""
    return [f"{file}: {name} {version} has no row in {RECORD.as_posix()} (a review for an update or a new package; "
            f"an \"{BASELINE}\" row only on adoption)" for file, name, version in unrecorded(root)]


def problems(root: Path) -> list[str]:
    """Every file's problems; [] when they hold."""
    reviewer = root / ".claude" / "agents" / "patch-reviewer.md"
    found = reviewer_problems(reviewer.read_text()) if reviewer.is_file() else [".claude/agents/patch-reviewer.md is missing"]
    record = root / RECORD
    found += record_problems(record.read_text()) if record.is_file() else ["docs/REVIEWED-VERSIONS.md is missing"]
    return found + pin_problems(root)


def main(argv: list[str]) -> int:
    """`--baseline J-nnn` prints a baseline row for each unrecorded pin; no argument prints the problems; exit 1 on any."""
    root = Path(__file__).resolve().parents[2]
    if len(argv) == 2 and argv[0] == "--baseline" and re.fullmatch(r"J-\d{3}", argv[1]):
        for file, name, version in unrecorded(root):
            print(f"| <date> | {name} | {NONE} | {version} | baseline | {NONE} | {NONE} | {BASELINE} | {argv[1]} | pinned in {file} before the record; the first review reads from this pin |")
        return 0
    found = problems(root)
    print("\n".join(found) if found else "dependency review: holds")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
