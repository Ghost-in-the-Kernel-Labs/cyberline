# Lessons from four Ghost projects, for the Ghost-Core template

Read-only survey of Suite Builder (TypeScript, 292 decisions, oldest), Katana (Java, 89 decisions),
Employee Evaluator (Java, 75 decisions) and Neon Rain (Python, 23 decisions, newest), 2026-10-23.
The four are four drafts of one template. Where they agree, the template copies. Where they
diverged, the later project usually fixed what the earlier one learned, and the later form wins
unless noted. Every claim below names the repo and the decision or journal entry it came from.

## 1. What every project converged on (copy as is)

**A pointer CLAUDE.md, under a word budget.** All four ended with the same shape: a two-paragraph
pitch; a routing table (`Task | Start here | Contract | Tests`, two to five files per row, none
over 400 lines); a "When X happens, read Y" list (SB G-283/G-289, EE E-069, Katana R-080, NR
J-028); "Before calling work done"; two or three rules that apply at every moment (maintainer is
Ghost; what never enters the repo); and the binding supply-chain rules, inline. Ghost's own words
for the rationale appear in three repos: replace large chunks of data read into context with cheap
one-line entries that point to the data when it is needed. Budget: SB caps it at 94 lines
(ratcheted down only), EE/Katana at 1,500 words, NR at 1,200. "A new instruction goes in the file a
row names, never in this file."

**Binding rules stay inline; everything else is a pointer.** EE learned this the hard way (E-073,
J-090): the supply-chain rules were moved behind a pointer, an agent skipped the pointer. "A
pointer depends on being followed; text read on entry does not." NR states the test for what stays
inline: a rule an agent must obey *before it knows it is in the situation* (the worm indicator
list, "never touch what you did not start").

