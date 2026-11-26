# Psiberline

A deterministic chain that turns solar software requirements into controlled English (EARS), a typed and checked representation, and then tests and application modules composed from verified fixtures, with no AI in the chain.

## Status

No feature exists yet. The project is stamped from Ghost-Core 31a0aee; it begins at TODO 0.1, and
`docs/HANDOFF.md` says what the human fills in first.

## Running the fast loop

    bash scripts/fast.sh

Every document check and unit test, with nothing installed; `scripts/save.sh` saves a session's work on its own
branch, `scripts/gate.sh --fast` is the check before a landing (`scripts/commit.sh`), `scripts/ship.sh` the only push
to `main`, and the full `scripts/gate.sh` runs at each tune-up (C-040).
