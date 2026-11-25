# Psiberline: Vision and Product Thesis

**Status:** Founding vision; aspirational, not a statement of implemented capability  
**Implementation language under consideration:** TypeScript  
**Repository:** https://github.com/Ghost-in-the-Kernel-Labs/psiberline

---

## 1. The ambition

Psiberline's ambition is to automate the journey from a body of human-authored requirements to working, verified software.

The long-term target is deliberately aggressive: **take a workflow that ordinarily spans requirements analysis, design, implementation, testing, and revision, and compress it toward a single hour of elapsed time wherever the scope and evidence make that possible.**

The one-hour target is a product ambition, not a promise that any arbitrary application can be safely generated in sixty minutes. A small, well-bounded change with clear requirements is a more appropriate early target than an entire enterprise system. The system must measure elapsed time, human intervention, unresolved ambiguity, generated scope, and verification results. It must never make a deadline by silently lowering correctness.

Psiberline should make software creation feel less like translating documents into tickets and then tickets into code, and more like expressing an intent in a language that a disciplined compiler can understand, challenge, formalize, and turn into verified software.

The intended user may be a business analyst (BA), domain expert, product owner, or engineer. A person should be able to describe what a system must do in ordinary or domain-specific language. Psiberline should progressively turn that description into an executable, testable specification and then into software modules.

The thesis is:

> A sufficiently well-specified body of requirements can be treated as a source language. If its meaning can be classified, constrained, represented, and verified, it can be compiled into software.

Psiberline is intended to make that process repeatable, inspectable, modular, and increasingly automated.

## 2. What Psiberline is

Psiberline is envisioned as a **compiler for requirements and other structured or semi-structured human language**.

It should not be a prompt that asks an AI model to read a document and write an application in one leap. That approach makes it difficult to establish what was understood, which rules were applied, where a decision came from, or whether the generated result actually satisfies the source.

Instead, Psiberline should establish a chain of explicit transformations:

1. Ingest a corpus of source material.
2. Interpret it according to a selected language specification.
3. Classify statements and identify their meaning, role, and relationships.
4. Evaluate them against a selected set of rules and invariants.
5. Resolve or expose ambiguity, contradiction, omission, and uncertainty.
6. Build a structured intermediate representation (IR).
7. Plan the software changes or modules implied by that representation.
8. Generate code through one or more output backends.
9. Generate or derive tests and other verification evidence.
10. Run the available checks, compare results against the requirements, and report what is and is not established.

Each stage should have explicit inputs, outputs, contracts, and failure states. The result should be traceable from generated code back through the IR to the source statements that justify it.

Psiberline should be capable of stopping. If the source is contradictory, incomplete, unsafe, or outside the supported language, the right result may be a precise question or a blocked compilation—not invented certainty.

## 3. The source language must be replaceable

The meaning of a corpus depends on the conventions used to write it. A set of solar project requirements, a financial-services specification, a healthcare workflow, and a general software requirements document may use similar words while assigning them different meanings.

Psiberline must therefore avoid assuming that one fixed natural-language interpretation applies to every project.

A **language specification** should define how a particular class of source material is recognized and interpreted. Depending on the domain, it may describe:

- Document and section structures.
- Recognized statement types.
- Domain vocabulary and terminology.
- Required fields and expected forms.
- Relationship and reference conventions.
- Rules for interpreting quantities, units, dates, conditions, and exceptions.
- How to distinguish requirements from rationale, examples, assumptions, and commentary.
- How unsupported or ambiguous constructions are reported.

Language specifications should be independently selectable and replaceable. A project should be able to adopt a different specification without rewriting the entire compiler.

The initial motivating use case is customer requirements for solar software. That is a starting domain, not a permanent restriction. The architecture should make it possible to add or replace a domain language without embedding its assumptions throughout the compiler.

## 4. Rules and invariants must be modular

