"""The score places each open item from facts by the grade map's points, and a map missing a fact is refused (C-036).

The table test's points, worked by hand (TODO, routing and sizes below; 4 characters a token, 1 point per 10,000):

- 1.1 names `test/test_a.py`; row Alpha covers it by its Tests cell. Working set: docs/a.md 40,000 + test/test_a.py
  4,000 = 44,000 characters = 11,000 tokens: +1. No layer, no contract. Its Check names a test: -2. 1 - 2 = -1,
  floored at 0: small (most 3); with the floor at mid, mid, raised from small.
- 1.2 names `src/leaf/x.py` and `src/project/p.py`; row Beta covers the first through its folder `src/leaf/`, which
  opens the files directly in it (src/leaf/x.py 32,000; src/leaf/sub/deep.py is a level down, not opened) and
  docs/b.md 8,000; the named src/project/p.py adds 12,000, src/leaf/x.py counted once: 52,000 characters = 13,000
  tokens: +1. Layers src/leaf and src/project, one beyond the first: +2. XX-01: +3. Nothing runnable. 6: mid (most 7).
- 1.3 names `scripts/checks/g.py`; the workpath's row Gamma covers it by its pattern `scripts/checks/<check>.py`,
  which opens nothing of its own. 20,000 characters = 5,000 tokens: +0. One layer, scripts: +0. Its Check names a
  script: -2. 0, but it goes to Ghost: strong.
- 1.4 names no file: unplaced.
- 1.5 names `theGhost.md`, protected: 400 characters = 100 tokens: +0; +3. 3: small.
"""
import subprocess
import sys
import unittest

from scripts.checks import score
from test.support import BROKEN, ROOT

GRADES = """| Grade | Model | Most points (provisional) | Tool calls | Gets |
| --- | --- | --- | --- | --- |
| small | Model S | 3 | 40 | a |
| mid | Model M | 7 | 120 | b |
| strong | Model L | no limit | no limit | c |
| ruling | Model R | — | — | none |

| Fact | Per | Points |
| --- | --- | --- |
| working set | 10,000 tokens | 1 |
| layer | each beyond the first | 2 |
| contract | an id or a protected file | 3 |
| mechanical | a runnable `Check:` line | −2 |

Floor: {floor}
"""
CLAUDE = """| Task | Start here | Contract | Tests |
| --- | --- | --- | --- |
| Alpha | `docs/a.md` | | `test/test_a.py` |
| Beta: the leaf | `src/leaf/`, `docs/b.md` (its end) | XX-01 | `test/test_b.py` |
| Paths | `docs/paths/p.md` (its rows) | | |
"""
WORKPATH = """| Task | Start here | Contract | Tests |
| --- | --- | --- | --- |
| Gamma | `scripts/checks/<check>.py` | | |
"""
TODO = """## Phase 1

### 1.1 One row

Check: `test/test_a.py` passes.

### 1.2 Two layers and a contract

Check: by hand, `src/leaf/x.py` and `src/project/p.py` keep XX-01.

### 1.3 A pattern row

Check: `scripts/checks/g.py` holds; this goes to Ghost.

### 1.4 Nothing named

Check: as 1.1.

### 1.5 A protected file

Check: `theGhost.md` gains a line.
"""
SIZES = {"docs/a.md": 40_000, "docs/b.md": 8_000, "src/leaf/x.py": 32_000, "src/leaf/sub/deep.py": 99_999, "src/project/p.py": 12_000,
         "test/test_a.py": 4_000, "scripts/checks/g.py": 20_000, "docs/paths/p.md": 400, "theGhost.md": 400}

# A stamped TypeScript project's shape (3.3): CLAUDE.md's stack row is a pattern naming a file, and a workpath's row
# names the when files by `*`; TODO 0.3 and 0.4 as the stamp writes them name a file beside each.
STAMPED_CLAUDE = """| Task | Start here | Contract | Tests |
| --- | --- | --- | --- |
| A stack's tooling | `stacks/<language>/README.md` | C-018, C-034 | `scripts/gate.sh` |
"""
STAMPED_WORKPATH = """| Task | Start here | Contract | Tests |
| --- | --- | --- | --- |
| A when file | `docs/when/*.md` | C-020 | `test/test_pointers.py` |
"""
STAMPED_TODO = """## Phase 0

### 0.3 The stack wired

Check: `stacks/typescript/gate.sh` runs green under its image, mutation included; its STAMP markers gone.

### 0.4 Tune-up pass 0

Check: `docs/when/tune-up.md` followed in full; the metrics table written.
"""
STAMPED_SIZES = {"stacks/typescript/README.md": 8_000, "stacks/typescript/gate.sh": 4_000, "docs/when/tune-up.md": 12_000, "scripts/gate.sh": 2_000}


def placed(floor: str) -> list[str]:
    """The fixture's report with the map's floor at the given grade."""
    rows = score.routing_rows(CLAUDE) + score.routing_rows(WORKPATH)
    return score.report(TODO, score.grade_map(GRADES.format(floor=floor)), rows, SIZES, ["src/leaf", "src/project"], ["C", "XX"])


