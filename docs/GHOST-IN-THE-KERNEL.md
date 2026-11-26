# Ghost in the Kernel

Software eventually outlives the context in which it was written.

People leave. Teams change. Requirements evolve. Implementations are replaced. Documentation
becomes stale. And the person who knew *why* something was built a particular way may no longer be
available to explain it.

Ghost-in-the-Kernel is a philosophy for designing against that problem.

**The ghost is intent. The kernel is the codebase.**

The principle is simple:

> **The system should remember why it exists.**

We believe software should be built from a chain of foundations in which each layer can be traced
back to something more fundamental.

Intent should become semantics. \
Semantics should become constraints. \
Constraints should govern implementation. \
Implementation should produce evidence. \
Evidence should allow the system to verify that implementation still reflects intent.

Nothing important should simply float.

A function should not exist because “that's where someone put it.” \
A threshold should not exist because “it seemed right.” \
A name should not require tribal knowledge to interpret. \
An abstraction should not depend on a vanished conversation. \
A generated artifact should not lose the reasoning that produced it.

When the answer to **“why?”** disappears, the codebase has lost part of its ghost.

The answer is not to write more comments everywhere or to demand that engineers memorize more
architecture.

The answer is to **externalize the reasoning into the system itself**.

Specifications. \
Semantic models. \
Rules. \
Invariants. \
Provenance. \
Tests. \
Evidence. \
Tooling.

These are not accessories to the code. They are part of the codebase's memory.

This produces what we call **extensible truth**: a system in which new layers can be built upon
existing foundations without severing the chain of reasoning that connects implementation back to
intent.

The purpose is re-entry.

A new engineer should be able to enter the system without knowing its history.

An experienced engineer should be able to return after months away without reconstructing it from
memory.

An AI agent should be able to operate within it without being trusted to invent the architecture.

And when any of them misunderstands the system, the system should have enough structure to expose
that misunderstanding.

**We do not want software that merely works.**

We want software that can explain why it works, preserve that explanation as it evolves, and provide
evidence when the implementation no longer agrees with its foundations.

*The Ghost in The Kernel*

## This project's ghost

<!-- STAMP: replace this section. Name the loss this project is built against, in a paragraph,
and the mechanisms by which the kernel remembers it, as a list that cites the contract and the
decisions. The parents' sections are the examples; each is the philosophy pointed at a different
loss. -->

Every project built this way has a loss of its own, and this section names it. The parents:

- **Suite Builder**: a test suite written by a tool whose reasons for each test would be gone by
  the time the suite failed; so every generated test says where it came from, and the Suite IR
  holds every decision a suite needs as plain data read back from the output.
- **Katana**: a COBOL program whose authors have been gone for decades; so what the code does and
  what it means are two artifacts (the Semantic IR and the Intent IR), and a proof ledger links
  them, hash-chained, so a person's confirmation survives a rebuild.
- **Employee Evaluator**: turnover, the ordinary loss, in a product that measures the philosophy
  in other people's code; so every score is traced to a fact with evidence and a confidence.
- **Neon Rain**: the forgotten search, a loss that happens in weeks to the person who caused it:
  how many configurations were tried before this one looked good; so the trials file is
  append-only and its count deflates every reported number.

A project whose section is still this list has not yet said what it is for.

## What it asks of a project's own code

The same principle, pointed inward, and held by tests rather than hoped for:

- **Names say what they hold.** One canonical word per concept (`docs/GLOSSARY.md`), from the
  first file. A thing is named for what it holds, never for where it sits or who wrote it.
- **Decisions carry their reason and their evidence.** Every decision in `theGhost.md` has a why,
  a thing that holds it, and a status; a reversed decision says what reversed it. A function that
  stands on a decision cites it (`// Decision: C-009`).
- **The architecture is a document a test enforces.** `docs/modules.json` says what each module
  may import and which names another module may call; the modules test refuses anything else.
