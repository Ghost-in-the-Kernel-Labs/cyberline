"""The one Markdown table reader: cells split outside code spans, the alignment row skipped, the table after a
heading, and a ragged table refused where a check reads cells by position (scripts/checks/tables.py; C-013)."""
import unittest

from scripts.checks import agent_table, tables
from test.support import BROKEN, ROOT

DOC = """# A

## Metrics

Intro.

| Metric | Target | Measured | Why |
| :--- | ---: | :-: | --- |
| `a|b` in code | < 3 | 1 | w \\| x |
| ``x ` y|z`` | 0 | — | an ` unclosed | tick |

### Under it

| x | y |
| --- | --- |
| 1 | 2 |

## Other

| Task | Start here | Contract | Tests |
| --- | --- | --- | --- |
| t | `s.md` | | |
"""


class TheRepository(unittest.TestCase):
    def test_the_real_tables_a_check_reads_by_position_hold_their_widths(self) -> None:
        for path, header in (("docs/AGENT.md", agent_table.HEADER), ("CLAUDE.md", ("Task", "Start here")), ("docs/paths/process.md", ("Task", "Start here"))):
            found = tables.headed((ROOT / path).read_text(), header)
            self.assertTrue(found, path)
            self.assertEqual([tables.ragged(table, 4) for table in found], [[] for _ in found], path)

    def test_the_planted_break_is_caught(self) -> None:
        agent = (BROKEN / "tables" / "docs" / "AGENT.md").read_text()
        self.assertEqual(tables.ragged(tables.headed(agent, agent_table.HEADER)[0], 4), ["row 2 (Gate (min)) has 3 cells, not 4"])
        with self.assertRaisesRegex(ValueError, r"ragged: row 2 \(Gate \(min\)\) has 3 cells, not 4"):
            agent_table.table(agent)


class TheReader(unittest.TestCase):
    def test_cells_keep_pipes_in_code_and_escaped(self) -> None:
        self.assertEqual(tables.cells("| `a|b` in code | < 3 | 1 | w \\| x |"), ["`a|b` in code", "< 3", "1", "w \\| x"])
        self.assertEqual(tables.cells("| ``x ` y|z`` | 0 |"), ["``x ` y|z``", "0"])

    def test_an_unclosed_backtick_is_text(self) -> None:
        self.assertEqual(tables.cells("| an ` unclosed | tick |"), ["an ` unclosed", "tick"])

    def test_the_tables_with_header_and_rows_and_no_alignment_row(self) -> None:
        found = tables.tables(DOC)
        self.assertEqual([table.header for table in found], [["Metric", "Target", "Measured", "Why"], ["x", "y"], ["Task", "Start here", "Contract", "Tests"]])
        self.assertEqual(found[0].rows, [["`a|b` in code", "< 3", "1", "w \\| x"], ["``x ` y|z``", "0", "—", "an ` unclosed", "tick"]])
        self.assertEqual(tables.tables("| a |\n| - |\n\n| b |\n"), [tables.Table(["a"], []), tables.Table(["b"], [])])

    def test_the_table_after_a_heading(self) -> None:
        self.assertEqual(tables.table_after(DOC, "## Metrics").header[0], "Metric")
        self.assertEqual(tables.table_after(DOC, "### Under it").rows, [["1", "2"]])
        self.assertEqual(tables.table_after(DOC, "## Other").header[0], "Task")
        self.assertIsNone(tables.table_after(DOC, "## Missing"))
        self.assertIsNone(tables.table_after("## A\n\ntext\n\n## B\n\n| x |\n", "## A"))

    def test_headed_and_ragged(self) -> None:
        self.assertEqual([table.rows for table in tables.headed(DOC, ("Task", "Start here"))], [[["t", "`s.md`", "", ""]]])
        metric = tables.headed(DOC, ("Metric",))[0]
        self.assertEqual(tables.ragged(metric, 4), ["row 2 (``x ` y|z``) has 5 cells, not 4"])
        self.assertEqual(tables.ragged(tables.Table(["a", "b", "c"], []), 4), ["the header has 3 cells, not 4"])
        self.assertEqual(tables.fixed(tables.headed(DOC, ("Task",))[0], 4).header[0], "Task")
