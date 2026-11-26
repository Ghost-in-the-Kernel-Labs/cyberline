# TODO: the open items, in order

The roadmap as a chain: items are done in this order, never out of it, and an item that cannot be
done as written stops the chain and goes to Ghost (C-016). Each item's plan is its step in
`docs/ROADMAP.md` §6, by the same number; its check is copied here. A done item moves to
`docs/DONE.md` with its number kept. `test/test_todo.py` holds this file: headings in numeric order
under their phase, the first open item has a check, every phase ends with a tune-up pass (a reopened phase
of at most three new items with a tune-up commit, `docs/when/tune-up.md`), and
nothing is both here and done or done twice. An item that waits on something outside the repository (Ghost's choice
or approval, counsel, another project) carries a `Waits on:` line naming it in words, or one of the two kinds with a
shape for what a session lacks, `Waits on: environment (<host or tool>)` or `Waits on: reference (<what>)`
(`scripts/checks/todo.py`), and moves to the last phase, headed `## Phase W: waiting on Ghost`, keeping its number and adding a `Moved: from Phase N` line; a phase
whose every item waits takes its tune-up pass with it (the pass's `Waits on:` names those items), and the waiting
phase needs no pass of its own. When what it waits on arrives, Ghost moves the item back into the chain. An open
question a later item depends on is copied into that item's text, so the item reads whole where it stands.

## Phase 0: founding

### 0.4 The contract and the leaf module

Check: `docs/CONTRACT.md` renamed and its first invariants written; `docs/modules.json`'s package and modules set; `test/test_contract.py` and `test/test_modules.py` green on the real folders.

### 0.5 The founding decisions

Check: `theGhost.md` holds Ghost's founding decisions for Psiberline, a decision for each core decision it refuses among them, each with Ghost as its Source. Agents cannot author Ghost's decisions: an agent drafts the questions for Ghost in `docs/HANDOFF.md`, and a builder that reports "waiting on Ghost" has done its job.

### 0.6 Tune-up pass 0

Check: `docs/when/tune-up.md` followed in full; the metrics table written; the navigation log's "Last review" set.

## Phase 1: the first slice, one accepted tree to a passing plan

### 1.1 The tree's format, version 0

Check: a document under `docs/` says what a handed-over requirement holds (its status, its approver, its provenance, its acceptance criteria, its typed tree of actor, event, operation, quantity with unit, and constraint, and the ontology's version) and names its version; `src/leaf/` holds the same as types; a check names each way a file breaks the format, with a planted break for each rule; the document says it is held here until the language project exists.

### 1.2 Two synthetic trees

Check: `trees/` holds two accepted trees written by hand, "read 50 panels of type A" and "read 10 more of type B", each with a named approver and a source passage, and `trees/MANIFEST.json` lists them; a unit test holds the manifest to the folder in both directions, with a planted break; nothing in them came from an employer or a customer (C-033).

### 1.3 Intake

Check: a command reads a tree and refuses it, naming the requirement and the rule, when its format's version is not the one accepted, its status is not accepted, it has no approver, or it uses a word or a unit the ontology version it names does not hold; each refusal has a planted break; the two trees of 1.2 pass.

### 1.4 The stand-in application

Check: a small simulated plant under `test/` answers how many panels of a given type it has; it is a test's helper, in no entry point's import graph; a unit test holds its answers for types A and B.

### 1.5 The first test fixture

Check: one test fixture reads a count of panels of a type from an application and asserts it equals a given number; its own unit tests cover a pass, a fail and a type the application does not have; mutation leaves no survivor unexplained in `docs/MUTATION.md`; an assertion that cannot fail is a planted break the fixture's tests catch.

### 1.6 Classification by rule

Check: the nine classes of `VISION.md` section 6 as rules, each with an id; the two trees classify as a new capability and an existing capability; a tree no rule classifies is reported for a person and compiles to nothing; each class has a unit test.

### 1.7 Capability resolution and composition

Check: each acceptance criterion of a tree is matched to a fixture and the fixture's inputs are addressed from the tree (the type, the count); a criterion no fixture can prove is a named gap in the output and never a guess; an input the tree does not supply stops the compile with the criterion and the input named; each has a planted break.

### 1.8 The plan

Check: the compile of "read 50 panels of type A" writes a test plan in JSON holding the fixture, its inputs, what is asserted and the trace; the plan is a golden compared byte for byte; the same tree compiled twice gives the same bytes; nothing in the plan is written new (P-011).

### 1.9 The runner

Check: one TypeScript runner executes the plan of 1.8 green against the stand-in; a plan whose expected count is wrong fails and names the assertion; a plan naming a fixture the runner does not have is refused.

### 1.10 Reuse

Check: "read 10 more of type B" compiles to a plan from the same fixture with 10 and type B; the diff of the tree against 1.9 holds no new fixture and no change to the compiler; a run prints the coverage rate for the two trees, and a test repeats it.

### 1.11 The trace

Check: a command given a plan prints its acceptance criterion, its requirement, the source passage and the approver, each by id; its output for the two plans is a golden; a plan whose trace does not reach a source passage is a failure, with a planted break.

### 1.12 Tune-up pass 1

Check: `docs/when/tune-up.md` followed in full, both runs of the gate; the metrics table written; the navigation log's "Last review" set; each override in `docs/HANDOFF.md` past its cooldown removed.
