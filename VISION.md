# Psiberline: Vision and Product Thesis

**Status:** Approved by Ghost, 2026-11-26 (P-021); aspirational, not a statement of implemented capability
**Supersedes:** the revised vision of 2026-11-26, which covered the language and the compiler together
**Implementation language:** TypeScript
**Repository:** https://github.com/Ghost-in-the-Kernel-Labs/psiberline

---

## 1. What changed from the last vision

The work is now two projects, split where the typed tree is handed over.

- **The language project** (its own repository) owns everything up to an accepted requirement: the corpus, the catalogue, the ontology, the EARS grammar and parser, the proofreader, the rewrite rules, the checks on a requirement's meaning, and triage. It is built first and pays for itself in clearer tickets and faster triage.
- **Psiberline is the compiler.** It starts from an accepted requirement, already parsed and approved, and composes tests, and later application modules, from verified fixtures.

Psiberline no longer reads English. It does not parse, proofread, rewrite or triage. Those sections of the last vision move to the language project.

## 2. Purpose

Compile an accepted requirement into a test that proves it, by selecting and configuring parts that are already verified, with every step traced back to the requirement.

> A requirement that has been written formally and approved should not need a person to turn it into a test. If the same kind of requirement has been tested before, the test already exists in pieces. The compiler finds the pieces and addresses them.

The long-term purpose reaches further: application modules composed the same way, so a defect fixed once is fixed for every application built from the same parts.

## 3. What Psiberline is and is not

Psiberline is a compiler from typed requirement trees to test plans, and later to application modules.

It is not:

- A reader of tickets or free English. Its input is the language project's output.
- A code generator. It writes no new code; it selects and configures fixtures.
- A stage with a model in it.
- A judge of what a requirement meant. That was settled when a person approved the tree.
- A way to restructure an application without its developers' agreement.

## 4. Where Psiberline sits

```
requirement in English ──► language project ──► accepted typed tree ──► Psiberline ──► test plan ──► runner
                           (parse, proofread,     (JSON, approved,       (classify,      (JSON)
                            check, approve)        versioned)             resolve, compose)
```

**The handover is files, not code.** The language project writes each accepted requirement as JSON: its typed tree, its acceptance criteria, its provenance and the name of the person who approved it, with the version of the ontology and of the tree's format. Psiberline reads those files. Neither project imports the other.

**The format is a contract with a version.** Psiberline names the version it accepts and refuses any other. A change to the format is a change both projects make on purpose.

**Psiberline never trusts its input.** It checks every tree against the format, refuses one that is not approved or not accepted, and refuses a word or a unit it does not know. A refusal names the requirement and the rule.

## 5. The compiler's stages

| Stage | What happens | Fails with |
| --- | --- | --- |
| 1. Intake | A tree is read and checked against the format's version, its status and its approval. | The requirement and the rule it broke |
| 2. Classification | The requirement's kind decides the compiler's response (section 6). | "No rule classifies this" |
| 3. Capability resolution | Each acceptance criterion is matched to a fixture that can prove it. | "No fixture exists": a named gap, never a guess |
| 4. Composition | The fixture's inputs are addressed from the tree: which asset, how many, what unit, what limit. | An input the tree does not supply |
| 5. Plan | The result is written as a test plan in JSON: the fixture, its inputs, what is asserted, and the trace. | n/a |
| 6. Run | One runner executes a plan against the application under test. | The assertion that failed |
| 7. Trace | From any plan back to its criterion, requirement, source passage and approver. | A trace that does not reach a source |

Every stage is deterministic: the same trees, fixture versions and compiler version give the same bytes.

## 6. Story classification

| Story classification | Compiler response |
| --- | --- |
| New capability | Select a module, or report that a fixture must be written |
| Existing capability | Reuse an existing module |
| Configuration change | Modify module configuration |
| Domain extension | Refuse until the ontology's new version is accepted |
| Constraint change | Re-evaluate the plans that depend on it |
| Integration change | Select or modify an adapter |
| Defect correction | Identify the affected capability and its verification obligations |
| Documentation | Update generated documentation |
| Research or investigation | No automatic implementation |

## 7. Fixtures and the host

A fixture is a verified unit that satisfies a canonical requirement. Two requirements asking to read 50 panels of type A and 10 of type B resolve to one reading fixture, addressed twice.

**Test side first.** The first fixtures are test fixtures: verified pieces from which test plans are composed. They change nothing in the application under test.

