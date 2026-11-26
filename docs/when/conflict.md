# Conflict: another agent's work against yours (C-029)

Read this when another agent's work breaks yours, contradicts your task, or keeps changing what you
just changed.

1. **Stop at once.** Not after three; there is no retry and no count.
2. **Assume a conflict of objectives, never sabotage.** From inside one agent's view the two look
   the same; only Ghost can tell them apart.
3. **Write it down:** a journal entry of class `conflict` (`docs/JOURNAL.md`) with **Mine** and
   **Theirs**, each objective stated plainly as you understand it, with no guess at intent.
4. **List it** under `docs/HANDOFF.md`'s "For Ghost", and wait. It stays listed until its
   **Resolved** line names Ghost (`test/test_journal.py` holds this).
5. **Never touch what you did not start:** never kill or stop a process another agent or person
   started (and never `pkill -f` anything: the pattern matches your own command); never revert,
   force-push over or rewrite another agent's commit; never force-push at all, not even by
   agreement, that is Ghost's alone; never edit the journal, the escalation log or `theGhost.md` to
   get around a conflict; never `git stash`, reset or check out in a working tree you share: it
   sweeps up others' uncommitted work with yours.

One writer per working tree: an agent you invoke to advise (the next grade up, a reviewer) reads; you
edit. An agent that starts other agents gives each its own files or worktree and an objective that
cannot collide, and commits only its own changes.

Why: three agents with conflicting objectives overwrote each other's work and ran kill scripts
against each other, each assuming sabotage, and none told the human who could have deconflicted
them (EE E-066, Neon Rain J-023). A trial ran `pkill -f` twice and killed its own check run
(Suite Builder, many-agents.md).