**theGhost.md, the decision log, with a test that holds its format.** Identical entry shape in all
four: `### X-nnn: title` then Decision / Why / Held by / Source / Status / See also / subject.
Statuses: proposed, in force, superseded by X-nnn, withdrawn, refused. Append only; a reversal is
a new entry and the old one names it, in the same commit. Source lines quote Ghost verbatim with a
date; that quote is the approval record. Each project has its own prefix (G-, R-, E-, NR's R-) and
a decision inherited from a sibling project points at the sibling's id rather than copying the
reasoning (EE "Lineage"). The test (GhostTest / test_ghost) checks ids unique and sequential,
supersession named on both sides, and no two in-force entries with the same subject carrying a
`conflicts-with:` line. The last check exists because SB once had two contradictory decisions both
in force (G-025 and G-124) and the test only checked syntax.

**Never read theGhost.md whole.** SB's is 400 KB, Katana's 1,500 lines; EE recorded (J-060) that
reading it up front costs more than it saves. All four generate `docs/decisions.md`, one line per
decision, and agents grep `### X-042`. Code cites decisions as `// Decision: X-042` on the line
above a function; Katana's WayBackTest checks the cited decision is in force.

**The journal, with fixed fields, kept identical across projects on purpose.** Who, Class, Intent,
Found, Options, Resolved, Touched, Caught by, Cost. Classes: contradiction, ambiguity,
failure-caught, failure-missed, decision, measurement, direction, trial, deferred, conflict. Written
in the same commit as the event, by whoever was there, newest last. "Not a restatement of the
commit log, not a status list, not the design." Katana split it into `docs/journal/J-x00-x99.md`
files behind a generated index after a 4,000-line file was read whole to find one entry (R-046);
the template should start split.

**TODO as a chain, DONE keeps the numbers, the roadmap shrinks.** Items are done in order; an item
that cannot be done as written stops the chain and goes to Ghost (EE E-016, Katana R-071, SB
G-151: "items put off are items buried"). Each item carries a `Check:` that fails before and passes
after. Finished items move to DONE.md with their numbers kept, because other documents cite them.
A built roadmap phase "shrinks to a ten-line header" (Katana P-06, NR P-06). SB generates a
`todo-index.md` with line numbers so agents `sed -n` the one item rather than reading a
1,900-line TODO.

**HANDOFF.md says what the next session should do and what waits on whom.** Sections converge on:
where the project stands (dated), starting a session cold, For Ghost (a numbered queue, phrased as
options plus a recommendation), For Fable, Trials (questions settled by a run, not an argument),
Waiting on a run, What to distrust. NR cut theirs from 2,082 to 1,105 words because "the file
agents grep first" had bloated (J-020); Katana archives finished sections verbatim to
`handoff-archive.md`. Katana's DuplicatesDocTest rejects any 200+ character paragraph pasted twice
in a first-read doc, after HANDOFF carried a 100-line section twice.

**The glossary enforces one word per concept.** `Term | Means | Not`; an alias in backticks is
enforced by a test and is added "the first time a test could have caught a real slip" (Katana).
NR's lesson J-006: enforce an alias only when it has no other honest use.

**Architecture as data a test enforces.** `docs/modules.json`: per module a purpose, `mayImport`,
`mustNotImport`, entry points; MOD-nn rules with sources; rendered to MODULES.md; a test refuses
any import not listed. A new module or a new cross-module import is a proposal that stops and waits
on Ghost (Katana R-043, NR J-025: "say you are waiting on Ghost, and stop"). A new file inside an
existing module is the agent's to add.

**Goldens define done for a refactor.** Byte-for-byte expected output, rewritten only behind an
explicit flag (`UPDATE_GOLDEN=1`, `-Dkatana.record=true`, `-PwriteGoldens`, `--decision R-nnn`)
with the diff reviewed line by line. "A refactor changes no output and is committed on its own,
first" (SB G-083): a refactor mixed with a change hides which one broke something. LF everywhere
(SB G-086: CRLF broke goldens on Windows). NR's refinement: the golden index holds each golden's
SHA-256 and the decision that last moved it, so a hand edit is caught by hash.

**Mutation testing, with every survivor killed or explained.** Stryker (SB), PIT (EE), mutmut
(NR). SB's origin story (G-239): a core file's tests caught 53% of mutants, then 97%; "tests that
test nothing are worse than none, because they are trusted." docs/MUTATION.md logs runs and lists
survivors with a one-line reason; a changed test is never weakened to pass. SB's weakened-test
detector (scripts/weakened.mjs) lists removed assertions, skip/only, and loosened matchers. NR adds
that a mutation to a *reported* number is never harmless.

**Every document that can drift has a test, and every test must reject a planted break.** EE's
`test/Check.java` pattern: each doc test holds the repository *and* rejects a deliberately broken
input, "so a check that stops catching anything is caught itself." NR writes each red condition as
a permanent test (J-011). Katana's R-056 makes independence *declared*: every check records its
oracle kind (tool, file, spec, self), its killer mutation, and what its verdict gates; a test task
that runs zero tests is red. All three of the Java/Python repos hit "I only changed documents" and
the doc tests were silently skipped (EE J-045, Katana J-006): build caching must be off for doc
tests.

**The tithe: one commit in eight, a pass per phase, gated not advised.** Started as SB's
observation (about a tenth of effort), then formalised: EE E-015, Katana R-008, NR R-012. The
commit changes no result and no golden; it improves routing rows, file sizes, names,
cross-references, stale docs, slow tests. Katana's J-154 is the reason it is a gate: the metrics
tool said "one is due" seventy-three times and stopped nothing; "a cadence that only warns is kept
while there is slack and dropped exactly when it is needed." Gate at 16 commits since the last
tithe (TitheGate), warning at 8. NR's tithe.md is the cleanest procedure: a "may change / may not
change" list ("a tithe that builds has overshot"), notes-as-product, hand back and commit nothing;
the reviewer reads the diff against the notes and pushes.

**The agent's environment is a first-class deliverable, measured and ratcheted.** docs/AGENT.md:
a contract (AGT-01..) plus a metrics table with one column per tithe pass. Shared metrics:
mandatory context words, fast loop seconds, largest source file, files per routing row, decisions
without See also, stale generated artifacts, docs lines per source line ("Suite Builder reached
0.37 and it hurt"; target 0.35). "A metric may improve; it never regresses without a decision." A
metric is "not armed" until first measured within target (Katana R-042/R-054, after the fast loop
doubled while it was only reported). "A limit is never raised to pass: make room." A ceiling below
the measured value "is red on every push and says nothing."

**Fresh Sonnet per task; Sonnet escalates to Opus after one attempt; Fable advises.** Formalised
in all four within the same week (SB G-282, EE E-060/E-064/E-068, Katana R-073/R-075/R-078, NR
R-022, J-027). The reason for fresh agents: a newcomer's trouble is the repository's trouble, and
a resumed agent at ~275k tokens missed three gaps a fresh one found (Katana). The escalation rule
made checkable: still red after one attempt and the output does not say why; then call Opus with
the task, the routing row, the diff and the failing output; Opus asks for a *replay of actions*
first ("I cannot remember" is fine; reasoning may be refused by safeguards), classifies the gap
(missing-row, not-read, wrong-instruction, no-replay, hard, conflict), logs it in ESCALATIONS.md;
three of one type is raised to Ghost for a routing pass. NR's J-032: an agent that could not
escalate spent 108 minutes on a metric no edit of its could fix, so "your hand-back is the
escalation." Opus reviews the diff, runs the gate, journals, pushes. Haiku is the context-budget
yardstick (SB G-242: "even Haiku can keep code in context and do piecemeal updates in one area")
and, in products, the pinned cheap scorer run three times and averaged (EE E-055, NR R-008).

**Navigation debriefs, reviewed for convergence.** NAVIGATION(-LOG/-NOTES).md: each agent ends
with Task, Opened (files, in order), Complaints, Suggestions; "nothing to say is an answer: write
none." Every ~10 commits (gate at 20 in Katana) Opus reads for what agents converge on ("the same
complaint from runs that did not see each other"), validates each item against the code, fixes
the valid ones, sends open questions to Fable, journals, wipes the entries (git keeps them). The
"Opened" list read against the routing row is the measure of navigability (NR R-023). Katana's
brief must end "finish as handoff.md says, then report", or the debrief gets missed.

**Conflict between agents: stop, assume objectives not sabotage, tell Ghost.** All four carry the
same rule from the same incident (EE E-066, NR J-023): three agents with conflicting objectives
overwrote each other and ran kill scripts against each other, each assuming sabotage. Never kill
a process, revert, force-push, stash, reset or checkout in a tree you did not start. SB adds:
never `pkill -f` (it killed its own check run), and a conflict stops work "at once, not after
three." One writer per working tree; an advising agent reads.

**Long output goes to a file, grepped for the verdict.** SB G-284, Katana R-076, NR J-021: the
gate's output in context crowds out the task. A sub-agent given a long run returns only the
failures. Every gate ends with one verdict line that the commit quotes.

**Commits authored as Ghost, several per session, main only, gated push.** `git config user.name
Ghost` / `118085043+ghost-in-the-kernel@users.noreply.github.com`; the agent keeps its
Co-Authored-By line. One branch (SB G-162: an open branch is forgotten by the next session). Push
gated and never `;`-chained (EE J-045 shipped a red commit). "Ghost reads the commit count as
velocity, so a session's work lands as several commits, each a deliverable that stands alone"
(NR). Messages cite decision and journal ids and quote Ghost's words with a date.

**The supply-chain baseline, verbatim, in CLAUDE.md, held by a test.** The seven bullets
(2026-10-19 baseline) are identical across repos; `test/SupplyChain*` plants a workflow, a hook,
a worm-named file, an unlocked import, and expects refusal. Lockfile-only installs, 7-day
cooldown on versions (SB G-256, NR R-018b), vendored jars hashed in third_party/MANIFEST.md,
actions pinned by SHA, `permissions: contents: read`, CI on dispatch only because minutes ran out.
NR went further: no CI at all, and a test fails if a workflow appears, because "a workflow with no
minutes is a check that cannot fail." Rule zero: "contain first, rotate last" (revoking a token
can fire a payload; destroys evidence).

**Scope fence.** SB G-252 / Katana SUPPLY-CHAIN: a security document must name whose repository
it is about, after an Opus agent assigned to Katana started working on Suite Builder. Every
security report opens "Applying security posture to: <project>"; agents confirm `git remote
get-url origin` first.

**Nothing proprietary, nothing a run produced, nothing a user gave, ever enters git.** SB G-085,
Katana R-037, EE E-014, NR "market data never enters this repository". `.gitignore` anchored (EE
J-023: an unanchored `runs/` silently dropped fixtures).

**Findings before claims.** A register (FINDINGS / DISCOVERIES / DIVERGENCES) with never-reused
ids, written *before* the result it qualifies, resolved entries marked not deleted. Katana's
claims are tagged verified or hypothesis; a question is settled by a source, then a trial, only
then by argument, and "the rivals are named first" (each candidate's predicted values written
before the run; SB's pre-registered experiments commit their SHA-256 into the decision). "Two
models arguing converge on the plausible, not the true; a run converges on the true."

**Writing register.** Third person, no real names, reviewers and sites named by letter (SB
G-087/G-100/G-102); "a document read years later should not depend on who 'we' was." Every rule
opens with a bold imperative clause and an id; metaphors only after the rule is stated plainly
(Katana ROADMAP 4.1). "No abstraction before its second use" (SB G-020). "Comments that restate
the code" are the one thing the philosophy does not ask for.

## 2. Where they diverged, and which form wins

| Topic | Earlier form | Later form | Winner for the template |
| --- | --- | --- | --- |
| CLAUDE.md task rows | SB: 25 task rows + 15 behaviour rows in one file (94 lines) | Katana R-074: CLAUDE.md names 6 *workpaths*; rows live in `docs/paths/<path>.md` | Katana's two-level routing for any project with more than ~12 rows; NR's flat table while it fits under 1,200 words. The template ships the flat table with a rule saying when to split. |
| Conditional-rule files | SB `docs/tasks/*.md` (task + behaviour mixed) | EE `docs/how/`, Katana `docs/when/` + `docs/paths/`, NR `docs/rules/` | `docs/when/` for situations, `docs/paths/` for workpaths. Katana's names say what they hold. |
| Intent on every function | SB G-088 labels on every function | SB G-105 retired them: caught four errors, all wrong labels, cost 25% of a task's tool calls; "the call graph is the one record of why a function exists that cannot drift" | `// Decision: X-nnn` only where a function holds a decision; `// Unsure:` for doubts; dead-code check (knip) so nothing floats. Katana's KERNEL-MAP (append-only function ledger) is a product feature of a compiler, not a template default. |
| Per-commit kernel log | SB G-092: a `Kernel-Log:` line gated every commit | SB G-106 retired the gate after two days once findings were acted on | A gate that costs every commit a line is run for a bounded stretch, then retired with a "what it showed" summary. The template ships the log format, not the gate. |
| Tithe enforcement | SB: periodic Ghost-initiated passes (kernel-log, trim, traversability) | EE/Katana/NR: 1-in-8 commit gate at 16, pass per phase, warn at 8 | Gate. Katana J-154. |
| Navigability trial | Katana fresh-agent trial per phase; Haiku 7-question trial | NR R-023 retired the trial: the trial agent grepped HANDOFF and found its own pass condition; the phase's real debriefs replaced it | Debriefs + review. Keep the trial design (R-020: pass condition kept out of every readable file, count reads by file not tool call) as an optional tool. |
| Context metric | SB G-242: token-counted working set (file + direct imports, comments excluded) with a 29,500-token budget and hub rule | EE/Katana/NR: words of mandatory context + lines per file + files per row | Lines and words for the template (language-neutral, cheap); SB's token working-set measure as an optional ratchet once a tokenizer is in the toolchain. |
| CI | SB/EE/Katana: dispatch-only, SHA-pinned, `contents: read` | NR: none, and a test refuses a workflow | Ship the SHA-pinned dispatch-only workflow *and* the local gate; the local gate is the definition of done either way (AGT-07 "the session is the machine"). Decision slot for the project. |
| Journal file | SB/EE/NR: one file | Katana: a file per hundred entries + generated index | Split from the first entry. |
| Decision prefix | G-, R-, E-, R- (NR reused Katana's letter) | | One unique letter per project, recorded in a cross-project lineage table in Ghost-Core so no two share one. |
| Vocabulary for intent | Paul's shorthand "intent directive" | Katana glossary: *Intent IR*, *fact*, *rule*, *review file*, *key*; "directive" is a listed non-word | The template's glossary ships Katana's terms. |

## 3. Lessons learned the hard way (the ones that should be rules from commit one)

- A check that cannot fail is not a check: compares a thing with itself, ran nothing and passed,
  always fails, its verdict stops nothing, or only warns (Katana lists five; NR adds "a metric with
  no dispersion and no trial count"). Independence is declared, not detected: a reimplemented
  oracle agrees with its twin on every shared mistake, which is why NR's mirror was written blind.
- Stryker's vitest runner silently tested nothing after its first pass; the first mutation scores
  were fake (SB G-290). The template's mutation setup includes a test that the runner catches a
  mutant it is known to catch.
- Pipes lose exit status (EE J-023): `set -euo pipefail`, every status checked, and the gate run
  against a known-broken commit once to prove it fails.
- Two sessions took the same decision number (Katana): `nextId` after `git fetch origin main`.
- `pgrep -f` for the gate's own name matches the waiting command (Katana J-258, an hour lost).
- Worktrees broke the fast loop (`.git` is a file there) (EE J-067); stryker temp files filled
  /tmp with 8,000 folders (SB); Windows CI minutes bill double and ran the account out (SB).
- Agents read silence literally: say explicitly what is allowed (NR J-025). Agents read every
  waiting item in full to learn it waited: a `Waits on:` line sends it to the bottom (SB G-292).
- A hook that asks for a commit is a token leak, not a nudge (SB, 2026-11-07, G-646 and G-363; Ghost's
  blurb of 2026-11-18): when only the gate could commit, every turn ended dirty and the end-of-turn hook
  fired about forty times a day, each firing a full re-read of the conversation at about $20. What fixed
  it, and what the template holds: save freely, gate only `main` (any agent commits and pushes its own
  session branch at any time with only the key scan first, so the hook has nothing to ask; when it does
  fire, pushing is the answer); `main` moves only after the gate passes, and the landing fast-forwards
  and pushes it in the same step, so `main` is never ahead of origin while a gate runs; Ghost as author
  and Claude as committer, which answered the hook's other complaint, an unverified commit; a long check
  runs in the background into a file, and nothing touches the tree meanwhile — workers' commits are held
  until a gate run finishes. The hook itself is never edited (the supply-chain rules): the fix is a
  working style under which it has nothing to say.
- Sessions reviewing their own work missed seven high-severity security findings (SB): a
  security-relevant change gets a blind second review by a fresh session of another model, given
  only the diff and the threat model, "never the author's reasoning."
- The founding documents of a new project contradicted each other three ways in the first week
  (NR J-006/J-007/J-032): counts kept in three files, a rule carried from a sibling project that
  contradicted a local decision. Derive every count from one source; doc tests before code.
- Measure the environment, don't assume it: NR probed network reachability at phase 0 and two
  sessions on the same day disagreed (J-008).
- Doc-shape tests (column widths) "cost more than they caught"; the path test "passes any true
  path under a false sentence", which led to proving recipes by mutation (SB).
- A rule with hundreds of exceptions is enforced by review, not by a test; demote it to a warning
  (SB G-107). "Ratchets, not exceptions": existing debt becomes a ceiling that only comes down;
  new code gets no entry (SB G-082).
- **Tithes get skipped unless they are concrete numbered roadmap items** (Ghost, 2026-10-23).
  A gate helps, but the thing that actually gets a tithe done is a TODO item with its own number
  and `Check:`, in the chain, so the chain stops on it. Every phase's last item is "Tithe pass N"
  with the steps spelled out, not "do a tithe".
- **A loosely defined tithe is punished harder than any other loose definition** (Ghost,
  2026-10-23). NR's J-033 is the example: the tithe agent "fixed" grep noise by deleting the
  mutation cache. The template's tithe rule must carry the "may change / may not change" lists,
  "a tithe that builds has overshot", and the hand-back-commit-nothing step from NR's tithe.md.
- **The tithe and the navigation review are one move, not two** (Ghost, 2026-10-23). Katana and
  NR run them on separate cadences (8 commits / 10 commits, two gates); the template merges them:
  the tithe item *is* the navigation review plus the fixes it found. Once a project matures, the
  navigation tune-up matters more than the code-shape work, because by then the files are already
  under 400 lines and the thing that rots is the routing. The metric that says which is due
  should be one counter, not two.
- **The gate's rule, in two clauses** (Ghost, 2026-10-23): a tithe commit is always accepted;
  any other commit is refused while a tithe is due. Not "warn at 8, refuse the push at 16": the
  refusal is at the commit, where the agent still has the context to do the tithe, and the only
  way through is the tithe itself. (Katana gated the push, so commits piled up locally past the
  limit and the gate fired on a batch.)
- **GitHub Actions minutes are a scarce resource, spent strategically** (Ghost, 2026-10-23). The
  evidence across the repos: SB ran the account out (Windows runners bill double), so SB, EE and
  Katana went dispatch-only and NR has no workflow at all. The template's rule: the local gate is
  the definition of done (AGT-07, "the session is the machine"); CI never runs on push or on a
  schedule; a workflow exists only for what the session cannot do (a second OS, a long matrix,
  a release) and is fired by hand, by Ghost's decision, with a journal line saying why the
  minutes were spent. Ubuntu only unless a decision says otherwise.
- **The kernel architecture is a declared DAG** (observed in all four, 2026-10-23): a
  `docs/modules.json` with per-module `mayImport` and a test that refuses any other import; one
  leaf module that holds the project's contract (numbers, types) that everything imports and that
  imports nothing (heuristics / rubric / profile / universe); one orchestrator (`project`) and a
  thin entry (`cli`) above it, kept separate so logic cannot hide in argument parsing; a new
  module or a new edge is a proposal for Ghost, a new file inside a module is the agent's.
- **Cloud-primary; nothing in the project may require Ghost's own hardware** (Ghost,
  2026-10-23). A step that only runs on the maintainer's machine endangers the project when that
  machine cannot handle it. Katana R-041 / EE E-039 / NR R-003 all say "cloud sessions only"; the
  template makes it a contract line (AGT): a clean clone builds and runs the fast loop and the
  gate in the session's container, with no local step anywhere in the recipes. A local run is an
  option a decision grants, never a requirement.
- **Names say what they hold, and the function-to-decision map is the intent mapping** (Ghost,
  2026-10-23). Suite Builder's naming rules (G-107: name a thing for what it holds; the glossary
  word, not an alias; `// Decision: G-nnn` above a function that stands on a decision; knip so
  nothing floats) are the template's naming rules. The map from theGhost.md to the functions that
  hold each decision is the intent map: a decision's `Held by` names the code, and the code's
  `// Decision:` names the decision, and a test (Katana's WayBackTest) checks both directions
  resolve and the cited decision is in force. SB tried labelling *every* function (G-088) and
  retired it (G-105); the map is only for functions that hold a decision.
- **The kernel contract: a doc with numbered invariants, the leaf module, and entry points**
  (observed in all four, 2026-10-23). SB SUITE-IR/HEURISTICS, Katana INT-/LANE-/LED-/PROOF-nn, EE
  SCORE-CARD SC-nn, NR HARNESS HAR-nn: the contract precedes the code ("not precise enough to
  implement is a defect in the document, not a reason to read the code", NR); ids are never
  reused; code cites `// Invariant: XX-nn`; one doc test per contract holds doc and code equal in
  both directions and rejects a planted break. The leaf module holds the contract's types and
  numbers; `modules.json` lists each module's `entryPoints`, the only names another module may
  call, and each `mayImport` edge carries its `why` (SB).
- The philosophy document should name *this project's* ghost: Katana's is authors gone for
  decades, NR's is "the forgotten search", EE's is turnover. The template leaves that section as a
  slot with the three as examples.

## 4. The template inherits, in one line each

From Suite Builder: the pointer CLAUDE.md, the behaviours index, task files with `Caught by`,
goldens, mutation, ratchets, the kernel log format, trim/traversability/hostile review formats,
the weakened-test detector, the security posture and manifest lock, pre-registered experiments.
From Katana: workpaths and `docs/when/`, the journal split and index, fixed-field registers with
never-reused ids, the check doctrine (oracle/killer/gates), claims and trials, TitheGate and
NavigationGate, `nextId`, the pinned offline image, the question classes (agent's, trial's,
Fable's, Ghost's). From Employee Evaluator: the doc-test-with-planted-break pattern (`Check`),
FOR-GHOST.md as the human-only queue, the decision lineage table, Haiku ×3 judging, the armed
metric. From Neon Rain: the "When X, read Y" wording, `docs/rules/` with "Read this when… / Why:
J-nnn", the tithe procedure, the escalation rule made checkable, the navigation log header, "the
tests are the audit" readability rules for a language the maintainer cannot audit by eye, the
golden index with hashes and `changed_by`, the trials file, and the sharpest statement of the
philosophy for agents ("On enlightenment").
