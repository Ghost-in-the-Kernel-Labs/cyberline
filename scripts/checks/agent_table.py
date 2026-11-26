"""docs/AGENT.md's metrics table: read it, judge a measurement against it, write it back (scripts/metrics.py).

Carried from Neon Rain's scripts/checks/agent_table.py (C-023).
"""
import re

from scripts.checks import tables

HEADER = ("Metric", "Target", "Measured")
COLUMNS = 4


def number(text: str) -> float | None:
    """The first number in a cell, or None: "0 (no results)" gives 0.0, "— (0.5)" gives None, "1,200" gives 1200.0."""
    match = re.match(r"^\s*(\d[\d,]*(?:\.\d+)?)", text)
    return float(match.group(1).replace(",", "")) if match else None


def within(target: str, value: float) -> bool:
    """Whether a value meets a target cell: "< 30", "≤ 5" or a bare "0" (meaning at most 0)."""
    limit = number(re.sub(r"^[<≤]\s*", "", target.strip())) or 0.0
    return value < limit if target.strip().startswith("<") else value <= limit


def table(agent: str) -> dict[str, dict[str, str]]:
    """The rows of the table headed Metric | Target | Measured | Why by metric name: {"Fast loop (s)": {"metric":
    "Fast loop (s)", "target": "< 30", "measured": "—", "why": "..."}}; {} with no such table. A ragged table raises
    ValueError (tables.fixed): a row of three cells would put its Why under Measured."""
    found = tables.headed(agent, HEADER)
    if not found:
        return {}
    rows = tables.fixed(found[0], COLUMNS).rows
    return {row[0]: dict(zip(("metric", "target", "measured", "why"), row)) for row in rows}


# Decision: C-023 (a metric is armed once recorded within its target, and an armed metric may not pass it)
def verdict(target: str, recorded: str, value: float | None) -> str:
    """One metric's state: "not measured", "informational" (a target with no number, "—": counted, never armed),
    "within", "not armed" (past target, never recorded within), "regressed"."""
    if value is None:
        return "not measured"
    if number(re.sub(r"^[<≤]\s*", "", target.strip())) is None:
        return "informational"
    if within(target, value):
        return "within"
    before = number(recorded)
    armed = before is not None and within(target, before)
    return "regressed" if armed else "not armed"


def shown(value: float | None) -> str:
    """A measurement as the table shows it: None as "—", 785.0 as "785", 0.375 as "0.4"."""
    if value is None:
        return "—"
    return str(int(value)) if float(value).is_integer() else f"{value:.1f}"


def rewritten(agent: str, values: dict[str, float | None]) -> str:
    """AGENT.md with each measured metric's Measured cell replaced; a metric not measured keeps its cell."""
    rows = table(agent)
    lines = []
    for line in agent.splitlines():
        cells = tables.cells(line) if line.startswith("|") else []
        row = rows.get(cells[0]) if len(cells) == COLUMNS else None
        if row and cells[1:] == [row["target"], row["measured"], row["why"]] and values.get(row["metric"]) is not None:
            line = f"| {row['metric']} | {row['target']} | {shown(values[row['metric']])} | {row['why']} |"
        lines.append(line)
    return "\n".join(lines) + "\n"