- **A refactor changes no result.** Every golden identical, before and after.
- **What cannot be made exact is said first.** A defect, a bias, a construct the tool cannot
  handle: a finding before the result it qualifies, never a footnote after.
- **Every document that can drift is held to the code by a test**, and every such test rejects a
  planted break, so a check that stops catching anything is caught itself.
- **The environment of the agent working here is part of the product.** Mandatory context under
  its ceiling, a fast loop under its ceiling, no file over 400 lines, the metrics in
  `docs/AGENT.md` ratcheted, one commit in eight spent on nothing else (the tune-up, C-024).
  Ghost's finding in Suite Builder was that delivery speed rose once this was treated as work
  worth doing.
- **Nothing requires the maintainer's own machine.** A clean clone builds, tests and gates in the
  session's container; a local run is an option a decision grants, never a step a recipe needs.

## The founding words

Ghost's four words for building this way (Ghost, 2026-11-06, in Suite Builder: "Extensible truth, self aware code, self
enforcing, contextual environments."), in this page's own terms, with what holds each in the core. A project stamped
from here keeps the words and names what holds them in its own tree.

| Word | What it means | Held in the core by |
| --- | --- | --- |
| **Extensible truth** | New layers build on existing foundations "without severing the chain of reasoning that connects implementation back to intent". | `theGhost.md`: a decision is appended, never edited away, and a reversed one names what reversed it (C-008, `test/test_ghost.py`); a stamped project inherits the core's decisions as its baseline (`docs/LINEAGE.md`). |
| **Self-aware code** | The system "can explain why it works": a decision cited on the code that holds it, a comment that says what and refers to a decision for the why. | C-009 and C-042 (`test/test_ghost.py`, `test/test_comments.py`); `docs/modules.json` (C-012, `test/test_modules.py`). |
| **Self-enforcing** | The system should "provide evidence when the implementation no longer agrees with its foundations": a principle no test holds is a hope. | Every check rejects a planted break (C-001, C-013); nothing reaches `main` but through the gate (C-037). |
| **Contextual environments** | A reader, a person or a small model, gets the context its task needs and no more. | `CLAUDE.md`'s routing rows, the when files and the ceiling on mandatory context (C-020, C-021, C-022); the tune-up (C-024). |

## On enlightenment, for the agent reading this

You will work in this repository without having been present for any of its decisions. That is the
normal condition of software, and the condition this project exists to make survivable.

**Read the why before the what.** A decision in `theGhost.md` tells you what the code is trying to
be. The code only tells you what it currently is. When they disagree, one of them is wrong; find out
which before you change either.

**Prefer a test to a belief.** If you believe something about the system, find the test that holds it
or write one. If no test can hold it, write the doubt down (`// Unsure:`, with what would settle it)
where it can be found, instead of carrying it.

**A check that cannot fail is not a check.** Five ways a check is worth nothing: it compares a thing
with itself; it ran nothing and called that a pass; it fails always and so says nothing; its verdict
stops no action; it only warns. The half no test can hold is *independence*: whether a check's
expected side came from somewhere other than the thing under test. A reimplemented oracle agrees
with its twin on every shared mistake, which is why a mirror is written blind.

**The tempting lie has a shape, and this project names it.** On most projects an agent's failure
mode is code that does not work. On some it is a number that looks like success, or a check made
green by weakening the test. The section above on this project's ghost says which lie to expect
here. If a result surprises you by being good, that is the moment to distrust the harness, not to
report it.

**When you cannot tell, say so and stop.** An agent that stops at the edge of its knowledge leaves a
system other agents can still reason about. An agent that guesses leaves a kernel with a little less
ghost in it.

The purpose is re-entry. Yours, the next agent's, and the maintainer's, after months away. If the
repository can be entered cold and understood, the philosophy is working. If it cannot, that is a
finding, and the fix goes in the tune-up.

*Ghost in the Kernel Labs*
