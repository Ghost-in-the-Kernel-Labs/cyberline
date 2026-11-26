# Psiberline: Vision and Product Thesis

**Status:** Revised vision (draft for Ghost's approval); aspirational, not a statement of implemented capability
**Supersedes:** the founding vision of 2026-11-25
**Implementation language:** TypeScript
**Repository:** https://github.com/Ghost-in-the-Kernel-Labs/psiberline

---

## 1. What changed from the founding vision

The founding vision described a general compiler from any requirements corpus to any software target. This revision narrows it on purpose.

- **One domain.** Psiberline targets utility-scale solar software. Other domains are a non-goal until the solar pipeline works end to end.
- **One entry point.** Requirements arrive through quality-assurance (QA) ticket triage, not as a finished corpus.
- **Tests before product code.** The first thing compiled is a test for an existing application. Compiling the application itself comes last.
- **Composition, not free generation.** Output is assembled from fixtures that have already been verified. A model does not write new product code inside the compiler.
- **A verification ladder.** Formal proof is the top rung, used where the cheaper rungs cannot reach.
- **No AI in the chain.** The goal is a fully deterministic chain of work, from a requirements document to its output. A model may help build the chain; it is not a stage in it.

## 2. Purpose

The immediate purpose is to raise the rate at which QA tickets are closed, without lowering what "closed" means.

The long-term purpose is unchanged: treat a well-specified body of requirements as a source language, and compile it into software whose behaviour is supported by evidence.

> Every ticket that passes through triage should leave behind a formal, reviewed statement of what the system must do. Enough of those statements make a language. A language can be compiled.

Each phase below has to be worth running if the phases after it never arrive.

## 3. What Psiberline is and is not

Psiberline is a pipeline that turns solar requirements into a typed, checked representation, and then into tests and, later, application modules.

It is not:

- A prompt that reads a ticket and writes an application in one leap, or a pipeline with a model as one of its stages.
- A general-purpose requirements compiler.
- A replacement for human review of what a requirement means.
- A way to restructure an existing product without its developers' agreement.

## 4. The pipeline

| Phase | What happens | What it delivers by itself |
| --- | --- | --- |
| 0. Triage | A rule set classifies each ticket (section 7) and rewrites the sentences it recognises into controlled English. A proofreader flags every sentence that does not conform, and says why. A person rewrites the flagged sentences until none remain. | Faster, more consistent triage; requirements that are clear before development |
| 1. Catalogue | Reviewed records are stored with their source, status and history, and linked to the code change that closed the ticket. | A searchable requirements history |
| 2. Ontology | The nouns, measurements and operations of conforming requirements enter the domain ontology. A word the ontology does not know is a proofreader flag. | A shared, checked vocabulary |
| 3. Parser and checks | Controlled English is parsed into a typed syntax tree and checked for units, asset identity, ranges and contradiction. | Inconsistent requirements caught mechanically |
| 4. Generated tests | Acceptance criteria compile into tests that run against the existing application. | Falling QA effort per ticket |
| 5. Fixtures and kernel | Application modules are composed from verified fixtures on a common kernel. | The compiler in full |

Each phase has explicit inputs, outputs and failure states. Any phase may stop with a precise question instead of an answer.

## 5. The catalogue

Requirements and acceptance criteria are separate entities. One requirement may have many acceptance criteria, and one criterion may give evidence for many requirements.

| Entity | Purpose |
| --- | --- |
| Requirement | Canonical statement of system intent |
| Acceptance criterion | Observable condition for acceptance |
| Criterion link | Joins a criterion to a requirement, and says what it evidences |
| Source artifact | The original ticket, document or specification |
| Decision | A human-approved interpretation or design decision |
| Constraint | A mandatory limit on implementation |
| Dependency | A relationship between requirements |
| Evidence | A test result, measurement, document or approval |
| Revision | A historical version of any entity |

Every requirement carries a status (proposed, accepted, superseded, withdrawn) and may name the requirement it supersedes. Old tickets contradict new ones; without supersession, history would block compilation.

Every record keeps its provenance: which source passage it came from, which rule or person produced it, and who approved it.

The catalogue is stored as JSON files under version control, so its history is the repository's history and nothing needs hosting.

## 6. The language

### 6.1 Surface: controlled English

Requirements are written in EARS (Easy Approach to Requirements Syntax), a small set of sentence templates such as "When *trigger*, the *system* shall *response*." EARS fixes the shape of a sentence. It does not fix the meaning; the ontology and the typed tree do that.

### 6.2 Ontology and symbol tables

The ontology defines what the words mean in this domain.

- **Assets:** solar plant, site, pad, panel, inverter, tracker, and how they contain one another. For example: every panel has a pad, every pad has a site and a voltage, every site has a parent plant.
- **Measurements:** voltage, current, energy, each with units and valid ranges.
- **Operations:** what reading a measurement means, what calculating performance means.
- **Constraints:** unit compatibility, asset identity, measurement range, access control.

Symbol tables hold these relationships so the parser can resolve a word against them.

### 6.3 Typed syntax tree

A parsed requirement becomes a typed tree of actors, events, conditions, states, operations and constraints. The tree is the intermediate representation: independent of the ticket's wording and of any target language.

### 6.4 The rule set and the proofreader

Two deterministic tools stand at the front of the chain.

- **The rule set** takes a requirements document and rewrites the sentences it recognises into EARS. Each rule is a pattern and a rewrite, versioned and tested, and each rewrite records the rule that made it. A sentence no rule matches is left unchanged and flagged.
- **The proofreader** works like a spelling checker for requirements. It marks any sentence that does not meet EARS, any word the ontology does not know, and any unit or reference that does not resolve, and it says which rule was broken.

No rule set can turn all free English into EARS, because much of what a ticket leaves out is not on the page to be rewritten. The chain does not depend on that. What the rules cannot convert, a person rewrites with the proofreader's guidance, and nothing moves downstream until the proofreader passes. The rule set grows from the sentences people had to rewrite by hand.

The same input, rule version and ontology version always give the same output.

### 6.5 Order of construction

Ontology first, then the proofreader, then the rewrite rules, then tokenizer and parser, then semantic analysis. The grammar is built from reviewed requirements. Code that passed QA is linked to its requirement as an example of one implementation. It is evidence, not specification, because it may contain defects QA did not find.

## 7. Story classification

| Story classification | Compiler response |
| --- | --- |
| New capability | Select a module, or report that a fixture must be written |
| Existing capability | Reuse an existing module |
| Configuration change | Modify module configuration |
| Domain extension | Extend the ontology |
| Constraint change | Re-evaluate dependent checks and proofs |
| Integration change | Select or modify an adapter |
| Defect correction | Identify the affected capability and its verification obligations |
| Documentation | Update generated documentation |
| Research or investigation | No automatic implementation |

Epics route to a module; stories live within it. Classification is by rule, from the ticket's fields and wording; a ticket no rule classifies goes to a person.

## 8. Fixtures and the kernel

A fixture is a verified unit that satisfies a canonical requirement within a module. Two stories asking to read 50 panels of type A and 10 of type B resolve to two reading fixtures in one module, with addressable inputs for 50 and 10.

**Test side first.** The first fixtures are test fixtures: verified pieces from which acceptance tests are composed. They need no change to the application under test.

**Product side later.** Product fixtures are written against a kernel that provides common services: type and schema enforcement, dependency injection, capability registration, event dispatch, transaction management, error handling, logging and telemetry, authorization, configuration, and version compatibility. A kernel service is built when the first fixture needs it, not before.

**Writing a new fixture is ordinary development.** It is written, reviewed and verified before the compiler may select it. The compiler composes; it does not improvise.

**Composition is checked.** Two verified fixtures can still interact badly. The kernel checks contracts between fixtures at assembly time.

A defect fixed in the compiler, the kernel or a fixture is fixed for every application built from them. A defect in a requirement is not; that is what phases 0 to 3 are for.

## 9. Verification ladder

Each claim is checked on the lowest rung that can establish it.

1. **Type and semantic checks** on the typed tree: units, asset identity, ranges, references.
2. **Constraint solving** for conditions of the form "A equals B when C."
3. **Property-based tests** for behaviour over many generated inputs.
4. **Generated acceptance tests**, traced to their criteria.
5. **Machine-checked proof (Lean)** for the calculation core, such as performance mathematics.

Tests derived from the typed tree show that code matches the interpretation. Only human approval of the tree, or independent evidence such as customer-supplied examples, shows that the interpretation matches the intent.

Generated, compiled, tested, verified and accepted are different words and are not used as synonyms.

## 10. A deterministic chain, and where AI stands

The chain from requirements document to output contains no model. Every stage is a rule set, a parser, a checker or a composer, and every stage gives the same output for the same input, byte for byte.

AI stands outside the chain, in two places.

- **Building it.** A model may help write rewrite rules, ontology entries, fixtures and proofs. What it writes is reviewed, tested and committed like any other code, and from then on it is an ordinary deterministic part.
- **Assisting a person.** A model may suggest how to rewrite a flagged sentence. The person decides, and the proofreader judges the result. Removing the model changes the speed of the work, not its outcome.

The chain must run to completion with no model available.

Tickets and documents are data. Text inside them cannot change Psiberline's rules, permissions or policy.

## 11. The data boundary

This repository holds the engine and synthetic material only.

- Nothing an employer or customer gave enters this repository: no tickets, no requirements, no code, nothing derived from them.
- Development here uses a synthetic solar corpus written for the purpose.
- Work on real requirements happens only inside the adopting organisation's own environment, with that organisation's approved tools.
- The engine is transferred into that environment. Ontology entries, grammar and fixtures learned from real tickets are created there and stay there.

Who owns what after the transfer is an open decision (section 16) and is settled before the transfer.

## 12. Measurement

The one-hour target of the founding vision remains an aspiration, for stories that resolve to existing fixtures. For every run, measure:

- Ticket cycle time, from triage to accepted.
- Human active time and number of interventions.
- **Conversion rate:** the share of sentences the rule set rewrites into EARS without a person.
- **Coverage rate:** the share of stories that resolve to existing fixtures without new development.
- Open questions raised, and how many were real.
- Acceptance criteria passed, failed or not tested.
- Rework after verification.
- Reproducibility across repeated runs.

A fast result that hides an ambiguity is a failure. A slower one that exposes it before development is a success.

## 13. Reuse and governance

Psiberline is a sibling of Suite Builder, which compiles website evidence into test suites. Phase 4 has the same shape, and Suite Builder's pipeline organisation, typed intermediate structures, byte-for-byte goldens and mutation testing are candidates for reuse. Each is inspected first and reused only where the abstraction is real. Crawling, HTML interpretation and page models are left behind.

TypeScript is the implementation language because Suite Builder is written in it. That constrains the compiler, not its output.

Governance comes from Ghost-Core by its stamping process, after this vision is approved.

## 14. Principles

1. **Each phase pays for itself.**
2. **The typed tree is the contract** between interpretation and everything downstream.
3. **Compose from verified parts.** New parts are verified before they can be selected.
4. **Preserve provenance** from source passage to generated test or module.
5. **Fail visibly.** Ambiguity, contradiction and unsupported constructs stop the pipeline.
6. **No model in the chain.** What a model helps write is reviewed and committed before it runs.
7. **Deterministic end to end.**
8. **Check on the lowest rung that works.**
9. **No abstraction before its second use.** One domain, one target, until a second exists.
10. **Keep the data boundary.**

## 15. Risks

- **Natural language is not a specification.** Tickets omit edge cases and lean on unwritten knowledge. The pipeline must ask, not guess.
- **The rules may convert less English than hoped.** If most sentences need a person, phase 0 is a proofreader with a small helper. That is still useful, and conversion rate is the number that says which it is.
- **The typed tree may be costly to review.** If approving it takes as long as testing by hand, phases 2 and 3 do not pay. Review time is measured from the first slice.
- **Tickets may not trace to code.** Phase 1 depends on commits that name their ticket. Where they do not, linking is manual.
- **A synthetic corpus is cleaner than a real one.** What works here may not survive real tickets. The first weeks on real requirements are a test of the design, not a rollout.
- **Coverage may grow slowly.** If most stories need a new fixture, the compiler adds little. Coverage rate is the number that says so.
- **Product fixtures need the developers.** Phase 5 cannot be done to a team, only with one.

## 16. This sprint, and decisions

**Scope of the first slice.** One requirement, "read 50 panels of type A," taken through the whole chain in miniature: a catalogue record, one EARS sentence, an ontology of four assets (plant, site, pad, panel), the proofreader, one rewrite rule, a parser, a unit check, and one generated test from one test fixture. A second requirement, "read 10 more of type B," then proves reuse. No Lean in the first slice.

**Settled by Ghost (2026-11-26).**

1. EARS is the controlled English.
2. The synthetic corpus is drawn from Solarpunk, a solar project Ghost owns.
3. The catalogue is JSON files under version control.
4. The stack is TypeScript.
5. The chain is deterministic end to end, with no AI in it.

**Open.**

1. Ownership of the engine after transfer into the adopting organisation.

---

**Psiberline's goal is to make every triaged ticket leave behind a checked statement of intent, and to compile those statements into tests first and software after, by a chain that needs no AI to run.**
