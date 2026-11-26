"""docs/AGENT.md's table matches what scripts/checks/metrics.py measures, no armed metric regressed; and the
judging is right on planted values (C-022, C-023); the two-run rule: a cold gate says so and its numbers never reach the
table (C-024, docs/when/tune-up.md step 2)."""
import json
import os
import shutil
import subprocess
import sys
import unittest

from scripts import metrics as metrics_script
from scripts.checks import agent_table, gate_record, journal, metrics
from test.support import ROOT, scratch
from test.support_git import gated_repo

TIMED: tuple[str, ...] = ("Fast loop (s)", "Gate (min)")


def real() -> tuple[dict[str, dict[str, str]], dict[str, float | None]]:
    """AGENT.md's rows and the measurements now (the timings left unmeasured: they belong to the gate)."""
    return agent_table.table((ROOT / "docs" / "AGENT.md").read_text()), metrics.measure(ROOT, None, None)


class TheRepository(unittest.TestCase):
    def test_every_metric_measured_is_in_the_table_and_back(self) -> None:
        rows, values = real()
        self.assertEqual(sorted(rows), sorted(values))

    def test_the_table_is_not_stale(self) -> None:
        rows, values = real()
        stale = {name: (rows[name]["measured"], agent_table.shown(value)) for name, value in values.items()
                 if value is not None and agent_table.number(rows[name]["measured"]) != value}
        self.assertEqual(stale, {}, "run python3 -I scripts/metrics.py --write and review the diff")

    def test_no_armed_metric_regressed(self) -> None:
        rows, values = real()
        states = {name: agent_table.verdict(rows[name]["target"], rows[name]["measured"], v) for name, v in values.items()}
        self.assertEqual([name for name, state in states.items() if state == "regressed"], [])


class TheJudging(unittest.TestCase):
    def test_numbers_are_read_from_cells(self) -> None:
        self.assertEqual([agent_table.number(c) for c in ("0 (none)", "— (0.5)", "1,200", "0.37", "")], [0, None, 1200, 0.37, None])

    def test_targets_are_judged(self) -> None:
        self.assertTrue(agent_table.within("< 30", 29.9) and not agent_table.within("< 30", 30))
        self.assertTrue(agent_table.within("≤ 5", 5) and not agent_table.within("≤ 5", 6))
        self.assertTrue(agent_table.within("0", 0) and not agent_table.within("0", 1))

    def test_a_metric_worse_than_its_armed_target_is_caught(self) -> None:
        self.assertEqual(agent_table.verdict("< 30", "12", 31), "regressed")

    def test_a_metric_never_within_target_is_not_armed(self) -> None:
        self.assertEqual(agent_table.verdict("< 0.35", "—", 20.0), "not armed")
        self.assertEqual(agent_table.verdict("< 0.35", "0.5", 0.6), "not armed")

    def test_an_unmeasured_metric_is_not_compared(self) -> None:
        self.assertEqual(agent_table.verdict("< 30", "12", None), "not measured")

    def test_the_table_is_rewritten_only_where_measured(self) -> None:
        table = "| Metric | Target | Measured | Why |\n| --- | --- | --- | --- |\n| A | < 30 | 12 | w |\n| B | 0 | — | w |\n"
        self.assertEqual(agent_table.rewritten(table, {"A": 14.0, "B": None}), table.replace("| 12 |", "| 14 |"))

    def test_routing_files_counts_the_widest_row(self) -> None:
        claude = "| Task | Start here | Contract | Tests |\n| --- | --- | --- | --- |\n| a | `x.md` | | |\n| b | `x.md`, `y.md`, `z.md` | | |\n"
        self.assertEqual(metrics.routing_files(claude), 3)


