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

## Phase 1: the first slice, one requirement through the whole chain

### 1.1 The corpus

Check: `corpus/` holds at least five synthetic requirements written from Solarpunk's own, each a text file with an id, among them "read 50 panels of type A" and "read 10 more of type B"; `corpus/MANIFEST.json` lists each with its id and where it was drawn from; a unit test holds the manifest to the folder in both directions, with a planted break (a file the manifest lacks); nothing in it came from an employer or a customer (C-033).

### 1.2 The catalogue's records

Check: `src/leaf/` holds the nine record types of `VISION.md` section 5 with a requirement's status and supersedes and every record's provenance (its source passage, what produced it, who approved it); a reader loads a catalogue of JSON files and names each record that breaks a rule (an unknown status, a link to a record that does not exist, a record with no source); a unit test holds each rule with a planted break; mutation leaves no survivor unexplained in `docs/MUTATION.md`.

### 1.3 The ontology, four assets and one measurement

Check: a file under `ontology/` defines plant, site, pad and panel with what each contains, voltage with its unit and range, and the operation read; a check names a containment that loops, a measurement with no unit and a word defined twice, each with a planted break; a command lists every word a requirement may use.

### 1.4 The grammar and the parser for two patterns

Check: the contract numbers EARS's patterns as invariants; a tokenizer and a parser turn a sentence of the plain pattern ("The <system> shall <response>") or the event-driven pattern ("When <trigger>, the <system> shall <response>") into a typed tree of actor, event, operation and constraint, and refuse any other sentence with the invariant it broke; one golden per corpus sentence, compared byte for byte; the same sentence parsed twice gives the same bytes.

### 1.5 The proofreader

Check: a command reads a requirements file and prints, for each sentence that is not EARS, each word the ontology lacks and each unit that does not resolve, the file, the line, the rule broken and the text; it exits 1 on any and 0 on none; its output for the corpus is a golden; a sentence planted with each fault is caught.

### 1.6 The first rewrite rule

Check: one rule, with an id and a version, rewrites one pattern of plain English ("<system> should <response> if <trigger>") into EARS and records its id on the result; a sentence no rule matches comes back as written and flagged; the rule has its own tests and a planted break; a run prints the corpus's conversion rate, and a test repeats the run.

### 1.7 The checks on the tree

Check: a tree whose units do not agree, whose asset is not in the ontology or whose value is outside its measurement's range is a finding naming the requirement and the rule, before any output and never beside it; each has a planted break; the corpus passes.

### 1.8 The first test fixture and the first generated test

Check: one test fixture, verified by its own tests and mutation, reads a count of panels of a type from a stand-in application kept under `test/`; the acceptance criterion of "read 50 panels of type A" compiles to a test that is the fixture with its inputs addressed and nothing written new; the generated test is a plan in JSON (P-011), a golden byte for byte, and one TypeScript runner runs it green against the stand-in.

### 1.9 Reuse

Check: "read 10 more of type B" compiles to a test from the same fixture with 10 and type B; the diff of the tree against 1.8 holds no new fixture and no change to the compiler; a run prints the coverage rate for the corpus (the share of its requirements that compile from fixtures that exist), and a test repeats it.

### 1.10 The trace

Check: a command given a generated test prints its acceptance criterion, its requirement, the source passage and each rule that touched it, each by id; its output for 1.8's and 1.9's tests is a golden; a generated test whose trace does not reach a source passage is a failure, with a planted break.

### 1.11 Tune-up pass 1

Check: `docs/when/tune-up.md` followed in full, both runs of the gate; the metrics table written; the navigation log's "Last review" set; each override in `docs/HANDOFF.md` past its cooldown removed.