The language specification identifies how to interpret the corpus. Rule sets and invariants determine what must be true of the interpreted material and of the software that follows from it.

These concerns should be separable.

A rule set may encode domain policies, business constraints, calculations, validation requirements, or organizational conventions. An invariant expresses a condition that must remain true. Some invariants may be universal to the compiler; others belong to a particular domain, project, module, or output target.

The system should support:

- Independently defined and versioned rule sets.
- Reusable rule libraries.
- Project-specific rule configuration.
- Explicit rule precedence and conflict handling.
- Rule provenance: which rule was applied, to what facts, and with what result.
- Tests and examples for each rule.
- Clear handling of missing, conflicting, or inapplicable rules.

A rule should not silently change meaning because an unrelated part of the system changed. Rule changes should be reviewable and testable.

The architecture must distinguish a fact extracted from the corpus, an interpretation inferred from that fact, a policy imposed by a rule, and a decision made by a human. These are different kinds of information and should not be collapsed into one opaque model-generated answer.

## 5. The intermediate representation is the center of the compiler

The IR is the most important architectural boundary in Psiberline.

It is the normalized, structured account of what the source corpus means for the purpose of software construction. It should be independent of both the original document format and the eventual programming language.

The IR may ultimately need to represent:

- Requirements and acceptance criteria.
- Actors, roles, and permissions.
- Entities, attributes, and relationships.
- Workflows, states, transitions, and events.
- Business rules, calculations, and constraints.
- Inputs, outputs, and external interfaces.
- Error conditions and exceptional paths.
- Security, privacy, audit, and operational requirements.
- Dependencies between requirements and software components.
- Open questions, assumptions, conflicts, and confidence/evidence status.
- Links to source passages and the transformations that produced each IR element.

The IR should be typed and validated. It should not be merely a bag of extracted text or a transcript of an AI conversation.

Every important element should preserve provenance: where it came from, how it was interpreted, which rules affected it, and whether a human confirmed it. A reviewer should be able to navigate from a generated behavior to the requirement and source passage that justify it.

A stable IR also creates leverage. Multiple source languages can compile into the same IR, and multiple target backends can compile from it. This is how Psiberline can become a general compiler rather than a collection of one-off document-to-code scripts.

## 6. Output backends must be replaceable

Psiberline should not be tied to a single implementation language, framework, runtime, or deployment environment.

The compiler itself is initially expected to be written in TypeScript. That does **not** mean its generated output must be TypeScript.

An output backend is responsible for translating validated IR into a particular software target. Different backends may generate different languages, frameworks, services, applications, configuration, schemas, or other artifacts.

The backend boundary should make it possible to:

- Add a new target without changing source-language interpretation.
- Generate multiple targets from the same IR when appropriate.
- Validate that a backend supports the constructs it is asked to compile.
- Report unsupported constructs rather than silently dropping them.
- Keep target-specific decisions out of the common IR.
- Test generated output against backend-specific contracts and golden examples.

A backend should declare its capabilities and limitations. Compilation should fail clearly when the IR requires something the selected backend cannot express safely.

## 7. The end-to-end workflow

The intended workflow is a controlled pipeline, not a single generation call.

### 7.1 Ingest

Accept a corpus of requirements and supporting materials. Preserve original source content and stable references to documents, sections, and passages. Normalize formats only as needed; do not discard the original evidence.

### 7.2 Interpret and classify

Apply the selected language specification to identify meaningful statements and classify them. Distinguish requirements from context, examples, rationale, assumptions, constraints, and unresolved questions.

### 7.3 Establish facts and constraints

Extract candidate facts and relationships. Normalize units and terminology where the language specification permits it. Apply the selected rules and invariants. Record the evidence and result for each operation.

### 7.4 Detect problems before coding

Find contradictions, duplicates, gaps, impossible combinations, underspecified behavior, and references that cannot be resolved. Present questions in a form a domain expert can answer. Do not bury unresolved issues inside generated code.