class ThePlacing(unittest.TestCase):
    def test_the_table_worked_by_hand(self) -> None:
        heads = [line.split(" — ")[0] for line in placed("small")]
        self.assertEqual(heads, ["1.1 small (Model S, 40 tool calls), 0 points", "1.2 mid (Model M, 120 tool calls), 6 points",
                                 "1.3 strong (Model L, no tool-call limit), 0 points", "1.4 unplaced",
                                 "1.5 small (Model S, 40 tool calls), 3 points"])

    def test_a_stamped_typescript_project_s_0_3_and_0_4_score_with_rows(self) -> None:
        """0.3's `stacks/typescript/gate.sh` sits in the folder of the pattern row `stacks/<language>/README.md`; 0.4's
        `docs/when/tune-up.md` in the folder of `docs/when/*.md`. Working sets: 0.3 opens only its named file (the pattern
        opens nothing of its own), 4,000 characters; 0.4 likewise, 12,000: +0 each; neither Check names a test or a script."""
        rows = score.routing_rows(STAMPED_CLAUDE) + score.routing_rows(STAMPED_WORKPATH)
        lines = score.report(STAMPED_TODO, score.grade_map(GRADES.format(floor="small")), rows, STAMPED_SIZES, [], ["C"])
        self.assertEqual(lines, ["0.3 small (Model S, 40 tool calls), 0 points — nothing; rows: A stack's tooling",
                                 "0.4 small (Model S, 40 tool calls), 0 points — nothing; rows: A when file"])

    def test_the_facts_are_written(self) -> None:
        lines = placed("small")
        self.assertIn("working set 11,000 tokens (+1), a runnable Check: line (-2); rows: Alpha", lines[0])
        self.assertIn("working set 13,000 tokens (+1), layers src/leaf, src/project (+2), contract XX-01 (+3); rows: Beta", lines[1])
        self.assertIn("a runnable Check: line (-2), waits on Ghost; rows: Gamma", lines[2])
        self.assertIn("contract theGhost.md (+3)", lines[4])

    def test_a_floor_raises_every_placement(self) -> None:
        heads = [line.split(" — ")[0] for line in placed("mid")]
        self.assertEqual(heads[0], "1.1 mid (Model M, 120 tool calls), 0 points")
        self.assertIn("raised to the floor from small", placed("mid")[0])
        self.assertTrue(placed("strong")[1].startswith("1.2 strong"))

    def test_the_workpaths_are_the_rows_claude_md_starts_at(self) -> None:
        self.assertEqual(score.workpaths(CLAUDE), ["docs/paths/p.md"])

    def test_a_routing_name_covers(self) -> None:
        cases = [("stacks/<language>/README.md", "stacks/java/README.md", True), ("stacks/<language>/README.md", "stacks/a/b/README.md", False),
                 ("src/leaf/", "src/leaf/x.py", True), ("README.md", "docs/README.md", True), ("docs/a.md", "docs/ab.md", False),
                 ("stacks/<language>/README.md", "stacks/typescript/gate.sh", True), ("stacks/<language>/README.md", "stacks/typescript/", True),
                 ("stacks/<language>/README.md", "stacks/typescript/starter/x.json", False), ("docs/when/*.md", "docs/when/tune-up.md", True),
                 ("docs/when/*.md", "docs/when/", True), ("docs/when/*.md", "docs/when/sub/x.md", False), ("docs/when/*.md", "docs/whenever.md", False),
                 ("docs/when/grades.md", "docs/when/tune-up.md", False)]
        self.assertEqual([score.covers(row, path) for row, path, _ in cases], [want for _, _, want in cases])

    def test_the_prefixes_are_the_core_the_project_and_the_contract(self) -> None:
        self.assertEqual(score.prefixes("### C-001: a\n### NR-001: b\n", "## HAR-01 x\n"), ["C", "NR", "HAR"])


class TheMap(unittest.TestCase):
    def test_the_real_map_places(self) -> None:
        self.assertEqual(score.map_problems(score.grade_map((ROOT / "docs/when/grades.md").read_text())), [])

    def test_the_planted_break_is_caught(self) -> None:
        found = score.map_problems(score.grade_map((BROKEN / "score/docs/when/grades.md").read_text()))
        self.assertEqual(found, ["the grade map gives no points for 'contract' (a row of the table Fact | Per | Points)"])

    def test_a_floor_that_is_not_a_grade_is_caught(self) -> None:
        self.assertIn("the grade map's Floor line names 'ruling', not one of ['small', 'mid', 'strong']",
                      score.map_problems(score.grade_map(GRADES.format(floor="ruling"))))


class TheCommandLine(unittest.TestCase):
    def test_one_line_per_open_item(self) -> None:
        result = subprocess.run([sys.executable, "-I", str(ROOT / "scripts" / "score.py")], capture_output=True, text=True)
        numbers = [item for item, _ in score.items((ROOT / "TODO.md").read_text())]
        self.assertEqual((result.returncode, [line.split(" ")[0] for line in result.stdout.splitlines()]), (0, numbers))
