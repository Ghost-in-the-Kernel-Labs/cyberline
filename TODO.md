# TODO: the open items, in order

The roadmap as a chain: items are done in this order, never out of it, and an item that cannot be
done as written stops the chain and goes to Ghost (C-016). Each item's plan is its step in
`docs/ROADMAP.md` §6, by the same number; its check is copied here. A done item moves to
`docs/DONE.md` with its number kept. `test/test_todo.py` holds this file: headings in numeric order
under their phase, the first open item has a check, every phase ends with a tune-up pass (a reopened phase
of at most three new items with a tune-up commit, `docs/when/tune-up.md`), and
nothing is both here and done or done twice. An item that waits on something outside the repository (Ghost's choice
or approval, counsel, another project) carries a `Waits on:` line naming it in words, or one of the two kinds with a
shape for what a session lacks, `Waits on: environment (<host or tool>)` or `Waits on: reference (<what>)`
(`scripts/checks/todo.py`), and moves to the last phase, headed `## Phase W: waiting on Ghost`, keeping its number and adding a `Moved: from Phase N` line; a phase
whose every item waits takes its tune-up pass with it (the pass's `Waits on:` names those items), and the waiting
phase needs no pass of its own. When what it waits on arrives, Ghost moves the item back into the chain. An open
question a later item depends on is copied into that item's text, so the item reads whole where it stands.

## Phase 0: founding

### 0.1 This project's ghost, named

Check: `docs/GHOST-IN-THE-KERNEL.md`'s "This project's ghost" section replaced by Psiberline's; the STAMP comment gone; committed by `scripts/commit.sh --docs-only` with every staged path under `docs/` (the gate refuses at the stack until 0.2), so the item's move from `TODO.md` to `docs/DONE.md` rides in 0.2's commit.

### 0.2 The stack wired

Check: `stacks/typescript/gate.sh` runs green under its image, mutation included, so `scripts/gate.sh` passes and records the tree; `stacks/typescript/PRESENT` present; its STAMP markers gone; each pin of the founding lockfile and image has its `unreviewed baseline` row in `docs/REVIEWED-VERSIONS.md` (`python3 -I scripts/checks/dependency_review.py --baseline J-nnn` prints them; `docs/DEPENDENCY-REVIEW.md`, "The record"); the first commit through the gate lands, carrying 0.1's move to `docs/DONE.md`.

### 0.3 The roadmap and TODO filled

Check: `docs/ROADMAP.md` §1 to §6 written for Psiberline (its STAMP line gone, Phase 1 planned in §6) and `TODO.md` holds Phase 1's items in order, each with its Check line, ending with its tune-up pass.

### 0.4 The contract and the leaf module

Check: `docs/CONTRACT.md` renamed and its first invariants written; `docs/modules.json`'s package and modules set; `test/test_contract.py` and `test/test_modules.py` green on the real folders.

### 0.5 The founding decisions

Check: `theGhost.md` holds Ghost's founding decisions for Psiberline, a decision for each core decision it refuses among them, each with Ghost as its Source. Agents cannot author Ghost's decisions: an agent drafts the questions for Ghost in `docs/HANDOFF.md`, and a builder that reports "waiting on Ghost" has done its job.

### 0.6 Tune-up pass 0

Check: `docs/when/tune-up.md` followed in full; the metrics table written; the navigation log's "Last review" set.
