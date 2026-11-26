"""The Markdown table reader every check shares (test/test_tables.py): a table's header and rows of cells, the table
after a heading, and a ragged table refused where a check needs a fixed column count.

A table is a run of lines that begin with `|`. A line's cells are split at its pipes, except a pipe inside a code span
(`a|b`) or escaped (`\\|`), which stays in its cell as written; the outer pipes are dropped and each cell is stripped.
A row whose every cell is dashes with optional colons is the alignment row and is skipped wherever it stands. Carried
from Neon Rain's scripts/checks/tables.py (`cells`, `TABLE`), with code spans and the header added.
"""
import re
from dataclasses import dataclass

BLOCK = re.compile(r"(?:^\|.*(?:\n|$))+", re.MULTILINE)
ALIGNMENT = re.compile(r":?-+:?")
HEADING = re.compile(r"^(#+) ")


@dataclass(frozen=True)
class Table:
    """One Markdown table: its first row's cells, and every row after it but the alignment row."""

    header: list[str]
    rows: list[list[str]]


def cells(line: str) -> list[str]:
    """A table line's cells, stripped, split at pipes outside code spans and not escaped: "| a | `b|c` | d\\\\|e |" gives
    ["a", "`b|c`", "d\\\\|e"]. A backtick run with no closing run of the same length is text, as in CommonMark."""
    text = line.strip()
    text = text[1:] if text.startswith("|") else text
    text = text[:-1] if text.endswith("|") and not text.endswith("\\|") else text
    found, cell, i = [], "", 0
    while i < len(text):
        if text[i] == "`":
            run = len(text[i:]) - len(text[i:].lstrip("`"))
            close = re.compile(rf"(?<!`){'`' * run}(?!`)").search(text, i + run)
            end = close.end() if close else i + run
            cell, i = cell + text[i:end], end
        elif text.startswith("\\|", i):
            cell, i = cell + "\\|", i + 2
        elif text[i] == "|":
            found.append(cell.strip())
            cell, i = "", i + 1
        else:
            cell, i = cell + text[i], i + 1
    return found + [cell.strip()]


def tables(text: str) -> list[Table]:
    """Each Markdown table in text, in order: "| a | b |\\n| - | - |\\n| 1 | 2 |" gives [Table(["a", "b"], [["1", "2"]])]."""
    found = []
    for block in BLOCK.findall(text):
        rows = [row for row in (cells(line) for line in block.splitlines()) if not all(ALIGNMENT.fullmatch(cell) for cell in row)]
        if rows:
            found.append(Table(rows[0], rows[1:]))
    return found


def table_after(text: str, heading: str) -> Table | None:
    """The first table under the heading line given ("## Metrics"), before the next heading of its level or higher;
    None when the heading is missing or its section has no table."""
    lines = text.splitlines(keepends=True)
    level = HEADING.match(heading)
    for index, line in enumerate(lines):
        if line.rstrip("\n") == heading:
            section = []
            for following in lines[index + 1:]:
                deeper = HEADING.match(following)
                if deeper and level and len(deeper.group(1)) <= len(level.group(1)):
                    break
                section.append(following)
            found = tables("".join(section))
            return found[0] if found else None
    return None


def headed(text: str, names: tuple[str, ...]) -> list[Table]:
    """The tables whose header begins with the names given: headed(text, ("Task", "Start here")) gives the routing tables."""
    return [table for table in tables(text) if table.header[: len(names)] == list(names)]


def ragged(table: Table, columns: int) -> list[str]:
    """What keeps a table from a fixed column count: a header or a row of another width; [] for a table that holds it.
    A table headed "| a | b |" with a row "| 1 |" against 2 gives ["row 1 (1) has 1 cells, not 2"]."""
    found = [] if len(table.header) == columns else [f"the header has {len(table.header)} cells, not {columns}"]
    return found + [f"row {n} ({row[0] if row else ''}) has {len(row)} cells, not {columns}" for n, row in enumerate(table.rows, 1) if len(row) != columns]


def fixed(table: Table, columns: int) -> Table:
    """The table, when every row has the count of cells given; a ragged table raises ValueError naming its rows, since
    a check that reads cells by position would read the wrong one."""
    problems = ragged(table, columns)
    if problems:
        raise ValueError(f"a table headed {' | '.join(table.header)} is ragged: " + "; ".join(problems))
    return table
