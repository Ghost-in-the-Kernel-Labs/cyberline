# Tune-up: improving the agent's environment, changing no result (C-024)

Read this when your task is a tune-up: a **tune-up commit** (`scripts/commit.sh` says one is due:
every eighth commit) or a **tune-up pass** (the last item of a phase, `TODO.md`'s "Tune-up pass N").
A commit is steps 1, 4, 5 and 6. A pass is every step, by one agent in one session.

**You may change:** routing rows and when lines; documents under `docs/` other than those listed
below; the glossary; names, to the glossary word; cross-references (`See also`, `Held by`); a
document's length; a file over 400 lines, split; a slow test moved out of the fast loop;
`scripts/checks/`; a missing regeneration command. **You may not change:** any result (every
golden identical, every generated file identical after its command); any test's assertions;
anything under the project's source modules, except by the structure half below; `docs/CONTRACT.md`'s invariants; `theGhost.md`;
`docs/ROADMAP.md`; a metric's target; the navigation log's entries, except to wipe them in step 5.
A fix that needs one of those, however small, is a question for step 6. You write no feature, no
test of code, no module: **a tune-up that builds has overshot.** A refactor is not building: the
structure half (below) moves code with a proof that nothing it does changed.

## The steps

1. **Note every miss as it happens:** what you looked for, where you looked first, where it was.
   The notes are the pass's product; steps 4 and 6 are made of them.
2. **Re-measure** (pass only), by two runs of the full gate, the release checkpoint (C-040: the fast
   checks land every commit between passes, so the pass is where the slow tests, every stack's gate and the
   metrics run; what they find is a fix-forward item, never a reason to undo a landing). First the cold run, `GHOST_COLD=1 scripts/gate.sh`:
   every cache a step keeps is bypassed and rewritten, its last line begins `gate (cold):`, its
   log is build/gate-cold.log, and its minutes go only to the journal's Cost line and the
   `tune-up:` commit's verdict line, never to the table. Then the warm run, `scripts/gate.sh` as
   every commit runs it (it logs to build/gate.log; grep that for `FAILED`, `Error`, `refused`):
   its last line gives the fast loop's seconds and the gate's minutes, and the table takes those:
   `python3 -I scripts/metrics.py --fast-loop <seconds> --gate <minutes> --write` (a bare `--write`
   leaves those two cells as they were). The script, not you, keeps the two apart: the cold gate
   passes `--cold`, and `--cold --write` prints one line and exits 1. It also refuses while an
   armed metric has regressed: a question for step 6, never a number or a target to edit. Step
   times come from build/gate-times.txt, one `<seconds> <step>` line per step of the last warm
   gate (`scripts/gate.sh`'s header): a tune-up commit reports them from there, without rerunning.
   Every advisory the stack's audit reports under the gate's threshold (a moderate or low one the
   gate lets through) is listed in `docs/HANDOFF.md` each pass, the package and the advisory's link,
   never silently left; a stack with no packages lists none (`docs/DEPENDENCY-REVIEW.md`, layer 3).
3. **Walk a stamp** (pass only, and only in a project that stamps others, such as Ghost-Core): stamp
   a scratch project with real git (`--allow-dirty`, since step 2's write has dirtied the tree), read
   its entry files as a newcomer and run its fast loop; every stale sentence or pointer to a file it
   lacks is a note for step 4.
4. **Read the debriefs** (`docs/NAVIGATION-LOG.md`) and fix what they and your notes found. Each
   debrief's complaints get one verdict: acted on earlier, acted on now, not valid, open. A point two
   or more agents ran into separately is actionable; one agent's alone is noted, not acted on, unless
   it is plainly a fact gone wrong. Each fix is one small diff; the fast loop after every fix.
   `CLAUDE.md` stays under its word ceiling.
   Pass only, stamped projects: `docs/when/core-update.md` (Core's later decisions, adopted or refused).

### The structure half (optional)

After step 4, in a commit or a pass, an advisor of the ruling grade (`docs/when/grades.md`) reads
the tree read-only and names refactors: one rule in two places, a function that holds two
decisions, a module that reaches past its neighbour. Each refactor is done only with a proof that
every result is identical: every golden byte-equal; the fast loop and the gate green; `git diff
--stat` of the outputs (generated files, goldens, the stamp) empty; for a refactor of a check, its
planted breaks still refused. A refactor without its proof is reverted, not argued. It lands in the
same `tune-up:` commit or the next one. The navigation half (steps 1 to 6) stays as it is.

5. **Wipe the entries** of the navigation log (git keeps them) and set its "Last review" line to
   the commit the review ran at (`git rev-parse --short HEAD`; the tune-up's own hash does not
   exist yet). Pass only: an open question goes to the ruling grade,
   read-only; its answer goes in the journal entry.
6. **Stop and hand back.** Debrief as the log's header says. The hand-back: the gate's verdict
   line, the metrics before and after, your notes, step 4's verdicts, the open questions, each with
   what it needs (a decision for Ghost, a roadmap line, a target that cannot be met). Commit
   nothing yourself: the reviewer commits, the message starting `tune-up:`.

## Edge cases

- A tune-up commit that falls mid-phase moves nothing in `TODO.md`: no item is done by it (a
  reopened phase's closing "Tune-up commit" item, below, is the one it moves).
- A commit and a pass that fall due together: the pass is the commit, one `tune-up:` commit.
- A fix-first commit that `scripts/commit.sh` refuses while a pass is due rides inside the
  `tune-up:` commit; it is not made on its own.
- A phase reopened after its pass with at most three new items closes by a `tune-up:` commit that
  re-measures (steps 1, 2, 5, 6), not a full pass; a fourth item makes it a full pass. Its closing
  item is titled "Tune-up commit"; `scripts/checks/todo.py` refuses a fourth item without a "Tune-up
  pass" (Ghost, 2026-11-07, provisional: moved by a decision from the Cost record).
- A due tune-up is deferred only on Ghost's word: the line `Tune-up deferred through <sha>` in
  `docs/HANDOFF.md`, which `scripts/commit.sh` honours by counting from after that commit (C-037).
  An agent never writes it. Ghost's word in chat is as good as the line (C-040): an agent that has
  it writes the line and quotes the word in `docs/HANDOFF.md`'s "Settled by Ghost".
- The count is `main`'s: a session branch's saves (`scripts/save.sh`) are not landings and are never
  counted (C-040).

## The reviewer, not you

Reads the diff against the notes; reverts any change past the may-change list; writes the journal
entry with step 4's verdicts and step 6's questions; moves the item to `docs/DONE.md` (a pass);
runs the full gate; commits with `scripts/commit.sh` and a message starting `tune-up:`; ships (`scripts/ship.sh`). Open
questions go to Ghost.

## Why this is the tightest definition in the repository

Ghost, 2026-10-23: "Tithes tend to be skipped, unless they are put in concrete numbered items on
the roadmap. Also, tithes definitions tend to be an area where poor definition is particularly
punishing. Tithe and navigation tune ups need to be done in the same move. In fact the navigation
tune ups is probably more important than tithe once the project matures." A tune-up agent once
"fixed" grep noise by deleting the mutation cache (Neon Rain J-033); the warning-only cadence
fired 73 times and stopped nothing (Katana J-154). The two runs are AI Slop Block's (ASB-014): its gate grew
from 5 to 21 minutes against a target of 10 until a warm cache and a cold run kept apart, the gate script and not
the agent deciding where each number goes. The structure half is Katana's: its tithe opens with a read-only
structure review and refactors under proofs that nothing changed, where nearly all its "one rule, one place" work came
from (Ghost, 2026-11-06). The reopened phase is AI Slop Block's: its Phase 0 closed three times, and the third pass
built nothing and cost a 19.85-minute cold gate. The gate accepts a `tune-up:` commit at any
count and refuses any other while one is due, so the only way through is this file.