class TheRatio(unittest.TestCase):
    def test_a_freshly_written_table_is_not_stale(self) -> None:
        root = scratch()
        (root / "src").mkdir()
        (root / "src" / "a.py").write_text("x = 1\n" * 7)
        (root / "docs" / "modules.json").write_text(json.dumps({"modules": {"m": {"folder": "src"}}}))
        (root / "docs" / "x.md").write_text("doc\n" * 3)
        value = metrics.docs_per_source(root)
        self.assertEqual(value, 0.4)
        agent = "| Metric | Target | Measured | Why |\n| --- | --- | --- | --- |\n| Docs lines per source line | < 0.35 | — | w |\n"
        written = agent_table.rewritten(agent, {"Docs lines per source line": value})
        row = agent_table.table(written)["Docs lines per source line"]
        self.assertEqual(row["measured"], "0.4")
        self.assertEqual(agent_table.number(row["measured"]), value)


def journal_entry(rid: str, cost: str, body: str = "") -> str:
    """A journal entry with every field and the Cost line given; `body` goes after the Found line (a table)."""
    fields = [("Who", "x"), ("Class", "measurement"), ("Intent", "x"), ("Found", "x"), ("Options", "x"),
              ("Resolved", "x"), ("Touched", "x"), ("Caught by", "x"), ("Cost", cost)]
    lines = [f"- **{name}**: {value}" + (f"\n\n{body}\n" if name == "Found" and body else "") for name, value in fields]
    return f"### {rid} a title\n" + "\n".join(lines) + "\n\n"


class TheCostRows(unittest.TestCase):
    """The informational row "Cost rows since the thresholds were set" (TODO 2.8, C-036) on planted text."""

    GRADES = "# Grades\n\n## Provisional\n\nThe points are set on 2026-11-06. They move.\n\nWhy: Ghost, 2026-10-01.\n"
    TABLE = "| run | grade | tool calls |\n| --- | --- | --- |\n| A | mid | 36 |\n| B | strong | 51 |"

    def test_the_date_is_read_from_the_provisional_paragraph_only(self) -> None:
        self.assertEqual(metrics.thresholds_set(self.GRADES), "2026-11-06")
        self.assertIsNone(metrics.thresholds_set("## Provisional\n\nNo date here.\n\nWhy: 2026-10-01.\n"))
        self.assertIsNone(metrics.thresholds_set("# Grades\n\nset on 2026-11-06\n"))

    def test_done_dates_each_cited_entry(self) -> None:
        done = "### 2.1 a\n\nDone 2026-11-05 (J-010, J-011). Check: x ✓\n\n### 2.2 b\n\nDone 2026-11-06. Check: y ✓\n"
        self.assertEqual(metrics.done_dates(done), {"J-010": "2026-11-05", "J-011": "2026-11-05"})

    def test_a_cost_row_names_a_grade_and_an_exact_count(self) -> None:
        rows = ["strong grade; 52 tool calls; tokens not reported", "mid; 1,204 tool calls; 130k tokens"]
        not_rows = ["strong grade; about 30 tool calls", "mid grade; ~40 tool calls", "12 tool calls; tokens not reported",
                    "strong grade; tool calls not counted", "the coordinator, about ten minutes"]
        self.assertEqual([metrics.is_cost_row(c) for c in rows + not_rows], [True] * 2 + [False] * 5)

    def test_a_fixture_journal_is_counted_by_entry_from_the_date(self) -> None:
        root = scratch()
        (root / "docs" / "when").mkdir()
        (root / "docs" / "journal").mkdir()
        (root / "docs" / "when" / "grades.md").write_text(self.GRADES)
        (root / "docs" / "DONE.md").write_text("Done 2026-11-05 (J-001). Check ✓\n\nDone 2026-11-06 (J-002). Check ✓\n")
        (root / "docs" / "journal" / "J-000-099.md").write_text(
            "# Journal\n\n"
            + journal_entry("J-001", "mid grade; 20 tool calls")           # before the date: outside
            + journal_entry("J-002", "strong grade; about 30 tool calls")  # inside, an estimate: not a row
            + journal_entry("J-003", "strong grade; 44 tool calls", self.TABLE)  # one row, its table evidence
            + journal_entry("J-004", "small grade; 9 tool calls"))          # no DONE line, after the window opened
        self.assertEqual(journal.problems(journal.journal_text(root), ""), [], "a table inside an entry is accepted")
        self.assertEqual(metrics.cost_rows_in(root), 2)

    def test_no_date_is_not_measured(self) -> None:
        self.assertIsNone(metrics.cost_rows({"J-001": {"Cost": "mid; 3 tool calls"}}, {"J-001": "2026-11-06"}, None))

    def test_an_informational_row_is_never_armed(self) -> None:
        self.assertEqual(agent_table.verdict("—", "0", 5), "informational")
        self.assertEqual(agent_table.verdict("—", "9", 0), "informational")
        self.assertEqual(agent_table.verdict("—", "—", None), "not measured")


