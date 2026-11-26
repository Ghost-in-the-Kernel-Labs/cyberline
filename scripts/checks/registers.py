"""The table registers: docs/FINDINGS.md (F-nnn in order, five columns, a known status) and
docs/ESCALATIONS.md (six columns, a known kind, three open of one kind listed for Ghost) (test/test_registers.py; C-014, C-028)."""
import re

FINDING_STATUSES: tuple[str, ...] = ("open", "resolved")
# A conflict between agents is not a kind: it stops the work at once and goes to Ghost uncounted (C-029).
KINDS: tuple[str, ...] = ("missing-row", "not-read", "wrong-row", "stale-pointer", "hard", "no-replay", "no-advisor")
RAISED_AT = 3


def rows(table: str, columns: int) -> list[list[str]]:
    """The body rows of the first markdown table with that many columns, each row its stripped cells.

    rows("| a | b |\\n| --- | --- |\\n| 1 | 2 |\\n", 2) gives [["1", "2"]].
    """
    found: list[list[str]] = []
    for line in table.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")] if line.startswith("|") else []
        if len(cells) == columns and not cells[0].startswith("---") and cells[0] not in ("Id", "Date"):
            found.append(cells)
    return found


def finding_problems(findings: str) -> list[str]:
    """Ids F-001, F-002, ... in order; a status that is open or resolved; no empty cell."""
    problems: list[str] = []
    for position, cells in enumerate(rows(findings, 5), start=1):
        if cells[0] != f"F-{position:03d}":
            problems.append(f"finding {position} is {cells[0]}, expected F-{position:03d}")
        problems += [f"{cells[0]} has an empty cell"] if "" in cells else []
        if not cells[4].split()[0:1] or cells[4].split()[0] not in FINDING_STATUSES:
            problems.append(f"{cells[0]} has status {cells[4]!r}, not open or resolved")
    return problems


# Decision: C-028 (three open escalations of one kind go to Ghost for a routing pass)
def escalation_problems(escalations: str, handoff: str) -> list[str]:
    """A kind outside the list; three or more open rows of one kind not named in HANDOFF's For Ghost section."""
    problems: list[str] = []
    open_by_kind: dict[str, int] = {}
    for cells in rows(escalations, 6):
        if cells[2] not in KINDS:
            problems.append(f"escalation on {cells[0]} has kind {cells[2]!r}, not one of {len(KINDS)}")
        if cells[5].lower().startswith("yes"):
            open_by_kind[cells[2]] = open_by_kind.get(cells[2], 0) + 1
    queue = "".join(re.findall(r"^## For Ghost.*?(?=^## |\Z)", handoff, flags=re.MULTILINE | re.DOTALL))
    for kind, count in open_by_kind.items():
        if count >= RAISED_AT and kind not in queue:
            problems.append(f"{count} open escalations of kind {kind!r} and no For Ghost item names it")
    return problems
