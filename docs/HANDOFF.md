# Handoff: what to work on next, and what is waiting on whom

Read `CLAUDE.md` first, then this. `TODO.md` is the chain in order; `docs/DONE.md` is what is finished.

## Where the project stands (2026-11-26)

Stamped from Ghost-Core today. Nothing of Psiberline's own is built; the template's documents, checks and
gates are in place and green.

## For Ghost: waiting on you

1. Confirm the wording of this project's ghost (`docs/GHOST-IN-THE-KERNEL.md`, J-002): drafted from `VISION.md`.
2. Confirm P-002's versions (vitest 4.1.12, typescript 7.0.2, knip 6.46.1, @stryker-mutator/core 10.1.1), the agent's choice (J-003).
3. Write the first invariants of the contract and set `docs/modules.json` (TODO 0.4).
4. Write the founding decisions in `theGhost.md`, a decision for each core decision this project refuses among them (TODO 0.5): agents cannot author them.
5. `VISION.md` section 8 calls the program a product fixture is written against the kernel; here the kernel is the codebase (`docs/GLOSSARY.md`), so the roadmap and the glossary call it the host. Say whether the vision takes the word.
6. Who owns the chain after it is carried into the adopting organisation (`VISION.md` section 16).

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

## Advisories under the gate's threshold

Moderate, let through by `npm audit --audit-level=high` (2026-11-26, J-003); both are in the development tools only:

- `minimatch`: https://github.com/advisories/GHSA-g3hv-75wg-m249
- `qs`, by way of `typed-rest-client`: https://github.com/advisories/GHSA-q8mj-m7cp-5q26, https://github.com/advisories/GHSA-x5fp-wj9c-mxmx, https://github.com/advisories/GHSA-4mjr-xmp4-gh2g, https://github.com/advisories/GHSA-6pq8-jhm2-2vcw
