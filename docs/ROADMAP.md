# Roadmap: the plan, not the decision log

A plan, in phases. Each phase's steps are items with a check that fails before the work and passes
after; each phase ends with a numbered tune-up pass (C-024). When a phase is built, its section
shrinks to a ten-line header and the decisions it produced live in `theGhost.md`. `TODO.md` is this
plan as a chain: the open items, in order, with the checks copied; `docs/DONE.md` is what is
finished.

## 1. The product in three sentences

Psiberline compiles an accepted solar software requirement, handed over as a typed and approved tree, into a test
plan composed from verified fixtures, each step traced back to the requirement. The thesis to hold: a requirement of
a kind that has been tested before can be compiled, by a chain with no model in it, into the same bytes every time,
with nothing written new. The thesis to refuse: that the compiler may guess; where no fixture exists it says so, and
where the tree does not supply an input it stops.

`VISION.md` is the long form: where Psiberline sits beside the language project, the compiler's seven stages, the
fixtures and the host, the verification ladder and the data boundary. This file is the plan that builds it.

## 2. Principles

The core's principles, copied from Ghost-Core when this project was stamped; this project's own follow them.

- **P-01 The check before the thing it checks.** Every document arrives with its check and the
  check's planted break, in the same commit (C-003, C-013).
- **P-02 A refactor changes no result.** Every test green before and after, every generated file
  identical (C-017).
- **P-03 Findings before claims.** What a check proves about a parent or a practice is a row in
  `docs/FINDINGS.md` before it is a sentence anywhere else (C-014).
- **P-04 One shape until proven.** One check framework, one test runner, one fast loop; a second
  arrives when the first has failed a stated test (C-002).
- **P-05 Numbered decisions, test-checked supersession** (C-008).
- **P-06 Plans shrink into decisions.** A built phase becomes a ten-line header.
- **P-07 The routing table is the front door** (C-020, C-021).
- **P-08 One canonical word per concept, from the first file** (C-011).
- **P-09 Ratchets only where there is debt** (C-023).
- **P-10 Proven by a run, not on paper.** "Done" never means "on paper" (C-004).
- **P-11 The agent's environment is a first-class deliverable**, funded at one commit in twenty-five and a pass at every phase's end (C-022, C-024, C-048).
- **P-12 Cloud-primary.** Nothing requires the maintainer's own machine (AGT-01).
- **P-13 CI minutes are spent by hand** (C-032).
- **P-14 Core checks run with nothing installed.** Python 3 standard library, `-I` (C-022).
- **P-15 No model in the chain.** Every stage is a rule set, a checker or a composer; the compiler runs to its end
  with no model available (`VISION.md` section 9; `docs/modules.json`, MOD-03; P-008).
- **P-16 The same input gives the same bytes.** Every stage's output is held by a golden compared byte for byte
  (C-045), and a stage that cannot repeat itself is not a stage.
- **P-17 Compose from verified parts.** The compiler selects and configures a fixture that is already verified; it
  writes no new code (P-009).
- **P-18 The typed tree is the contract** between the language project and this one, in a format with a version
  (P-021).
- **P-19 Never trust the input.** A tree is checked for its format, its status, its approval and its words before
  anything is made from it.
- **P-20 A gap is a result.** "No fixture exists" and "the tree does not supply this input" are named and listed,
  never hidden and never filled in.
- **P-21 Check on the lowest rung that can.** A check on the tree before a fixture's own tests, those before a
  solver, a solver before a property test, a generated plan last (`VISION.md` section 8; no machine-checked proof,
  P-020).
- **P-22 Nothing an employer or a customer gave enters this repository** (C-033): the trees here are synthetic.
- **P-23 No abstraction before its second use** (C-002): one domain and one target until a second exists.

## 3. Settled facts