# A stand-in for scripts/metrics.py in the scratch gate: it logs the arguments the gate passed it.
ARGS_PY = "import sys\nprint('metrics args', sys.argv[1:])\n"
# A present stack whose gate logs what it was given of GHOST_COLD.
STACK_GATE = "#!/usr/bin/env bash\necho \"stack saw GHOST_COLD=${GHOST_COLD:-unset}\"\n"


class TheTwoRunRule(unittest.TestCase):
    """3.9: `GHOST_COLD=1 scripts/gate.sh` is the cold run; its verdict says so and metrics.py refuses its numbers."""

    def cold_gate(self, cold: bool) -> tuple[subprocess.CompletedProcess, str]:
        """The scratch gate with a logging metrics step and a present stack, run warm or cold: (result, its log)."""
        root = self.root = gated_repo()
        (root / "scripts" / "metrics.py").write_text(ARGS_PY)
        (root / "stacks" / "x").mkdir(parents=True)
        (root / "stacks" / "x" / "gate.sh").write_text(STACK_GATE)
        (root / "stacks" / "x" / "PRESENT").write_text("")
        env = dict(os.environ)
        env.pop("GHOST_COLD", None)
        if cold:
            env["GHOST_COLD"] = "1"
        result = subprocess.run(["bash", "scripts/gate.sh"], cwd=root, capture_output=True, text=True, env=env)
        self.assertEqual((root / "build" / "gate.log").exists(), not cold, "a cold run leaves the warm run's log alone")
        self.assertEqual((root / "build" / "gate-times.txt").exists(), not cold)
        return result, (root / "build" / ("gate-cold.log" if cold else "gate.log")).read_text()

    def test_a_cold_gate_prints_the_cold_verdict_and_passes_cold_on(self) -> None:
        result, log = self.cold_gate(cold=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        last = result.stdout.splitlines()[-1]
        self.assertRegex(last, r"^gate \(cold\): passed; fast loop \d+\.\d\ds, \d+\.\d\d min, 1 commits since the last tune-up$")
        self.assertTrue(log.endswith(last + "\n"))
        self.assertIn("metrics args ['--fast-loop',", log)
        self.assertIn("'--cold']", log)
        self.assertIn("stack saw GHOST_COLD=1", log)
        self.assertIsNotNone(gate_record.record(self.root), "a passing cold run records its tree as a warm one does")

    def test_a_warm_gate_is_unchanged(self) -> None:
        result, log = self.cold_gate(cold=False)
        self.assertRegex(result.stdout.splitlines()[-1], r"^gate: passed; ")
        self.assertNotIn("--cold", log)
        self.assertIn("stack saw GHOST_COLD=unset", log)

    def test_metrics_refuses_to_write_a_cold_run(self) -> None:
        """metrics.py --cold --write in a scratch copy: one line, exit 1, AGENT.md untouched (the real one is never at risk)."""
        root = scratch()
        shutil.copytree(ROOT / "scripts" / "checks", root / "scripts" / "checks", ignore=shutil.ignore_patterns("__pycache__"))
        for name in ("scripts/__init__.py", "scripts/metrics.py", "docs/AGENT.md"):
            shutil.copy(ROOT / name, root / name)
        before = (root / "docs" / "AGENT.md").read_bytes()
        script = str(root / "scripts" / "metrics.py")
        result = subprocess.run([sys.executable, "-I", script, "--fast-loop", "9", "--gate", "1", "--cold", "--write"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(result.stdout.splitlines(), [metrics_script.COLD_WRITE])
        self.assertEqual((root / "docs" / "AGENT.md").read_bytes(), before)

