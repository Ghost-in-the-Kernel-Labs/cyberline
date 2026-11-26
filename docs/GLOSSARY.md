# Glossary: one word per concept

The canonical word for each concept, what it means, and the words *not* to write. An alias in
backticks is enforced: `test/test_glossary.py` fails when it appears in a document outside this
file. An alias without backticks is a review guide. Enforce an alias only when it has no other honest
use in the repository: "model" is both a Claude model and a project's model of its domain, and a
test cannot tell the uses apart. Add a term before using a new word for a concept (C-011).

Not governed: `docs/LESSONS.md`, `docs/LINEAGE.md`.
They quote the parents in the parents' words.

A project stamped from this template keeps every row here and adds its own below them; a row it
removes is a decision in its own log.

| Term | Means | Not |
| --- | --- | --- |
| **Ghost** | the maintainer, in every file, comment and commit (C-030) | the author's legal name, "we", "I" |
| **ghost** (lower case) | the intent a codebase was built with; what is lost when nobody can say why | spirit, spec |
| **kernel** | the codebase, and the leaf module that holds a project's contract in code | core (the core is Ghost-Core), engine |
| **agent** | a Claude session doing a task in the repository | assistant, bot, AI (alone) |
| **decision** | one numbered entry of `theGhost.md`: what, why, held by, source, status (C-008) | ADR, rule (a rule is what a decision may be held by), policy |
| **contract** | a document of numbered invariants the code is held to in both directions, and the leaf module that holds its types and numbers | spec, interface (a language's word), schema |
| **invariant** | one numbered line of a contract, `XX-nn`, never reused | rule, constraint, assertion |
| **leaf module** | the module every other module imports and that imports nothing: the contract in code | core module, common, `utils` |
| **entry point** | a name in `docs/modules.json` that another module may call; the only such names | public API, export |
| **routing row** | one line of CLAUDE.md's table: a task, the two to five files to open first, its contract, its tests (C-020) | task row, index entry |
| **workpath** | one area of work with its own file of routing rows, named in CLAUDE.md when the table outgrows it | module (a module is code), section |
| **when file** | a file under `docs/when/` read at the moment its situation arises and not before (C-021) | skill (Claude Code's own word for its packaged instructions), `rule file`, `trigger file` |
| **mandatory context** | CLAUDE.md plus whatever an agent must read before any task, in words, under its ceiling (C-022) | prompt, system prompt, preamble |
| **fast loop** | the tests an agent runs after every edit: doc checks and unit tests, no data, no network, under its ceiling | quick tests, smoke tests (a smoke test is an integration test's first form) |
| **gate** | the script whose verdict stops an action: `scripts/gate.sh` before a push, `scripts/commit.sh` before a commit | hook (an agent never installs one), CI (CI is spent by hand, C-032), precommit |
| **check** | one of `scripts/checks/`: reads the repository, returns a list of problems, empty when clean; its test rejects a planted break (C-013) | `validator`, `linter` (a linter is a stack's tool, run by the gate), audit |
| **planted break** | a deliberately broken input a check's test must reject, kept under `test/fixtures/broken/` | negative test, bad example |
| **golden** | expected output compared byte for byte, rewritten only behind a flag and a reviewed diff (C-017) | snapshot, fixture (a fixture is input), expected file |
| **fixture** | an input a test or a golden is computed from | golden (that is output), sample, test data |
| **refactor** | code moved or split with nothing it does changed: every golden identical, committed on its own (C-017) | `cleanup`, rewrite, tidy |
| **tune-up** | one commit, or the pass that closes a phase, that changes no result and improves the agent's environment: misses noted, the metrics re-measured, a stamp walked (a pass, where the project stamps others), the navigation review and the fixes it found (C-024, `docs/when/tune-up.md`) | tithe (the parents' word for the code-shape half, kept in quotations), `tithe pass`, `cleanup`, refactor (a refactor changes code shape; a tune-up may not) |
| **navigation review** | step 4 of a tune-up: reading the debriefs for what agents who did not see each other converge on (C-025) | retrospective, nav review |
| **debrief** | an agent's entry in `docs/NAVIGATION-LOG.md` after a task: what it opened, in order; complaints; suggestions | feedback, retro, postmortem (a postmortem is a journal entry of class failure-missed) |
| **journal** | `docs/journal/`, what happened while the work was done, in fixed fields, by whoever was there (C-015) | log (a log is a tool's output), changelog, diary |
| **finding** | an entry of `docs/FINDINGS.md`: a flaw the project's checks prove, with its proof, written before the result it qualifies (C-014) | bug (a bug is in this codebase; a finding is about the input or another tool), issue, caveat |
| **escalation** | a worker's hand-off of a hard fix to the next grade up, logged by kind (C-027, C-028, C-036) | retry, help request |
| **grade** | the size of agent a task is placed at: small, mid or strong, each one model in `docs/when/grades.md`, which no other instruction names; and the ruling grade above them (C-036) | `tier` (AI Slop Block's product word), level, model (a model is what a grade maps to) |
| **floor grade** | the lowest grade a project places any work at, the `Floor:` line of `docs/when/grades.md`: strong in Ghost-Core, mid by default in a stamped project (C-036) | minimum grade, base level |
| **ruling grade** | the grade above strong: takes no items, answers questions, which go to it first and to Ghost last (C-036) | arbiter, judge |
| **brief** | the one page a task is handed out with: the objective and its pass line, the working set, the grade and its stop limits, the never-rules, the commit mode, the report wanted (`docs/when/hand-out-a-task.md`, C-036) | prompt (a prompt is anything sent to a model), ticket, assignment |
| **report** | the one page a worker hands back: what was asked, the commits, what was tried and its failing output, the files read, the tool calls, the tokens or `not reported`, the choices left for Ghost (C-036) | summary, transcript (the next grade starts from the report and the diff, never a transcript), status update |
| **worker** | an agent another agent started for one task: briefed with a brief, handing back a report (`docs/when/hand-out-a-task.md`, C-036) | sub-agent, subagent (Claude Code's own words for what its Agent tool starts), helper |
| **coordinator** | the strong-grade agent that places items, writes briefs, starts workers and works from their reports, and stays small (`docs/when/coordinate.md`, C-036) | orchestrator, manager, lead agent |
| **Context Canary** | the two words every reply starts with: a reply without them says CLAUDE.md has slipped from view (C-036) | canary token (a security word), heartbeat |
| **conflict** | another agent's work breaking yours, contradicting your task, or changing what you changed; stop, both objectives to Ghost (C-029) | merge conflict (git's word; a merge conflict is resolved by the one who fetched), race, sabotage (never assumed) |
| **claim** | a statement tagged verified or hypothesis; settled by a source, then a trial, only then by argument (C-004) | assumption, belief, fact (a fact is a confirmed claim) |
| **trial** | a run that settles a claim, with the rivals and the pass condition written before it (C-004) | experiment (a pre-registered experiment is a trial's form), test (a test is in the fast loop), spike |
| **fact** | in an intent map: one thing inferred about the code, with evidence, a confidence and a state: inferred, confirmed or refuted (C-005) | annotation, hint, directive (unenforced: a directive is also Ghost's standing instruction, as in the supply-chain directive) |
| **ratchet** | a limit that may come down and never go up; existing debt becomes its ceiling, new code gets no entry (C-023) | threshold (a threshold is a heuristic's number), quota |
| **armed** | a metric first measured within its target, from which point it may never regress without a decision (C-023) | enabled, active |
| **oracle** | the independent source a check's expected side comes from, built and frozen before the thing it checks (C-003) | reference implementation (an oracle may be one; the word says it is independent), ground truth |
| **mirror** | a reimplementation of a contract written blind, from the contract text alone, by an agent that has not seen the code; compared to the code by a test | shadow, clone, copy |
| **stamp** | to create a new project from this template: `README.md`'s recipe | fork (git's word), clone (git's word), instantiate |
| **parent** | one of the four projects Ghost-Core is distilled from (`docs/LINEAGE.md`) | upstream, ancestor, source project |
| **Unsure line** | `// Unsure: <why>; settled by <what>` above code the writer could not be certain of; listed by the metrics, failed on by nothing | TODO (a TODO is an item in TODO.md), FIXME, question |
| **patch reviewer** | the agent that reads one dependency update's diff with Read, Grep and Glob and nothing else: read-only by construction (C-035) | security reviewer, approver (its SAFE approves nothing alone), auditor |
| **reviewed version** | the last version of a package the project read in full, in `docs/REVIEWED-VERSIONS.md`; the next review's old side | last installed version (the diff is read from the reviewed one, not the installed one) |
| **routine update** | a patch or minor of a package the project already has that passes every layer; taken without asking Ghost (C-035) | minor bump, auto-update |
