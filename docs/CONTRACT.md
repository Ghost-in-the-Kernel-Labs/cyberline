# The kernel contract

<!-- STAMP: rename this file to the project's contract (HARNESS.md, SCORE-CARD.md, SUITE-IR.md) and
replace the prefix XX with the project's; keep the header's rules and the numbering. -->

The contract precedes the code. It is the specification the leaf module is built from and that a
mirror could be written from blind: if something here is not precise enough to implement, that is a
defect in this document, and the fix is to make it precise, not to read the code. Each invariant is
one heading, `## XX-nn title`, numbered in sequence and never reused; code cites one as
`// Invariant: XX-03` (or the language's comment) and `test/test_contract.py` holds the two
together in both directions: every invariant is named somewhere in the leaf module, and the code
names no invariant the document does not have.

The leaf module (`docs/modules.json`'s `leaf`) holds this contract in code: the types and the
numbers every other module imports and that imports nothing of the project's own. A threshold
lives there and nowhere else; a threshold defined elsewhere fails the check.

## XX-01 The leaf module imports nothing of the project's own

Every other module may import it; it may import only the standard library and the stack's vendored
dependencies. Held by `test/test_modules.py` (`mayImport: []`).

## XX-02 Every number a document reports comes from a run the repository can repeat

A number without the command that produced it does not exist. Held by the project's results check.

## XX-03 What the kernel cannot make exact, it says first

A construct, a case or an input the kernel cannot handle is a finding (`docs/FINDINGS.md`) before
it is output, never silent output. Held by the project's findings check.
