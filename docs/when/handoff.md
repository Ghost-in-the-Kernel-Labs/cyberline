# Handoff: finishing a task, and reviewing one (C-025, C-026)

Read this when you finish a task, and when you review one. Handing a task out (the brief, the
report, the Cost line): `docs/when/hand-out-a-task.md`.

## Finishing a task

1. The fast loop green (`scripts/fast.sh`), and the item's own check where it has one.
2. Your debrief in `docs/NAVIGATION-LOG.md`, as its header says: Task, Opened (files, in order),
   Complaints, Suggestions. Not the task's own findings; those go in the journal. "none" is an answer.
3. Your journal entry, if an event happened (a contradiction, a decision, a failure caught).
4. Save (`scripts/save.sh -m <message>`) when you work on a session branch, so nothing you built is dirty
   or unpushed when your turn ends (C-040); on `main` there is nothing to save.
5. Report as your brief says (`docs/when/hand-out-a-task.md`, "The report"). Land only if its
   commit mode says so, and then through `scripts/commit.sh` after `scripts/gate.sh --fast`, never a raw commit
   on `main` (`docs/when/tune-up.md` says why).

## Reviewing a task (the strong grade)

Read the diff against the task; run the fast checks (`scripts/gate.sh --fast`); write the journal entry; land what
the worker saved on its branch, through `scripts/commit.sh`; ship (`scripts/ship.sh`). A tune-up's diff is
read against the agent's notes; a fix that reached past the may-change list is reverted.

Why: a fresh agent meets the repository as a newcomer does, so its trouble is the repository's, and
its debrief is where that trouble is written down for the tune-up to read (Katana R-078).