### 7.5 Construct and validate the IR

Build a typed representation of the intended behavior. Check internal consistency, required relationships, and rule satisfaction. Make the IR reviewable before it becomes a basis for implementation.

### 7.6 Plan the implementation

Translate the IR into a dependency-aware plan of software modules and changes. Identify interfaces, data structures, workflows, integrations, and verification obligations. Keep the plan small enough to reason about and traceable to the requirements.

### 7.7 Generate software

Use the selected backend to create or update code. Prefer bounded, composable modules over a monolithic output. Generation should be reproducible where possible: the same source, specifications, rules, IR, backend version, and configuration should produce the same output, or clearly explain why not.

### 7.8 Verify

Generate or derive tests from requirements and acceptance criteria, then run the applicable checks. Verification should include more than whether the generated code compiles. It should establish behavior against the requirements, check invariants, and report untested or unprovable claims.

### 7.9 Report and iterate

Produce a useful account of what was generated, what passed, what failed, what remains uncertain, and which source requirements are covered. If a correction is needed, trace it to the relevant source, rule, IR element, or backend behavior and recompile the affected scope.

## 8. Verification is part of compilation, not an optional afterthought

Psiberline's output is not complete merely because code was generated.

The product goal is not to maximize the volume or speed of code production. It is to shorten the time required to produce **working software whose behavior is supported by evidence**.

Verification should be designed into the compiler from the beginning:

- Requirements should carry acceptance conditions where possible.
- IR elements should map to verification obligations.
- Generated modules should have explicit contracts.
- Tests should be traceable to requirements and invariants.
- The system should report coverage gaps and unverified behavior.
- Failed checks should block claims of successful completion.
- Human review should be required where evidence is insufficient or the consequence of an error warrants it.

The system must distinguish among generated, compiled, tested, verified, and accepted. Those words must not be treated as synonyms.

## 9. AI's role: useful reasoning inside a deterministic system

AI may be valuable for interpreting natural language, proposing classifications, identifying possible relationships, drafting questions, suggesting IR structures, and assisting with code generation.

But model output should be treated as a proposal or input to a controlled process—not as authority.

The compiler should establish explicit boundaries between probabilistic interpretation and deterministic validation. Where a model proposes a fact or structure, the system should preserve its source evidence and subject it to the relevant schema, rules, invariants, and checks.

The product should not depend on a model being correct merely because it sounds confident. It should be able to reject malformed output, detect contradictions, demand confirmation, and reproduce downstream compilation from an accepted IR.

Source documents are data. Instructions embedded in customer documents must not be allowed to override Psiberline's system rules, tool permissions, or compilation policy. The system must treat external text as untrusted input and isolate it from privileged instructions and execution.

The long-term objective is not to remove engineering judgment from the process. It is to encode repeatable engineering knowledge into explicit rules, contracts, tests, and compiler stages so human judgment can focus on the decisions that genuinely require it.

## 10. The one-hour objective

The one-hour ambition should become a measurable engineering target, not a slogan.

A useful early benchmark is a bounded change with:

- A source corpus of known size and format.
- A defined language specification and rule set.
- A limited, explicit software scope.
- A supported output backend.
- A known set of acceptance criteria.
- A reproducible verification environment.

For each run, measure at least:

- Elapsed time from accepted input to verified output.
- Human active time and number of interventions.
- Time spent interpreting, resolving ambiguity, planning, generating, and verifying.
- Number and severity of unresolved questions.
- Requirements represented in the IR.
- Requirements linked to generated changes.
- Acceptance criteria passed, failed, or not tested.
- Rework after verification.
- Reproducibility across repeated runs.

The one-hour goal should be approached in stages:

