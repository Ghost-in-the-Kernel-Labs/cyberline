# Workpath: process (a decision, the plan, the journal, metrics, the routing, the supply chain)

The one workpath every project has. Rows: a task, the two to five files to open first and nothing
else yet, the contract to read, the tests to run before and after. A new row goes here, never in
CLAUDE.md. A project adds its own workpaths beside this one (`docs/paths/<name>.md`) and names each
in CLAUDE.md's workpath table when the routing table outgrows the word ceiling.

| Task | Start here | Contract | Tests |
| --- | --- | --- | --- |
| A decision: propose, record, supersede | `theGhost.md` (its header), `docs/decisions.md` | C-008; who may write: the header; a new file a Held by names is staged (`git add -N`) before the fast loop, which reads git's list, and a Core-only file is named there in plain text (the pointer row below) | `test/test_ghost.py` |
| The plan: what to work on; finishing a step | `docs/HANDOFF.md`, `TODO.md` (the first open item), `docs/ROADMAP.md` §6; to add items before an open tune-up pass, renumber the pass to the phase's end; an item whose Check earlier commits already meet is closed with the evidence named in its journal entry, not rebuilt (as Ghost-Core's 1.3 became 1.5, then 1.23, then 1.24); an item that waits on something outside the repository moves to the waiting phase (`TODO.md`'s header); an open question a later item depends on is copied into that item's text | C-016 | `test/test_todo.py` |
| Writing down what happened | `docs/JOURNAL.md`, the newest `docs/journal/J-*.md` (its end) | C-015 | `test/test_journal.py` |
| A word | `docs/GLOSSARY.md` | C-011 | `test/test_glossary.py` |
| Why a rule is what it is | `docs/GHOST-IN-THE-KERNEL.md`, `docs/LESSONS.md` | | |
| A finding, an escalation | `docs/FINDINGS.md`, `docs/ESCALATIONS.md` | C-014, C-028 | `test/test_registers.py` |
| The agent's environment: the metrics | `docs/AGENT.md`, `scripts/metrics.py` | AGT-01 to AGT-08 | `test/test_metrics.py` |
| A routing row, a when line, a pointer | `CLAUDE.md`, `docs/paths/process.md` (this file), `docs/when/*.md` | C-020, C-021; a pointer to a file not yet written is allowed only while an open TODO item names that file in its check; a parent's file, a Core-only file or a file a core decision merely promises is named in plain text, since a stamped project inherits the document and the decision but not the item or the file (`scripts/checks/pointers.py`'s docstring) | `test/test_claude_md.py`, `test/test_pointers.py` |
| A test of the kernel contract or the leaf in this repository | `docs/modules.json` (in a stamped project, the real folders once TODO 0.4 sets them; in Ghost-Core, a template with no `src/` and no leaf folder, a leaf assertion reads the map and is proven on a fixture, never on the tree, and the stamped fast loop the gate runs is where a real-tree assumption shows) | C-012 | `test/test_contract.py`, `test/test_modules.py` |
| A document's check: what it holds | `scripts/checks/<check>.py`, `test/test_<check>.py` | the check's docstring; one planted break under `test/fixtures/broken/<check>/`; a check reads its files through `scripts/checks/common.py` (`tracked_files`: git's list, never the disk, so a file a clone would not hold is not read; C-001) | that test |
| The supply chain: a config, a workflow, a hook; the secret scan and its allow list; the auto-execution surfaces inventory and the commit check (C-039) | `docs/SUPPLY-CHAIN.md`, CLAUDE.md's binding rules, `scripts/checks/secrets.py`, `docs/secret-allow.txt` | C-034, C-037, C-038 | `test/test_supply_chain.py`, `test/test_secrets.py` |
| A dependency: add, update or remove one | `docs/when/dependency-update.md`, `docs/DEPENDENCY-REVIEW.md`, `docs/REVIEWED-VERSIONS.md` | C-035 | `test/test_review_scan.py`, `test/test_reviewed_versions.py`, `test/test_patch_reviewer.py` |
| The gates: the three checkpoints (C-040: a save is scanned, `scripts/save.sh`; a landing passes the fast checks, `scripts/gate.sh --fast`; a release passes the full gate), the tree record (the gate writes the SHA of the tree it passed on to .git/ghost/tree and its kind, `fast` or `full`, to .git/ghost/kind, read by `scripts/checks/gate_record.py`), the lock (.git/ghost/lock, one gate per clone), the gated commit (its steps and refusals: `scripts/commit.sh`'s header; the tune-up count on `main`'s first-parent line only), the ship; a red step's `FAIL:`/`ERROR:` names on the terminal before the verdict, and build/gate.log never deleted. Suite selection, for a stack whose full gate exceeds its ceiling (Katana R-097): the gate runs the suites the changed paths select, by a map from path prefixes to suites kept in code, never in a person's head; a path the map does not name selects every suite, so a new folder costs time and never coverage; a table test holds the map (each row a path and the suites it must select, an unmapped path among them); and the full gate still runs at every tune-up, so nothing the map misses goes unrun for longer than eight commits | `scripts/gate.sh`, `scripts/save.sh`, `scripts/commit.sh`, `scripts/ship.sh`, `scripts/checks/gate_record.py` | C-024, C-032, C-037, C-040 | `test/test_gates.py`, `test/test_fast_checks.py`, `test/test_save.py`, `test/test_ship.py` |
| The score: an item placed at a grade from facts; the points it reads | `scripts/score.py`, `docs/when/grades.md` | C-036 | `test/test_score.py` |
| Any Python under `scripts/` or `test/`: the readability rules every function is held to | `test/test_readability.py` (a function at most 39 lines; a docstring on every function and test helper, with a concrete example where the result is not plain from the name (asked, not checked); no `*args` or `**kwargs`; small comprehensions) | | `test/test_readability.py` |

## The order of a step

Research (what the item needs, read against its check), build, the fast loop, the journal entry
(then `python3 -I scripts/journal_index.py` and `python3 -I scripts/metrics.py --write`, the two
generated files it changes), the debrief, the save (`scripts/save.sh -m <message>` on a session branch: the key
scan, a plain commit as Ghost, the branch pushed; on `main` itself there is nothing to save, so the step is skipped
there), the fast checks (`scripts/gate.sh --fast`: the fast loop, the key scan, each present stack's fast checks; it
records the tree), the commit through `scripts/commit.sh -a -F <message>` (it stages, scans, runs the fast loop and
refuses a tree the gate did not record, C-037, C-040; a fast record adds the trailer `Gate: fast checks`; a change
wholly under `docs/` may add `--docs-only`, which skips the record and adds the trailer `Gate: fast loop only`, the
one path open in a stamped project before its stack's gate is wired), the ship (`scripts/ship.sh`, the only
`git push` to `main`: it fetches `main` and refuses a HEAD whose tree is not the record or that is not a
fast-forward; the save's push goes to the session's branch, never `main`). In short: research, build, fast loop,
journal, debrief, save, fast checks, commit, ship. The full gate (`scripts/gate.sh`, the slow tests, every stack's
gate, the metrics) is the release checkpoint, run at each tune-up pass and before a real project is stamped; a failure
it finds after a landing is a fix-forward item, never a blocked commit (C-040). One test alone (the `-m unittest test.test_x` form cannot import under `-I`):
`python3 -I -m unittest discover -s test -t . -p 'test_x.py'`. A finished step is merged
to `main` at once (C-031). A step too large for one ship is built in slices,
each tested and shipped on its own, each a commit that stands alone (C-030).