| Id | Fact | Source | Implication |
| --- | --- | --- | --- |
| F-01 | Psiberline is the compiler; the language is a second project in its own repository. | Ghost, 2026-11-26; P-021 | Nothing here parses, proofreads, rewrites or triages English. |
| F-02 | The handover is JSON files in a format with a version. | P-021; `VISION.md` section 4 | Neither project imports the other; the format is written down and checked at intake. |
| F-03 | A generated test is a plan in JSON, run by one TypeScript runner. | Ghost, 2026-11-26; P-011 | The plan is the golden; a runner for an adopter's framework comes later. |
| F-04 | The stack is TypeScript, with four development dependencies and none at run time. | Ghost, 2026-11-26; P-002 | A new dependency is a decision of Ghost's (C-034). |
| F-05 | The chain holds no model. | Ghost, 2026-11-26; P-008 | P-15; `docs/modules.json` forbids a model client's import. |
| F-06 | No machine-checked proof. | Ghost, 2026-11-26; P-020 | The ladder ends at a generated plan. |
| F-07 | A clause that says what code guarantees stays in a comment; a reason is a decision. | Ghost, 2026-11-26; Core C-042 | `scripts/checks/comments.py` holds the code here. |
| F-08 | The language project, Psiberline Language, is founded and has built nothing yet; no real requirement is available here. | Ghost, 2026-11-26; J-014 | The first trees are written by hand; the format is held here until Ghost says where it lives (`docs/HANDOFF.md`; Phase 4). |
| F-09 | The first slice is "read 50 panels of type A", then "read 10 more of type B". | `VISION.md` section 15 | Phase 1's items. |

## 4. What is deliberately not built

- **Anything that reads English.** No parser, proofreader, rewrite rule or triage: the language project's.
- **A stage that is a model.**
- **Code written by the compiler.** A new fixture is ordinary development, verified before it can be selected.
- **A guess where a fixture is missing or an input is absent.** The gap is reported.
- **Product fixtures before the application's developers agree.** Test fixtures come first; they change nothing
  in the application under test.
- **A database, a server or a hosted service.** Files, a command and a gate.
- **A runner for a particular test framework** before an adopter's framework is known.
- **Machine-checked proof.** No Lean, and no other proof assistant (P-020).
- **A general compiler.** One domain, solar, until the chain works end to end (P-23).

## 5. The meta-architecture

The core's table, copied from Ghost-Core when this project was stamped; this project's rows follow it.

| Document | What it holds | Test |
| --- | --- | --- |
| `CLAUDE.md` | the routing table, the when list, the binding rules | `test/test_claude_md.py` (words, rows, pointers) |
| `theGhost.md` | the decisions | `test/test_ghost.py` |
| `docs/GLOSSARY.md` | the words | `test/test_glossary.py` |
| `docs/journal/` | what happened | `test/test_journal.py` |
| `TODO.md`, `docs/DONE.md`, this file | the plan as a chain | `test/test_todo.py` |
| `docs/HANDOFF.md` | what waits on whom | `test/test_journal.py` (open conflicts), `test/test_registers.py` (raised escalations) |
| `docs/FINDINGS.md`, `docs/ESCALATIONS.md` | the registers | `test/test_registers.py` |
| `docs/NAVIGATION-LOG.md` | the debriefs and the last review | `test/test_navigation.py` |
| `docs/AGENT.md` | the environment contract and the metrics | `test/test_metrics.py` |
| `docs/CONTRACT.md`, `docs/modules.json` | the kernel contract and the import graph | `test/test_contract.py`, `test/test_modules.py` |
| `docs/when/*.md`, `docs/paths/*.md` | what to do in a situation; a workpath's rows | `test/test_pointers.py` |
| `docs/SUPPLY-CHAIN.md` | the baseline and where this repository stands | `test/test_supply_chain.py` |
| `VISION.md` | the product's long form, approved by Ghost | none: a statement of intent, read by this file and the philosophy page |
| `docs/REVIEWED-VERSIONS.md` | every pinned version and how it came in | `test/test_reviewed_versions.py` |
| the code's comments | what the code does, a decision by id for the reason | `test/test_comments.py` |


The product's own documents arrive with their phase, each with its check in the same commit (P-01): the contract
renamed and numbered (0.4), the tree's format (1.1), the trees' manifest (1.2) and the fixture library's index (2.1).

## 6. Phases

Each phase ends with a tune-up pass. Phases 1 to 3 are numbered; Phases 4 to 6 are numbered when the phase before
them is built, since what they need is learned there.

### Phase 0: founding

- 0.1 this project's ghost, named (a `--docs-only` commit: the gate refuses at the stack until 0.2)
- 0.2 the stack wired, so the gate can pass and the first gated commit lands
- 0.3 the roadmap and TODO filled: §1 to §6 and Phase 1's items
- 0.4 the contract and the leaf module
- 0.5 the founding decisions, Ghost's (agents cannot author Ghost's decisions; a builder that reports "waiting on Ghost" has done its job)
- 0.6 Tune-up pass 0

### Phase 1: the first slice, one accepted tree to a passing plan

