# Grades: which model each grade is (C-036)

Read this when you hand out a task, escalate, or need to know what a grade gets. This is the one file
that names models; every other instruction names the grade, and `scripts/checks/grades.py` fails the
fast loop on a model's name anywhere else an agent is instructed. (Your system prompt names your model;
this table gives its grade.)

| Grade | Model | Most points (provisional) | Tool calls | Gets |
| --- | --- | --- | --- | --- |
| small | Claude Haiku | 3 | 40 | mechanical work inside one routing row, with a mechanical pass line |
| mid | Claude Sonnet | 7 | 120 | a feature over a few files; small's escalations; gate-fix loops; placing the items the score left unplaced |
| strong | Claude Opus | no limit | no limit | the coordinator; design; Ghost's questions; security; failures whose cause is unknown; mid's escalations |
| ruling | Claude Fable | — | — | no items; answers questions, which go to it first and to Ghost last |

The score (`scripts/score.py`) places an item by these points, from facts, no model (C-036):

| Fact | Per | Points |
| --- | --- | --- |
| working set | 10,000 tokens (characters / 4) of the Start-here files of every routing row covering a file the item names, plus the named files | 1 |
| layer | each code layer beyond the first (a module folder `docs/modules.json` names, or `scripts/`) | 2 |
| contract | a decision or invariant id, or a protected file | 3 |
| mechanical | a `Check:` line naming something runnable | -2 |

The total is floored at 0; an item waiting on Ghost is strong whatever its points; an item naming no
file is unplaced, and the mid grade places it.

Floor: mid

An item is placed at the lowest grade whose most points its score is within, then raised to the floor
if it is below it. The floor raises every duty the first table gives a grade below it, since none of
a project's work is placed under its floor (C-036): where the floor is strong, the strong grade places
the items the score left unplaced and runs the gate-fix loops. A worker stops at the first limit it reaches (C-036): one attempt at a change the
checks reject for a reason it cannot explain in one reading, then the next grade up; a file outside
its brief's working set; its tool calls; a choice its brief did not settle. When you start an agent
with the Agent tool, its `model` is the grade's model in lower case, its first word dropped (mid:
`sonnet`).

## Provisional

The points (the table above, the ones `scripts/score.py` reads), the most points of each grade and the
tool-call limits are Suite Builder's, unmeasured here, set on 2026-11-06. They move only by a decision
made from this project's Cost rows, never by an edit to this table alone: `scripts/metrics.py` counts
the journal entries since that date whose Cost line names a grade and an exact tool-call count
(`docs/when/coordinate.md`, "Ending a session").

Why: Ghost-Core's floor is strong because a template is held to a higher standard than the projects
stamped from it (Ghost, 2026-11-06); a stamped project's default is mid. One table, held by a check,
because a model's name copied into an instruction outlives the model (Neon Rain's first run found
seven stray files).
