# Lineage: the four projects Ghost-Core is distilled from

Ghost-Core is the fifth project built the Ghost in the Kernel way and the first that is only the
way itself: the process, the documents, the checks and the gates that the four before it
converged on, with nothing product-specific left in. A decision here that came from a parent names
the parent's id in its Source line; the reasoning is pointed at, not copied, so a reader who wants
the evidence goes to the project that paid for it.

| Project | Repository | Language | Decision prefix | Decisions at survey | First commit | What it is |
| --- | --- | --- | --- | --- | --- | --- |
| Suite Builder | Ghost-in-the-Kernel-Labs/suite-builder | TypeScript | G- | 292 | 2026-09 | Crawls a site and writes a Playwright, Selenium or Cypress test suite for it; built as a compiler |
| Katana | ghost-in-the-kernel/katana | Java 21 | R- | 89 | 2026-10-04 | COBOL-to-Java migration compiler proven byte-identical by an oracle; Intent IR and proof ledger |
| Employee Evaluator | Ghost-in-the-Kernel-Labs/Employee-Evaluator | Java 21 (+ Python sandbox) | E- | 75 | 2026-10 | Ranks developers by the AI-assisted repository they built; seven metrics, every score traced to facts |
| Neon Rain | ghost-in-the-kernel/Neon-Rain | Python 3.12 | R- (shared letter with Katana) | 23 | 2026-10-22 | Market-prediction research held to a backtesting harness frozen before the first model |
| Cyberline | https://github.com/Ghost-in-the-Kernel-Labs/cyberline | TypeScript | P- | 1 | 2026-11-26 | A compiler that turns accepted solar software requirements, handed over as typed and approved trees, into test plans, and later application modules, composed from verified fixtures, with no AI in the chain; taken up to Ghost-Core 56cb5ed |
| Ghost-Core | Ghost-in-the-Kernel-Labs/Ghost-Core | Python 3 stdlib (checks); any stack (projects) | C- | — | 2026-10-23 | This template |

Surveyed read-only on 2026-10-23 at the commits then on `main` (SB fd349c7, EE 72268bc, Katana
8733f28, NR 4160b6c). The survey and its findings are `docs/LESSONS.md`.

## Prefixes

Each project's decisions carry one letter so a citation anywhere in the Labs says which log it
means. Katana and Neon Rain both took R-; a future project takes a letter no row above uses, and
adds its row here. A Ghost-Core decision cited from a project is written `Core C-012`.

## What each parent contributed

**Suite Builder** (the origin): the pointer CLAUDE.md and the behaviours index ("when this
happens, look up that"); task files with a `Caught by:` line per step; goldens compared byte for
byte and rewritten only behind a flag; mutation testing and the rule that a test is never weakened
to pass; ratchets, not exceptions; the kernel log format; the trim, traversability and hostile
review formats; the weakened-test detector; the security posture and the manifest lock of
auto-execution surfaces; pre-registered experiments; the naming rules (a thing is named for what
it holds; the glossary word, never an alias); the observation that treating the agent's
environment as work worth about a tenth of effort raised delivery speed, which every later project
formalised.

**Katana**: workpaths and `docs/when/`; the journal split into files of a hundred entries behind a
generated index; registers with fixed fields and never-reused ids (findings, discoveries,
divergences); the check doctrine (every check declares its oracle, its killer mutation and what its
verdict gates; a test task that runs zero tests is red); claims tagged verified or hypothesis, and
trials over arguments ("two models arguing converge on the plausible, not the true"); the tithe
and navigation gates (whose lesson, that a warning stops nothing, Ghost-Core turns into a commit
gate); `nextId` after a fetch; the pinned offline image; the four question classes (the agent's,
a trial's, Fable's, Ghost's); the Intent IR vocabulary (fact, rule, review file, key).

**Employee Evaluator**: the doc-test pattern that both holds the repository and rejects a planted
break, so a check that stops catching anything is caught itself; FOR-GHOST.md as the human-only
queue; the decision lineage table; the finding that binding rules must be inline because "a
pointer depends on being followed; text read on entry does not"; the armed metric; Haiku run three
times and averaged as the cheap judge; the escalation gap kinds and "three of a kind goes to
Ghost".

**Neon Rain**: the "When X happens, read Y" wording and `docs/rules/` files that open "Read this
when…" and close "Why: J-nnn"; the tithe procedure with its may-change / may-not-change lists and
"a tithe that builds has overshot"; the escalation rule made checkable ("still red after one
attempt and the output does not say why"); the navigation log header and the Opened-list measure
of navigability; "the tests are the audit", the readability rules for a language the maintainer
cannot read by eye; the golden index with hashes and `changed_by`; the trials file; the sharpest
statement of the philosophy for agents ("On enlightenment"); no CI at all when a workflow would be
a check that cannot fail.

## What Ghost-Core adds that no parent had

Decided by Ghost on 2026-10-23, during the survey, from what the four had each half-learned:

- The **tune-up**: the tithe and the navigation review as one move on one counter, a numbered
  roadmap item closing every phase, held by a gate at the commit (a `tune-up:` commit is always
  accepted; any other commit is refused while one is due), with the tightest definition in the
  repository.
- **Cloud-primary** as a contract line: nothing in a project may require the maintainer's own
  hardware.
- **CI minutes are scarce**: the local gate is the definition of done; a workflow is fired by
  hand, by decision, with a journal line saying why the minutes were spent.
- The **core checks in one language for every stack** (Python 3 standard library, under Neon
  Rain's readability rules and mutation-tested), so a docs-only session on a Java or TypeScript
  project still runs them with nothing installed.
- One **kernel-contract template**: a document of numbered invariants, the leaf module that holds
  its types and numbers, and `modules.json` entry points as the only names another module may
  call.