"Read 50 panels of type A" from a hand-written accepted tree to a test plan run green, in miniature; then "read 10
more of type B" to prove a fixture is reused. Every stage of `VISION.md` section 5 exists, each as small as the slice
allows.

- 1.1 The tree's format, version 0: what a handed-over requirement holds (its status, its approver, its
  provenance, its acceptance criteria, its typed tree of actor, event, operation, quantity with unit, and
  constraint, and the ontology's version), as a document and as types in the leaf, with a planted break for each
  rule. Held here until the language project exists (F-08).
- 1.2 Two synthetic trees, written by hand, with a manifest a test holds to the folder: type A, 50 panels; type B,
  10 more. Nothing from an employer (P-22).
- 1.3 Intake: a tree is read and refused, with the requirement and the rule, when its format's version is not the
  one accepted, its status is not accepted, it has no approver, or it uses a word or a unit the named ontology
  version does not hold.
- 1.4 The stand-in application, under `test/`: a small simulated plant that answers how many panels of a type it
  has, so a plan has something to run against.
- 1.5 The first test fixture: it reads a count of panels of a type and asserts it; verified by its own tests and by
  mutation before the compiler may select it.
- 1.6 Classification by rule: the nine classes of `VISION.md` section 6, with the two trees classified and a tree
  no rule classifies reported for a person.
- 1.7 Capability resolution and composition: each acceptance criterion matched to a fixture and the fixture's
  inputs addressed from the tree; a criterion no fixture can prove is a named gap, and an input the tree does not
  supply stops the compile.
- 1.8 The plan: the compile's output as a test plan in JSON (the fixture, its inputs, what is asserted, the
  trace), a golden byte for byte; the same tree compiled twice gives the same bytes.
- 1.9 The runner: one TypeScript runner executes a plan green against the stand-in, and a plan whose assertion
  fails names the assertion.
- 1.10 Reuse: the second tree compiles with the same fixture and nothing written new. The coverage rate printed.
- 1.11 The trace: from a plan to its criterion, its requirement, its source passage and its approver, as a command
  and a golden.
- 1.12 Tune-up pass 1

### Phase 2: the fixture library

The second and third kinds of fixture, and what it takes to keep many of them honest.

- 2.1 The library's index: every fixture with the canonical requirement it satisfies, its inputs and their types,
  and the tests that verify it; a fixture not in the index cannot be selected.
- 2.2 A measurement fixture: reads a quantity with its unit and asserts it within a range; a unit the fixture does
  not take is refused at composition.
- 2.3 An event fixture: for the event-driven shape ("when a trigger, the system shall respond"), asserts the
  response after the trigger.
- 2.4 A threshold fixture: for an unwanted condition, asserts the alarm or the refusal.
- 2.5 Contracts between fixtures: two fixtures composed into one plan declare what each needs and leaves, and a
  pair that cannot hold together is refused when composed.
- 2.6 The gap report: every criterion no fixture could prove, by kind, as the library's backlog; a golden.
- 2.7 A fixture's version: a plan names the version of each fixture it uses, and a changed fixture shows which
  plans' goldens move.
- 2.8 Tune-up pass 2

### Phase 3: the ladder's middle rungs, and many trees

- 3.1 Property tests for a fixture over generated inputs, with the generator's seed in the plan's trace.
- 3.2 Conditions of the form "A equals B when C" checked by a solver, which is a dependency for Ghost to approve
  (C-034).
- 3.3 A batch compile: a folder of trees in, plans, gaps and refusals out, with a summary; a golden.
- 3.4 Constraint change: when a tree changes, the plans that depend on it are named and recompiled, and no other.
- 3.5 The measures of `VISION.md` section 11, written by a run a test repeats.
- 3.6 Tune-up pass 3

### Phases 4 to 6 (outline; items are numbered when the phase before is built)

- **Phase 4, the format shared with the language project.** The format's document moves to the language project,
  and Psiberline pins a version of it; intake runs on trees that project emits from its synthetic corpus; a check
  that the two repositories hold the same version; how a new version is taken up.
- **Phase 5, the chain carried to its adopter.** A runner for the adopter's test framework; fixtures for a real
  application, written in that application's environment; the first compile of real accepted requirements as a
  test of the design; time from an accepted requirement to a passing plan, and coverage, measured there; who owns
  what, settled before it (waits on Ghost).
- **Phase 6, product fixtures and the host.** A host that gives fixtures their common services, each built when a
  fixture first needs it; adapters for equipment; application modules composed as plans are. It waits on the
  application's developers.