1. **Assist:** reduce the time required to turn documents into structured requirements.
2. **Specify:** produce a validated IR with traceable evidence and explicit open questions.
3. **Generate bounded modules:** create small software components from approved IR.
4. **Verify generated changes:** automatically test those components against their requirements.
5. **Automate a complete bounded workflow:** take a well-scoped request from source corpus to verified, reviewable change with minimal human intervention.
6. **Expand scope carefully:** increase the complexity and breadth of work only when measurements show that quality remains stable.

A one-hour result that produces unreviewable or incorrect code is a failure. A result that takes longer but exposes a critical ambiguity before implementation may be the better outcome.

## 11. Relationship to Suite Builder and Ghost-Core

Psiberline is conceived as a sibling compiler to Suite Builder.

Suite Builder takes structured website evidence—particularly HTML and related application behavior—and produces QA automation suites. Psiberline is intended to take human-authored requirements and compile them into software modules and their verification evidence.

The projects have different source languages and different products, but they share a deeper engineering problem: transform source material through explicit, testable stages into deterministic, useful output.

Suite Builder is therefore an important source of reusable implementation and engineering knowledge. Reuse should be evaluated deliberately, not assumed.

Potentially reusable areas include:

- Compiler and pipeline organization.
- Typed intermediate data structures and validation patterns.
- Deterministic generation and byte-for-byte output checks.
- Rule and invariant enforcement patterns.
- Test architecture, fixtures, golden files, and mutation testing.
- Traceability and reporting conventions.
- Module boundaries and dependency discipline.
- Quality gates, regression protection, and documentation practices.
- AI-assisted workflows in which model output is constrained and verified.

Domain-specific website crawling, HTML interpretation, browser automation, and page models should not be imported simply because they exist. Psiberline should reuse abstractions that have demonstrated value and leave Suite Builder's domain assumptions behind.

Ghost-Core is the proposed source of project governance and development discipline. The intention is to inherit its useful practices through the proper stamping process later, rather than to imitate the stamp manually or claim that Psiberline has already been stamped.

### Why TypeScript is the initial implementation choice

TypeScript is the preferred initial language because Suite Builder is written in TypeScript and meaningful code reuse is an explicit goal.

Using TypeScript should make it easier to share or adapt existing libraries, types, tests, tooling, and generation infrastructure. It also keeps the initial compiler ecosystem coherent.

This is a choice about the language used to implement Psiberline, not a restriction on generated software. Output backends must remain independently replaceable and may target other languages and platforms.

Python, C++, or C should not be introduced merely because they have compiler-related libraries or performance characteristics. A different implementation language should be considered only when a measured requirement justifies the added boundary and maintenance cost.

## 12. Founding architectural principles

These are proposed principles for the project to test, refine, and eventually formalize as governed decisions.

1. **Separate interpretation from generation.** Source-language understanding must not be entangled with target-language code generation.
2. **Make the IR central.** The IR is the contract between interpretation and compilation.
3. **Make language specifications replaceable.** Domain-specific interpretation belongs in explicit, versioned specifications.
4. **Make rules modular.** Rule sets and invariants should be composable, testable, and traceable.
5. **Make backends replaceable.** Target-specific code generation must not define the source language or common IR.
6. **Preserve provenance.** Generated behavior must be traceable to source evidence and the transformations that produced it.
7. **Fail visibly.** Ambiguity, contradiction, unsupported constructs, and failed checks must not be silently papered over.
8. **Treat model output as untrusted until validated.** Confidence and fluency are not proof.
9. **Prefer deterministic downstream processing.** Once interpretation is accepted, validation and compilation should be reproducible.
10. **Verification is a product feature.** Generated code without evidence is an incomplete result.
11. **Optimize for verified elapsed time.** Speed matters only when quality and traceability remain intact.
12. **Reuse proven infrastructure without importing irrelevant domain assumptions.** Suite Builder is a source of leverage, not a mandate to copy its entire design.

## 13. Risks and questions the project must confront

The vision is ambitious and contains unresolved design questions. These should become explicit research and implementation work rather than hidden assumptions.

