# Roadmap: the plan, not the decision log

A plan, in phases. Each phase's steps are items with a check that fails before the work and passes
after; each phase ends with a numbered tune-up pass (C-024). When a phase is built, its section
shrinks to a ten-line header and the decisions it produced live in `theGhost.md`. `TODO.md` is this
plan as a chain: the open items, in order, with the checks copied; `docs/DONE.md` is what is
finished.

## 1. The product in three sentences

Psiberline turns a solar software requirement into controlled English a parser accepts, a typed and checked
tree of what it means, and a test composed from verified fixtures, each step traced back to the passage the
requirement came from. The thesis to hold: a requirement that has passed the proofreader and been approved can be
compiled, by a chain with no model in it, into the same bytes every time. The thesis to refuse: that a model, or a
rule set, can be trusted to say what a vague ticket meant; what the rules cannot rewrite a person rewrites, and the
chain waits.

`VISION.md` is the long form: the purpose, the six phases of the pipeline, the catalogue, the language, the
verification ladder and the data boundary. This file is the plan that builds it.

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
- **P-11 The agent's environment is a first-class deliverable**, funded at one commit in eight (C-022, C-024).
- **P-12 Cloud-primary.** Nothing requires the maintainer's own machine (AGT-01).
- **P-13 CI minutes are spent by hand** (C-032).
- **P-14 Core checks run with nothing installed.** Python 3 standard library, `-I` (C-022).
- **P-15 No model in the chain.** Every stage is a rule set, a parser, a checker or a composer; the chain runs to
  its end with no model available (`VISION.md` section 10; `docs/modules.json`, MOD-03).
- **P-16 The same input gives the same bytes.** Every stage's output is held by a golden compared byte for byte
  (C-045), and a stage that cannot repeat itself is not a stage.
- **P-17 Each phase pays for itself.** A phase is worth running if the phases after it never arrive
  (`VISION.md` section 2).
- **P-18 The typed tree is the contract** between reading a requirement and everything made from it.
- **P-19 Compose from verified parts.** The compiler selects and configures a fixture that is already verified; it
  writes no new code.
- **P-20 Fail visibly.** A sentence no rule matches, a word the ontology lacks, a unit that does not resolve: each
  stops the chain with the rule it broke, and none is passed on.
- **P-21 Check on the lowest rung that can.** A type check before a solver, a solver before a property test, a
  proof last (`VISION.md` section 9).
- **P-22 Nothing an employer or a customer gave enters this repository** (C-033): the corpus here is synthetic.
- **P-23 No abstraction before its second use** (C-002): one domain and one target until a second exists.

## 3. Settled facts

| Id | Fact | Source | Implication |
| --- | --- | --- | --- |
| F-01 | The controlled English is EARS (Easy Approach to Requirements Syntax). | Ghost, 2026-11-26 (`VISION.md` section 16) | The grammar is EARS's five sentence patterns; the ontology and the typed tree give them meaning. |
| F-02 | The synthetic corpus is drawn from Solarpunk, a solar project Ghost owns. | Ghost, 2026-11-26 | Phase 1 writes its requirements from that project's own, and no other source enters. |
| F-03 | The catalogue is JSON files under version control. | Ghost, 2026-11-26 | No database and no host; a record's history is the repository's. |
| F-04 | The stack is TypeScript, with four development dependencies and none at run time. | Ghost, 2026-11-26; P-002 | A new dependency is a decision of Ghost's (C-034). |
| F-05 | The chain holds no model. | Ghost, 2026-11-26 (`VISION.md` section 10) | P-15; `docs/modules.json` forbids a model client's import. |
| F-06 | A clause that says what code guarantees stays in a comment; a reason is a decision. | Ghost, 2026-11-26; Core C-042 | `scripts/checks/comments.py` holds the code here. |
| F-07 | The tool that marks English that is not EARS is the proofreader. | The glossary keeps another word for a stack's tool (J-001's stamp) | One word, in the glossary, from the first file. |
| F-08 | The first adopter has Claude Code, and no real requirement or code of theirs is available here. | Ghost, 2026-11-26 | Everything in this repository is built and proven on the synthetic corpus; real requirements are met only after the chain is carried over (Phase 6). |
| F-09 | The first slice is "read 50 panels of type A", then "read 10 more of type B". | `VISION.md` section 16 | Phase 1's items. |

## 4. What is deliberately not built

- **A general requirements compiler.** One domain, solar, until the chain works end to end (P-23).
- **A stage that is a model.** A model may suggest a rewrite to a person; the proofreader judges the result.
- **A rule set that claims to convert all English.** What no rule matches is flagged and left as written.
- **Product code written by the compiler.** A new fixture is ordinary development, verified before it can be selected.
- **Product fixtures before the application's developers agree.** Test fixtures come first; they change nothing in
  the application under test.
- **A database, a server or a hosted service.** Files, a command and a gate.
- **An editor plug-in.** The proofreader is a command first; an editor's view of it waits on Phase 4's proof that the
  command is right.
- **A connector to a ticket tracker in this repository.** Real tickets are read only in the adopter's environment.
- **Machine-checked proof before the lower rungs.** Lean is Phase 8, for the calculations only.

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
renamed and numbered (0.4), the corpus's manifest (1.1), the ontology (1.3), the grammar (1.4) and the rule set (1.6).

## 6. Phases

Each phase ends with a tune-up pass. Phases 1 to 4 are numbered; Phases 5 to 8 are numbered when the phase before
them is built, since what they need is learned there.

### Phase 0: founding

