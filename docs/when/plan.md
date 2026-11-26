# Plan: turning a roadmap into a chain (C-016, C-024)

Read this when you write or change the plan: a roadmap's phases, the items of `TODO.md`, a phase
reopened, an item that waits. Working the plan (what to do next, finishing a step) is
`docs/paths/process.md`'s row, not this file.

## The roadmap's shape

`docs/ROADMAP.md`, in six sections: the product in three sentences, with the thesis to hold and the
thesis to refuse; the principles, numbered; the settled facts, each with its source; what is
deliberately not built; the documents and the test that holds each; the phases.

A phase is a heading (`### Phase N: title`), a paragraph saying what the phase proves, and its items,
one line each, `- N.M what is built`. Its last item is `Tune-up pass N`. A later phase may stand as an
outline, a paragraph without numbers, until the phase before it is built: what it needs is learned
there. When a phase is built its section shrinks to a header, and what it decided lives in
`theGhost.md`.

## The chain's shape

`TODO.md` is the roadmap's open items in order:

- a phase is `## Phase N: title`; an item is `### N.M title` with a `Check:` line under it;
- a check fails before the work and passes after, and names the file, the test or the command that
  shows it;
- items stand in numeric order under their phase, and the first open item has a check;
- every phase ends with `### N.K Tune-up pass N`;
- a done item moves to `docs/DONE.md` under its phase's heading, keeping its number, with the date,
  the journal entry, its check and a tick. Nothing is both open and done, and nothing is done twice.

## Adding items

New items go before the phase's open tune-up pass, and the pass is renumbered to the phase's end. A
done item never changes its number: other documents cite it. An open question a later item depends
on is copied into that item's text, so the item reads whole where it stands.

## A phase reopened

A phase whose tune-up pass is already in `docs/DONE.md` may take new items. With at most three, it
closes by an item titled `Tune-up commit`; a fourth makes its closing item a full `Tune-up pass`
(`docs/when/tune-up.md`, "Edge cases").

## An item that waits

An item that waits on something outside the repository carries a `Waits on:` line: in words (Ghost's
choice or approval, counsel, another project), or one of the two kinds with a shape,
`Waits on: environment (<host or tool>)` and `Waits on: reference (<what>)`. It moves to the last
phase, headed `## Phase W: waiting on Ghost`, keeps its number and adds `Moved: from Phase N`. A
phase whose every item waits takes its tune-up pass with it, the pass's `Waits on:` naming those
items; the waiting phase needs no pass of its own. When what it waits on arrives, Ghost moves the
item back into the chain.

## What holds it

`scripts/checks/todo.py`, through `test/test_todo.py`: the order, the first item's check, the passes,
the reopened phase's limit, the waiting phase's lines, and that the two files share no item.