**Product side later.** Product fixtures are written against a host that provides common services: type and schema enforcement, dependency injection, capability registration, event dispatch, transaction management, error handling, logging and telemetry, authorization, configuration, and version compatibility. A host service is built when the first fixture needs it.

**Writing a new fixture is ordinary development.** It is written, reviewed and verified before the compiler may select it. The compiler composes; it does not improvise.

**Composition is checked.** Two verified fixtures can still interact badly. Contracts between fixtures are checked when they are composed.

**A missing fixture is a result.** "No fixture exists for this criterion" is the compiler's honest answer, and the list of such gaps is the fixture library's backlog.

## 8. Verification

Each claim is checked on the lowest rung that can establish it. There is no machine-checked proof (P-020).

1. **Checks on the input tree:** format, status, approval, known words and units.
2. **Each fixture's own tests and mutation**, before it can be selected.
3. **Constraint solving** for conditions of the form "A equals B when C."
4. **Property-based tests** for a fixture's behaviour over many generated inputs.
5. **The generated plans themselves**, run against the application.

A plan that passes shows the application matches the approved tree. It does not show the tree matches what was wanted; that is the language project's approval step.

Generated, compiled, tested, verified and accepted are different words and are not used as synonyms.

## 9. A deterministic chain, and where AI stands

No stage of Psiberline is a model. A model may help write a fixture or a classification rule, which is then reviewed, tested and committed as ordinary code. The compiler runs to completion with no model available.

Trees and the documents behind them are data. Text inside them cannot change Psiberline's rules.

## 10. The data boundary

This repository holds the compiler, its fixtures for synthetic applications, and synthetic trees.

- Nothing an employer or customer gave enters this repository: no requirement, no tree made from one, no code.
- Development here uses trees written by hand, or produced by the language project from its synthetic corpus.
- Fixtures for a real application are written in that application's own environment.

## 11. Measurement

For every run, measure:

- **Coverage rate:** the share of accepted requirements that compile from fixtures that already exist.
- Time from an accepted requirement to a passing plan.
- Human interventions, and what each was for.
- Gaps reported, by kind.
- Plans passed, failed or not run.
- Reproducibility across repeated runs.

The founding vision's one-hour target stands as an aspiration for requirements that resolve to existing fixtures.

## 12. Reuse and governance

Psiberline is a sibling of Suite Builder, which compiles website evidence into test suites. Its pipeline organisation, typed intermediate structures, byte-for-byte goldens and mutation testing are candidates for reuse, each inspected first and reused only where the abstraction is real.

Governance comes from Ghost-Core, from which this repository is stamped.

## 13. Principles

1. **Compose from verified parts.**
2. **The typed tree is the contract** between the two projects, with a version.
3. **Never trust the input.**
4. **A gap is a result, not a failure to hide.**
5. **Preserve the trace** from plan to source passage.
6. **No model in the chain; deterministic end to end.**
7. **Check on the lowest rung that works.**
8. **No abstraction before its second use.** One domain, one target, until a second exists.
9. **Keep the data boundary.**

## 14. Risks

- **A tree designed without its consumer.** If the language project fixes the format alone, it may leave out what composition needs. Psiberline's first slice is built early, against a hand-written tree, so the format is tested from both sides.
- **The format drifts.** Two repositories can change one contract out of step. The version check at intake is what catches it.
- **Coverage may grow slowly.** If most requirements need a new fixture, the compiler adds little. Coverage rate is the number that says so.
- **Synthetic trees are cleaner than real ones.** What compiles here may not survive real requirements.
- **Product fixtures need the developers.** That phase cannot be done to a team, only with one.

## 15. The first slice, and decisions

**Scope of the first slice.** One accepted tree, written by hand, for "read 50 panels of type A": intake, classification, one test fixture verified by its own tests, a plan in JSON, the runner green against a stand-in application, and the trace. A second tree, "read 10 more of type B," then proves reuse with nothing new written.

**Carried over, settled by Ghost.** The stack is TypeScript; no model is in the chain; tests before product code; one domain, solar; a generated test is a plan in JSON run by one TypeScript runner; no machine-checked proof; the adopting organisation is never named here.

**Open, for Ghost.**

1. The language project's name and repository.
2. Where the tree's format is written down: in the language project, with Psiberline pinning a version, or here until that repository exists.
3. Which of Psiberline's founding decisions move to the language project (EARS, the corpus, the catalogue, the proofreader, rewrite rules, approval, units).
4. Ownership after the carry-over, now a question for each project.

---

**Psiberline's goal is to turn an accepted requirement into a test that proves it, by composing parts that are already verified, with nothing guessed and everything traced.**
