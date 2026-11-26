# Core update: taking Ghost-Core's later decisions into a stamped project

Read this at step 4 of a tune-up pass (`docs/when/tune-up.md`) in a project stamped from Ghost-Core.
Core itself is not stamped, so this file exists to be carried into stamps; in Core it is only read.

A stamp is a copy at one commit. Core moves on (both early stamps missed C-035 within days), and a
project that never looks falls behind without a record of it. The look is made once per pass, here.

## 1. Find the commit the project was stamped from

It is written in two places, put there by the stamp: the `Source` line of the project's first decision,
`<prefix>-001` in `theGhost.md` ("stamped from Ghost-Core `<hash>`"), and the project's row in
`docs/LINEAGE.md` (the last column). If the two differ, the row is the one a past pass moved forward.
A hash of `unknown` means the stamp was made without git: ask Ghost which Core commit it was.

## 2. List what Core did since

From a clone of Core, updated to its `main`:

    git -C <core clone> log --oneline <hash>..main -- theGhost.md CLAUDE.md docs scripts test stacks/<stack>

with `<stack>` the project's one stack (`stacks/<stack>/PRESENT`): a fix to its starter lands in Core under
`stacks/<stack>/starter/` and in the project at the root, so compare the two by name. Or, with no clone, the
compare page: `https://github.com/Ghost-in-the-Kernel-Labs/Ghost-Core/compare/<hash>...main`.
Read the log for new `C-nnn` entries in Core's `theGhost.md` (`git -C <core clone> diff <hash>..main -- theGhost.md`),
and for the files that enforce them: the changes under `docs/`, `scripts/`, `test/` and `stacks/<stack>/`.

## 3. Adopt or refuse each new C-nnn, never ignore one

Every new `C-nnn` Core gained since the recorded commit gets one project decision, in this pass:

- **Adopted**: a project decision (`<prefix>-nnn`, Status `in force`, `See also: Core C-nnn`) that cites it;
  the files that hold it copied from Core as Core has them; the check that holds it run and green.
- **Refused**: a project decision with Status `refused` that names the `C-nnn` and says why this project
  does not take it. A refusal is a record, not a way to skip the work: a decision refused without a
  reason is the same as one ignored.

A change in Core to a check, a script or a document with no new `C-nnn` behind it (a bug fix, a wording)
is taken or left by the pass's own judgement and named in the pass's journal entry; it needs no decision.
A file a project has changed on its own is not overwritten: the pass merges by hand and says so in the journal.

## 4. Move the recorded hash forward

When every new `C-nnn` has its decision, set the project's row in `docs/LINEAGE.md` to the Core commit the
pass read up to (`git -C <core clone> rev-parse --short main`), in the same words ("stamped from Ghost-Core
`<hash>`" becomes "taken up to Ghost-Core `<hash>`"). Leave `<prefix>-001` as it is: it is the history of the
stamp, not the state. Record the range read and the decisions made in the pass's journal entry.
