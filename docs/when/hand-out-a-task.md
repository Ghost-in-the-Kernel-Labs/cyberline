# Handing out a task: the brief and the report (C-036, C-026)

Read this when you hand a task to an agent. The task goes out as a one-page brief and comes back as a
one-page report; the next grade starts from the report and the diff, never from the transcript. A
report that will not fit a page says the task was placed too low (C-036). Finishing and reviewing a
task: `docs/when/handoff.md`.

## Before you write it

- A new task gets a fresh agent of its grade (`docs/when/grades.md`), briefed with the task, not with
  what earlier runs found: what a run learned is carried by the repository (the journal, `TODO.md`,
  the routing rows). Resume an agent only within one unfinished task, on the same files, while its
  context is small.
- The item is ready. An item whose only text is its `Check:` line, with no plan line to build from
  (its step in `docs/ROADMAP.md`), is not: write the plan first. An open question a later item
  depends on is copied into that item, not left in the journal.
- Name a file by its repository path. Name a class or a function only after `grep -rn` shows it (or
  shows a new name absent). A number carried into the brief says where it came from. A pointer names
  a symbol or a heading, never a line range.
- A name the item's `Check:` line uses (a file, a helper, a function) is copied into the brief as the
  Check spells it, never renamed. A parent project's id is copied from the survey row or the source it
  came from, or marked "(verify)": an id carried from memory is wrong more often than it looks.
- Read the body against the documents it quotes before you hand it out: a heading or a rule quoted
  from memory is wrong more often than it looks.
- The working set is the Start-here files of the routing row the item matches, plus the files the
  item names; nothing else. Say explicitly what the agent may and may not do: agents read silence
  literally.

## The brief

Copy the block, fill each `<...>`, delete nothing; a field with nothing in it says "none".

```text
You are a <small|mid|strong>-grade worker (docs/when/grades.md) for <project>, TODO <n.n>: <title>.
Repository <path>, branch <branch>. Read CLAUDE.md first; its rules bind you, and this brief only narrows them.
Every reply you write, this report included, starts with the words "Context Canary".

Objective: <one sentence>.
Pass line: <the item's Check: line, quoted whole>.
Plan and evidence: <the item's roadmap line; each journal, survey or decision row it rests on, by id>.
Working set: <the routing row's Start-here files> and <the files the item names>. Nothing else, except a
test, a fixture, a document or a golden the change must regenerate, the journal, TODO.md, docs/DONE.md
and docs/NAVIGATION-LOG.md.

Stop limits: stop at the first you reach, change nothing further, and report.
1. One attempt at a change the fast loop or the gate rejects for a reason you cannot explain in one
   reading; then the next grade up (docs/when/escalation.md).
2. A file outside the working set, other than those it names.
3. <40 | 120 | no limit> tool calls in all (your grade's, docs/when/grades.md).
4. A choice this brief does not settle (a schema, a name, a threshold): ask in the report, never pick.

Never: weaken a test or a check to pass; change an auto-execution surface without naming its decision in the commit, or theGhost.md beyond a cross-reference
its header allows (See also, Held by); add a dependency; push; create or edit a hook or anything under
.claude/; git stash, --amend, reset or force; stop, undo or overwrite what you did not start.

Commit mode: <save only: scripts/save.sh -m "<what changed>" on your branch at the end of each item and before
your turn ends; the coordinator lands it | land, one commit per item: scripts/gate.sh --fast, then
scripts/commit.sh -a -F -, authored as Ghost, subject "<n.n> <what changed> (J-nnn)", the fast checks' verdict
line quoted; if commit.sh says a tune-up is due, stop: the coordinator makes it>. Never a raw commit or push
on main (C-040).

Finish as docs/when/handoff.md says (the debrief), then report as docs/when/hand-out-a-task.md's
"The report" says: one page, the only thing the coordinator reads.
```

The closing sentence stays: a brief that describes only the report is read as the whole finish, and
the debrief is missed.

## The report

```text
Context Canary
Grade: <grade>. Task: TODO <n.n>.
Asked: <one sentence>.
Commits: <hash and subject, each landed> | saved on <branch> (scripts/save.sh: its last short SHA).
Pass line: <its result; the fast-loop or gate verdict line>.
Tried and failed: <what, each with the exact failing output> | none.
Files read: <in order>.
Tool calls: <n>. Tokens: <n> | not reported.
For Ghost: <each choice the brief left open, with the reading taken> | none.
```

The agent that started the worker reads the report, never the transcript, and re-reads nothing the
worker read. A missing canary is an alarm: the worker's instructions slipped from view; a present one
is not a clean bill. The report's grade, tool calls and tokens go into the Cost line of the task's
journal entry, with the other fields `docs/JOURNAL.md` names: a worker cannot see its own token count, so `not reported` is an
answer and a guess is not.

Why: the posture was written in Suite Builder when the coordinator's own long session, re-reading
itself every turn, was the largest cost of a week (SB G-357; G-361 for the report as the hand-off one
grade up); Employee Evaluator (E-092) and Neon Rain (R-039, its docs/rules/brief.md, whose template this
follows) took the brief and the report as a page each. The hygiene list is AI Slop Block's nine
incidents in six days (J-034 to J-089), the posture's own first escalation among them, a heading
quoted from memory, and Katana's J-338: a brief's names are checked against the tree before it goes
out. A resumed agent at about 275k tokens missed three gaps a fresh one found (Katana R-078); a brief
without the closing sentence lost the debrief twice (Katana J-253, N-005).
