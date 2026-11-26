# Escalation: a question, or a change that stays red (C-027, C-028, C-036)

Read this when your brief does not settle a choice, when the fast loop or the gate is still red after
your first attempt at a change, or when you are the grade an agent below you asked for help. Your
system prompt names your model; `docs/when/grades.md` gives its grade and the grade above it.

## The ladder: what goes where

- **A question** (a choice your brief did not settle; a contract not precise enough to build from)
  goes to the ruling grade first, and to Ghost last, only when the ruling grade cannot answer it or
  the question is Ghost's by a decision (a Status, a dependency, a surface's behaviour). A worker an agent
  started asks it in its report and never picks (the brief's stop limit 4); the agent that started it
  takes it up the ladder.
- **A failure** (red after one attempt, the cause not plain from the output) goes one grade up:
  small to mid, mid to strong, strong to Ghost. Never a second attempt of your own first.
- **A fix you can see is not an escalation.** A red run whose output names the cause (a typo, a
  missing import, a rule the check quotes, a command that regenerates a file): fix it and run again.

## How a failure goes up

- **Through the agent that started you**, when one exists: stop, and hand back your one-page report
  (`docs/when/hand-out-a-task.md`, "The report": the task, the exact failing output, the files you
  read in order; your diff stays in your tree). That report is the hand-off; the agent that started you takes it to the
  next grade, which starts from the report and the diff, never your transcript.
- **Directly**, when no agent started you and you have the Agent tool: invoke the next grade (its
  `model` from `docs/when/grades.md`) with the same report. It advises; you make the edits (one
  writer per working tree, `docs/when/conflict.md`) and run the check yourself.
- **A worker with no Agent tool** hands back, and that is its escalation: do not keep trying. The
  receiving grade logs it as `no-advisor` when no one above could be reached.
- When the receiving grade asks you to replay what you did, answer as a record of actions (which
  files, which commands, in order), not your reasoning. "I cannot remember" is a fine answer.
- Name the escalation in your journal entry and your debrief.

## If you are the grade asked to help

1. Ask for the replay: the instructions followed and the files opened, in order.
2. Check that what the task needed reached the agent at its start: CLAUDE.md's row, the when-line,
   the item's text, the brief. Decide the kind: `missing-row`, `not-read`, `wrong-row`,
   `stale-pointer`, `hard`, `no-replay`, `no-advisor` (`docs/ESCALATIONS.md`). A conflict between
   agents is not an escalation: it stops the work at once (`docs/when/conflict.md`, C-029).
3. Log one row in `docs/ESCALATIONS.md`. Three open rows of one kind go to Ghost under
   `docs/HANDOFF.md`'s "For Ghost" for a routing pass; the test refuses the third without it.
4. Then help with the fix. If your answer also fails, it goes one grade further up; past the
   strong grade, stop and tell Ghost.

## Sprint mode: when Ghost is away

In an unattended run the ladder holds without him: a question goes to the ruling grade, a failure to
the next grade, and Ghost is asked only at a phase boundary (a phase's tune-up, a decision only he
may make), with the questions gathered under `docs/HANDOFF.md`'s "For Ghost". An item that waits on
Ghost carries its `Waits on:` line and moves to the waiting phase (`TODO.md`'s header), so the run goes
on past it. When the open list empties, the coordinator takes the next item of the roadmap
(`docs/ROADMAP.md`) into `TODO.md`, with its Check, and goes on.

Why: the cheaper grade does the routine work; the costly failure is retrying a hard fix until
something passes for the wrong reason, usually a weakened test (Suite Builder G-282, Katana R-073,
EE E-060). An agent that could not escalate spent 108 minutes on a metric no edit of its could fix
(Neon Rain J-032), hence `no-advisor`. As practised, a question went to the ruling grade first and a
failure one grade up, Ghost last; a stopped worker reported to the agent that started it (SB G-361);
Katana's log gained no rows in 676 commits because its escalations ran as question rounds in the
journal (Core's second survey, LESSONS-2026-11, Part 2 row 6). The replay is the measure of the route: the log is
how routing rows get fixed, not the fix itself.