### Natural language is not a formal specification

Requirements often omit edge cases, conflict with one another, or rely on tacit organizational knowledge. Psiberline needs a disciplined ambiguity model and a way to ask targeted questions. It must not pretend every document can be compiled without clarification.

### The IR could become too generic or too domain-specific

A generic IR may lose important domain meaning. A domain-specific IR may prevent reuse across languages and backends. The project must discover the right shared core and allow typed extensions without turning every project into a bespoke compiler.

### Rules can conflict or drift

Rule sets need versioning, precedence, provenance, and regression tests. A rule update can change generated behavior even when source documents have not changed; that change must be visible.

### Generated code can be plausible but wrong

Compilation success and superficial tests do not establish that the software satisfies the requirements. Verification must be mapped to requirements and must report its limits.

### Scope can overwhelm the one-hour target

An entire production system may involve integrations, deployment environments, security reviews, data migrations, and operational constraints that cannot be compressed into one hour. The target must be scoped and measured honestly.

### AI can introduce nondeterminism and unsafe assumptions

The project needs controlled model boundaries, structured outputs, validation, provenance, and a secure execution model. Customer documents and generated code must not be allowed to grant themselves privileges.

### Reuse can create accidental coupling

Suite Builder's existing code should be inspected for stable, domain-independent contracts before reuse. Shared code should be extracted only when the abstraction is real and tested—not merely because two projects have similarly named folders or functions.

## 14. A sensible development progression

This is a directional sequence, not a detailed committed roadmap.

### Foundation: prove the compiler boundary

- Inspect Suite Builder and identify reusable, domain-independent components.
- Define a minimal source-language specification contract.
- Define the first version of the IR and its validation rules.
- Define interfaces for rule sets and output backends.
- Establish deterministic fixtures and tests for each stage.
- Demonstrate source-to-IR transformation with provenance.

### First vertical slice: requirements to a bounded module

- Choose a narrow, representative requirements corpus.
- Implement classification and invariant checks.
- Detect ambiguity and contradiction.
- Compile accepted IR into one small software module.
- Derive acceptance tests and run them.
- Produce a traceability report from source to generated code and test evidence.

### Repeatability: make the result trustworthy

- Add regression corpora and golden outputs.
- Test rule changes and backend changes independently.
- Measure reproducibility and failure modes.
- Add explicit human approval points.
- Demonstrate that a change to one domain pack does not break unrelated language or backend packs.

### Workflow automation: reduce elapsed time

- Automate the transition between stages where contracts are satisfied.
- Parallelize independent work only where dependencies permit it.
- Make questions and approvals concise and actionable.
- Measure time, rework, and verification quality.
- Optimize the slowest proven bottlenecks rather than guessing.

### Expansion: multiple languages and targets

- Add additional language specifications.
- Add additional rule packs and domain invariants.
- Add additional output backends.
- Demonstrate that a new source language or target can be added without rewriting the compiler core.

## 15. What success looks like

Psiberline succeeds when a domain expert can provide a body of requirements and receive a software change whose meaning is explicit, whose implementation is traceable, and whose behavior has been checked against the original intent.

A mature Psiberline should be able to answer, for any generated module:

- Which source requirements caused this module to exist?
- How were those requirements interpreted?
- Which language specification and rule versions were used?
- Which invariants were checked?
- Which assumptions or human decisions were made?
- Which backend generated the code?
- Which tests and verification results support the claim that it works?
- What remains unimplemented, untested, or uncertain?
- Can the same accepted inputs reproduce the same result?

The ultimate experience should be simple for the person expressing the need: describe the desired behavior, answer the questions that genuinely matter, review the resulting change, and receive verified software.

The complexity should live in the compiler's explicit machinery—not in an opaque chain of guesses.

**Psiberline's goal is to make the path from intent to verified software dramatically shorter, with one hour as the aspirational target for increasingly broad classes of bounded work.**
