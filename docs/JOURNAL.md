# Journal: every event in the work, as a record a researcher can count

One entry per event: a contradiction found, a decision taken, a failure caught or missed, a change of
direction, a measurement. Not a restatement of the commit log (`git log` has what changed), not a
status list (`docs/DONE.md`, `TODO.md`) and not the design (`theGhost.md`): the journal records *what
happened while the work was done*: what was intended, what was found, what was on the table, how it
was resolved, and what it touched. Fixed fields, kept identical across every Ghost project so entries
can be counted and compared (C-015). Newest last. Written by whoever was there, in the same commit as
the event; an agent writes its own entries.

Entries live in `docs/journal/`, a hundred to a file (`J-000-099.md` holds J-001 to J-099,
`J-100-199.md` the next hundred), behind `docs/journal/INDEX.md`, written by
`scripts/journal_index.py`; `test/test_journal.py` fails when the index is stale. A new entry goes at
the end of the newest file; past J-n99 a new file begins. Take the number from `scripts/next_id.py`
after `git fetch origin main` (two sessions once took the same number).

## The fields

An entry is `### J-nnn title` and these lines, every one present (`none` is an answer):

- **Who**: Ghost, or the agent by its model name, or both.
- **Class**: one of `contradiction` (the plan disagreed with itself or with reality), `ambiguity`
  (two readings, both reasonable), `failure-caught`, `failure-missed`, `decision`, `measurement`,
  `direction`, `feature` (a numbered item built, with nothing caught or decided beyond its check), `trial` (a question settled by running something: name the trial, its result and
  the decision it produced), `deferred` (a question parked with its default taken; closed by a later
  `decision` entry naming it), `conflict` (another agent's work against this one: **Mine** and
  **Theirs** stated, listed under HANDOFF's "For Ghost" until its **Resolved** names Ghost).
- **Intent**: what the work was trying to do when the event happened.
- **Found**: the fact the event turned on.
- **Options**: what was considered, including the one taken and the ones refused.
- **Resolved**: what was done, by whom.
- **Touched**: decisions, metrics, documents or modules the event changed or created.
- **Caught by**: for a failure, what noticed it (a test, a run, a person, an agent's habit, luck).
- **Cost**: grade, score (the `scripts/score.py` line, or `—`), tool calls, tokens (numbers or `not reported`), commits, wall time where known
  (`docs/when/hand-out-a-task.md`: a worker's report carries them).
