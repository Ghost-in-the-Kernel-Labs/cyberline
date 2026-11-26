# Navigation log: what agents found hard to find

Each new task goes to a fresh agent of the grade it is placed at (C-026, C-036; `docs/when/grades.md`). At the end of its task the agent
debriefs here: one entry, its complaints and suggestions about finding its way (routing rows,
documents, names, rules that were unclear), not about the task's code. "none" is an answer.

**The review is part of every tune-up** (steps 4 and 5 of `docs/when/tune-up.md`; C-024, C-025;
`scripts/commit.sh` says when one is due): read the entries for what agents who did not see each other converge on; wipe the entries
(git keeps them); check each item against the code and act on the valid ones; take an open question
to the ruling grade; record the review in the journal; set the line below to the commit the
review ran at (`git rev-parse --short HEAD`, not the tune-up's own, which does not exist yet). Each entry's **Opened** list, read against the routing row its task matched, is the measure
of whether a fresh agent found its way: files, in order; `CLAUDE.md` does not count.

Last review: f2b6e21 (2026-11-26, tune-up commit at Ghost's word: one debrief, the core update's, its complaint noted; entries wiped)

## Entries

An entry is `### <date> · <task> · <model>` and these lines:

- **Task**: what the agent was asked.
- **Opened**: the files it opened, in order.
- **Complaints**: what slowed or misled it.
- **Suggestions**: what it would change.

### 2026-11-26 · the core update to 56cb5ed · Fable

- **Task**: take Core C-049, the landing from a session branch.
- **Opened**: `docs/when/core-update.md`, `theGhost.md`, `CLAUDE.md`, a fresh stamp of the core beside the last one.
- **Complaints**: none
- **Suggestions**: none

### 2026-11-26 · the handoff for a cold start · Fable

- **Task**: leave the repository so a session with no memory of this one can begin.
- **Opened**: `docs/HANDOFF.md`, `TODO.md`, `docs/DONE.md`.
- **Complaints**: none
- **Suggestions**: none
