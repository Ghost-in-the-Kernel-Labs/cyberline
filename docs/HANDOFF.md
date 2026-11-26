# Handoff: what to work on next, and what is waiting on whom

Read `CLAUDE.md` first, then this. `TODO.md` is the chain in order; `docs/DONE.md` is what is finished.

## Where the project stands (2026-11-26)

Stamped from Ghost-Core today. Nothing of Psiberline's own is built; the template's documents, checks and
gates are in place and green.

## For Ghost: waiting on you

1. Name this project's ghost (`docs/GHOST-IN-THE-KERNEL.md`, TODO 0.1).
2. Pin the stack's image digest and dependencies; wire mutation (TODO 0.2); every `STAMP` marker in the tree is a line to fill (`grep -rn STAMP .`).
3. Write the roadmap's §1 to §6 and Phase 1's items in `TODO.md` (TODO 0.3).
4. Write the first invariants of the contract and set `docs/modules.json` (TODO 0.4).
5. Confirm P-002's wording (comments say what, never why), and say whether a check should hold it: one that reads comments in `src/` for reasons, with a planted break, once the stack is wired.
6. Write the founding decisions in `theGhost.md`, a decision for each core decision this project refuses among them (TODO 0.5): agents cannot author them.

## Trials: questions settled by a run, not an argument

(none yet)

## What to distrust

- The stack's gate has not run under its image until TODO 0.2 is done.
- Until TODO 0.2 lands the gate refuses at the stack (`stacks/typescript/gate.sh`), so only `scripts/commit.sh --docs-only` commits are open: 0.1 lands that way, touching `docs/` alone, and its move from `TODO.md` to `docs/DONE.md` rides in 0.2's commit.
- `docs/AGENT.md`'s Fast loop and Gate cells are Ghost-Core's numbers until Tune-up pass 0 re-measures them here.
