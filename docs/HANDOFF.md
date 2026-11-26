# Handoff: what to work on next, and what is waiting on whom

Read `CLAUDE.md` first, then this. `TODO.md` is the chain in order; `docs/DONE.md` is what is finished.

## Where the project stands (2026-11-26)

Founded in one session, whose container no longer exists: everything it made is in this repository and
Ghost-Core's. Done (`docs/DONE.md`): 0.1 this project's ghost, 0.2 the stack wired and the first ship, 0.3 the
roadmap and Phase 1's chain. On the same day the work was split in two (P-021): Psiberline is the compiler, and the language is a second project whose repository does not exist yet. `VISION.md` is the compiler's approved long form; `docs/ROADMAP.md` is its plan. The full gate
passes in about half a minute, mutation included. The core is taken up to Ghost-Core 56cb5ed, with one later fix to the
gated commit copied in (J-009).

Next in the chain: 0.4 the contract and the leaf module; 0.5 the founding decisions, which are Ghost's to write
(an agent drafts the questions); 0.6 Tune-up pass 0; then Phase 1, the first slice.

## Starting a session cold

Clone; `git config user.name Ghost` and the email in `CLAUDE.md`; a session branch before the first edit
(`git checkout -b claude/<session>`), since `scripts/commit.sh` refuses on `main` (P-004). `scripts/fast.sh` needs
nothing installed. The stack's gate needs npm 11 or newer and a session's container ships npm 10:
`npm install -g npm@11 --ignore-scripts`, then `npm ci --ignore-scripts`. A landing is `scripts/save.sh`,
`scripts/gate.sh --fast`, then `scripts/commit.sh -a -F <message> --ship`.

## For Ghost: waiting on you

0. The split (P-021, J-012): Psiberline is the compiler. Three things are yours: the language project's name and its repository, which an agent cannot create; where the tree's format is written down (the agent's proposal: in the language project, Psiberline pinning a version, and here until that repository exists); and the seven founding decisions that are about the language (P-005, P-006, P-007, P-012, P-013, P-014, P-015): say for each whether it is withdrawn here and re-made there, or stands here as what the compiler expects of its input.
1. Confirm the wording of P-005 to P-020, the founding decisions (J-010, J-011): you took the options the agent set out; the words are the agent's.
2. Confirm the wording of this project's ghost (`docs/GHOST-IN-THE-KERNEL.md`, J-002): drafted from `VISION.md`.
3. Confirm P-002's versions (vitest 4.1.12, typescript 7.0.2, knip 6.46.1, @stryker-mutator/core 10.1.1), the agent's choice (J-003).
4. Write the first invariants of the contract and set `docs/modules.json` (TODO 0.4); TODO 0.5 closes after it, its decisions being written.
5. Who owns the chain after it is carried into the adopting organisation (`VISION.md` section 16; P-018 waits on it).
6. The roadmap (`docs/ROADMAP.md`, J-013): re-cut to the compiler, Phases 1 to 3 numbered and 4 to 6 outlined from `VISION.md`; the order and the items are the agent's, for your ruling.

## Overrides to remove once past the cooldown

Each holds a version the founding lockfile would have brought in younger than seven days to the highest version of
its major older than that (J-003). A tune-up removes one when its newer version is past the cooldown; removed, the
newer version comes in by `docs/DEPENDENCY-REVIEW.md` like any update. The three Babel keys are scoped to the 8.1 line,
since the lockfile also holds 8.0.10 of each.

`@babel/generator@^8.1.0` 8.1.2, `@babel/helper-module-transforms` 8.1.2, `@babel/helper-string-parser` 8.1.2, `@babel/helpers` 8.1.2, `@babel/parser@^8.1.0` 8.1.2, `@babel/plugin-transform-explicit-resource-management` 8.0.5, `@babel/plugin-transform-modules-commonjs` 8.1.2, `@babel/plugin-transform-typescript` 8.0.6, `@babel/traverse@^8.1.0` 8.1.2, `@babel/types` 8.1.2, `@inquirer/ansi` 2.1.0, `@inquirer/checkbox` 5.3.0, `@inquirer/confirm` 6.4.0, `@inquirer/core` 12.1.0, `@inquirer/editor` 5.4.0, `@inquirer/expand` 5.2.0, `@inquirer/external-editor` 3.1.0, `@inquirer/figures` 2.1.0, `@inquirer/input` 5.2.0, `@inquirer/number` 4.3.0, `@inquirer/password` 5.3.0, `@inquirer/prompts` 8.8.0, `@inquirer/rawlist` 5.4.0, `@inquirer/search` 4.4.0, `@inquirer/select` 5.3.0, `@inquirer/type` 4.3.0, `@types/estree` 1.0.10, `baseline-browser-mapping` 2.11.38, `brace-expansion` 5.0.13, `caniuse-lite` 1.0.30001826, `electron-to-chromium` 1.5.491, `js-tokens` 10.0.0, `node-releases` 2.0.65, `rolldown` 1.3.3, `tinyexec` 1.3.1, `unbash` 6.0.4, `vite` 8.3.8.

## Trials: questions settled by a run, not an argument

(none yet)

## What to distrust

- Mutation reports one mutant for `src/leaf/status.ts`: Stryker reads no tsconfig (the starter's setting), and the file is four lines. The score says little until there is more code.
- `docs/AGENT.md`'s Fast loop and Gate cells are Ghost-Core's numbers until Tune-up pass 0 re-measures them here.
- `test/test_landing.py` adds about four seconds to the fast loop, which the core measured at 26.76 s against a ceiling of 30: the next pass may find the armed metric past it, here and in the core.

## Advisories under the gate's threshold

Moderate, let through by `npm audit --audit-level=high` (2026-11-26, J-003); both are in the development tools only:

- `minimatch`: https://github.com/advisories/GHSA-g3hv-75wg-m249
- `qs`, by way of `typed-rest-client`: https://github.com/advisories/GHSA-q8mj-m7cp-5q26, https://github.com/advisories/GHSA-x5fp-wj9c-mxmx, https://github.com/advisories/GHSA-4mjr-xmp4-gh2g, https://github.com/advisories/GHSA-6pq8-jhm2-2vcw
