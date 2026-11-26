# The agent's environment: its contract and its metrics

What an agent working here can count on, and the metrics every tune-up re-measures and ratchets
(C-022, C-023, C-024). A metric may improve; it never regresses without a decision in `theGhost.md`.
Until a metric is first measured within its target it is "not armed" and not compared; a row whose
target is "—" is informational, counted and never armed;
`test/test_metrics.py` holds the table to what `scripts/metrics.py` measures.

## The contract

- **AGT-01 Cloud-primary.** A clean clone runs the fast loop and the gate in the session's
  container with nothing installed beyond the stack's lockfile; no recipe has a step that runs only
  on the maintainer's machine.
- **AGT-02 The fast loop runs under its ceiling.** Doc checks and unit tests only; no data, no
  network, no cache that can skip a doc test (F-03).
- **AGT-03 Mandatory context stays under its ceiling.** `CLAUDE.md` plus whatever an agent must
  read before a task.
- **AGT-04 A routing row opens at most five files, none over 400 lines.**
- **AGT-05 Every generated artifact has a command that regenerates it and a test that fails when
  it is stale**: `docs/decisions.md`, `docs/journal/INDEX.md`, this table's Measured column.
- **AGT-06 Every check rejects a planted break.** A check that cannot fail is not a check.
- **AGT-07 The session is the machine.** The gate is the definition of done; CI is spent by hand
  (C-032).
- **AGT-08 A failing check says what to do in its first line.**

## The machine

The session's container, on which AGT-01 and AGT-07 stand: measured facts, not contract items. A
stamped project inherits these lines and its tune-up pass re-measures the first.

- 2 cores, 7 GB of memory, measured 2026-11-07 (`nproc`, `free -g`); sessions differ, so a gate's
  minutes are compared on the machine that measured them.
- A background task lives at most two hours, an idle container is reclaimed within minutes, and a
  restart kills every process; what a long run does about each is `docs/when/long-run.md` ("The
  machine").
- One gate runs per clone (.git/ghost/lock, C-037); nothing a recipe needs runs only on the
  maintainer's computer (AGT-01).

## The metrics

| Metric | Target | Measured | Why it matters to the agent |
| --- | --- | --- | --- |
| Mandatory context (words) | < 1,200 | 1073 | every task pays it |
| Fast loop (s) | < 30 | 24.2 | run after every edit |
| Gate (min) | < 10 | 5.0 | paid before every push |
| Largest source file (lines) | < 400 | 378 | fits a read without paging |
| Files a routing row opens | ≤ 5 | 2 | the first five reads decide the task |
| Decisions without `See also` | 0 | 0 | links find what grep misses |
| Stale generated files | 0 | 0 | AGT-05 |
| Docs lines per source line | < 0.35 | 444.3 | Suite Builder reached 0.37 and it hurt; unarmed until there is source |
| Cost rows since the thresholds were set | — | 0 | informational, never armed: `docs/when/grades.md`'s provisional numbers move only by a decision from these rows (C-036) |

## Re-measuring (a tune-up pass, C-024)

Step 2 of `docs/when/tune-up.md`: `scripts/gate.sh` (its log is build/gate.log), then
`python3 -I scripts/metrics.py --fast-loop <s> --gate <min> --write`. It refuses while an armed
metric has regressed: a question for the hand-back, never a number or a target to edit.