- 0.1 this project's ghost, named (a `--docs-only` commit: the gate refuses at the stack until 0.2)
- 0.2 the stack wired, so the gate can pass and the first gated commit lands
- 0.3 the roadmap and TODO filled: §1 to §6 and Phase 1's items
- 0.4 the contract and the leaf module
- 0.5 the founding decisions, Ghost's (agents cannot author Ghost's decisions; a builder that reports "waiting on Ghost" has done its job)
- 0.6 Tune-up pass 0

### Phase 1: the first slice, one requirement through the whole chain

"Read 50 panels of type A" from a written requirement to a generated test, in miniature; then "read 10 more of
type B" to prove a fixture is reused. Every stage exists, each as small as the slice allows.

- 1.1 The corpus: a handful of synthetic requirements written from Solarpunk's own, each a source artifact with an
  id, listed in a manifest a test holds to the folder; nothing from an employer (P-22).
- 1.2 The catalogue's records in the leaf: requirement, acceptance criterion, criterion link, source artifact,
  decision, constraint, dependency, evidence, revision; a status and a supersedes on a requirement; the
  provenance on every record. JSON files, read and checked, with a planted break for each rule.
- 1.3 The ontology, four assets and one measurement: plant, site, pad, panel and how they contain one another;
  voltage with its unit and range; the operation read. A file a check holds: every word a requirement may use.
- 1.4 The grammar: EARS's patterns as numbered invariants of the contract; a tokenizer and a parser for the two the
  slice needs (the plain "the system shall" and the event-driven "when"), giving a typed tree; a golden per
  sentence.
- 1.5 The proofreader, as a command: a sentence that is not EARS, a word the ontology lacks, a unit that does not
  resolve, each named with the rule it broke, the file and the line; exit 1 on any; goldens for its output.
- 1.6 The first rewrite rule: one pattern of plain English rewritten to EARS, the rule's id recorded on the result;
  a sentence no rule matches left as written and flagged. The conversion rate printed for the corpus.
- 1.7 The checks on the tree: unit compatibility, asset identity and range, each a finding before any output (P-20).
- 1.8 The first test fixture and the first generated test: an acceptance criterion compiled to a test against a
  stand-in application kept under `test/`, composed from one verified fixture with its inputs addressed (50 of
  type A); the output a golden, byte for byte.
- 1.9 Reuse: the second requirement compiles with the same fixture and 10 of type B, and nothing else is written.
  The coverage rate printed.
- 1.10 The trace: from a generated test to its criterion, its requirement, its source passage and each rule that
  touched it, as a command and a golden.
- 1.11 Tune-up pass 1

### Phase 2: triage

The front of the chain as a person uses it: a batch of tickets in, records and flags out (`VISION.md` section 4,
phase 0).

- 2.1 The ticket as a source artifact: the fields a ticket has (title, body, kind, links), read from a file; the
  corpus grows to tickets of every class in section 7 of the vision.
- 2.2 Classification by rule: the nine classes and the compiler's response to each; a ticket no rule classifies
  goes to a person, counted.
- 2.3 Requirements and acceptance criteria split out of a ticket into separate records, linked many to many.
- 2.4 Duplicates and near-duplicates named: two tickets that give the same typed tree.
- 2.5 The triage report: per ticket, its class, its records, its flags and what a person must rewrite; a golden.
- 2.6 The measures: conversion rate, flags per ticket, person-rewrites per ticket, written by a run a test repeats.
- 2.7 Tune-up pass 2

### Phase 3: the catalogue over time

- 3.1 Supersession: a requirement that replaces another names it; a superseded requirement compiles to nothing
  and says what replaced it.
- 3.2 Revisions: every change to a record is a later revision; the catalogue at any commit can be rebuilt.
- 3.3 Dependencies between requirements, and the order they compile in.
- 3.4 Contradiction: two accepted requirements whose trees cannot both hold are a finding that stops both.
- 3.5 Evidence: a test result, a measurement or an approval attached to the record it supports.
- 3.6 The link to code: a change that closes a ticket names it; where none does, the gap is listed.
- 3.7 A query command: what requires this asset, what a requirement depends on, what a test proves.
- 3.8 Tune-up pass 3

### Phase 4: the language grows

- 4.1 The remaining EARS patterns: state-driven, unwanted behaviour, optional feature, and their combinations.
- 4.2 The ontology's second ring: inverter, tracker, string; current, power, energy, irradiance; units and
  conversions between them.
- 4.3 Operations with meaning: what reading a measurement is; what calculating performance is, as a definition a
  check can apply.
- 4.4 Symbol tables: a word resolved against the assets it may belong to, and a reference that resolves to none
  flagged.
- 4.5 Constraints as their own records: access control, measurement range, asset identity, each checked on the
  tree.
- 4.6 The rule set grown from the corpus: each rule a pattern, a rewrite, a version and its tests; a rule's change
  shown by the goldens it moves.
- 4.7 The proofreader's messages reviewed against a person's rewrites: what a person needed to be told.
- 4.8 Tune-up pass 4

### Phases 5 to 8 (outline; items are numbered when the phase before is built)

- **Phase 5, generated tests at scale and the ladder's middle rungs.** A library of test fixtures; acceptance
  criteria of every class compiled; property tests over generated inputs; conditions of the form "A equals B when
  C" checked by a solver, which is a dependency for Ghost to approve; coverage reported by requirement.
- **Phase 6, the chain carried to its adopter.** What leaves this repository and what never does; the adopter's
  first run on real requirements as a test of the design; ticket cycle time and person time measured there; who
  owns what, settled before it (waits on Ghost).
- **Phase 7, product fixtures and the host.** A host that gives fixtures their common services, each built when a
  fixture first needs it; adapters for equipment; contracts between fixtures checked when they are composed. It
  waits on the application's developers.
- **Phase 8, proof for the calculations.** The performance mathematics stated and proven in Lean, the proof
  checked by the gate.
