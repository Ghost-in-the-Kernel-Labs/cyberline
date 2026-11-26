# A long run: the gate, mutation testing, anything that prints pages (C-019)

Read this when you start a run whose output is long, or one that may outlive your next call.

## The output

- Run the gate as it is, `scripts/gate.sh`: it prints one `== <step>: passed (N s)` line per step
  and its verdict last, and writes every step's output to build/gate.log and each step's seconds to
  build/gate-times.txt (C-037).
- Send anything else long to a file: `mkdir -p build; <command> > build/<name>.log 2>&1`.
- Read the verdict first and the log only when it refuses:
  `grep -E "FAILED|Error|refused" build/gate.log`.
- The gate's verdict is its last line, `gate: passed …` or `gate: refused at …`; a cold run's begins
  `gate (cold):` and logs to build/gate-cold.log (`docs/when/tune-up.md` step 2).
- A worker you start does the same and reports only the verdict and the failures.
- Never chain the commit or the ship to the gate with `;`: the commit refuses a tree the gate did
  not record, and the ship (`scripts/ship.sh`) a HEAD whose tree is not the record.

## The waiting recipe

1. Start the run detached from the first call, never in the foreground of a tool with a time limit:
   the harness's background run, or

       mkdir -p build; setsid nohup scripts/gate.sh > build/gate-run.log 2>&1 < /dev/null &

   (the gate's own log is build/gate.log, so its terminal lines go to another name).
2. Wait with one bounded loop, its ceiling under your tool's own limit; repeat the call while the
   run lives:

       timeout 540 bash -c 'until grep -q "^gate:" build/gate-run.log; do sleep 30; done'

   A cold run's line is `gate (cold):`, so grep `^gate (cold):` for it. A bare `sleep` is not a wait.
3. Never find your run by `pgrep -f` with words from your own command: the pattern matches the
   shell that runs it. Read the log, or `kill -0` a PID you saved.
4. A log with no verdict line is a cut-off run, not a pass: run it again.
5. Wait silently: no turn that only says the run is still going.

## The machine

The session is the machine (AGT-07); `docs/AGENT.md` "The machine" holds its measured cores and memory.

- A background task lives at most two hours; a run that may take longer is cut into pieces.
- An idle container is reclaimed within minutes, `nohup` or not: a live background task keeps the
  session, a scheduled check-in does not.
- A restart kills every process, so a long run checkpoints after each unit and resumes from the
  last one.
- After a restart, warm the caches by running once; never raise a limit or a timeout for the
  restart's cold start.
- Start a gate only when the load is low: `uptime` below the core count (`nproc`).
- One gate per clone: the lock is .git/ghost/lock, and a second gate refuses at once.

## Why

A long check's output in context crowded out the task; a sub-agent sending it to a file fixed it
(Suite Builder G-284). Two full checks run side by side on one machine failed tests that pass alone,
and Ghost said to stagger them (SB G-307: one check per computer). Five checks failed on their first
run after a container restart, on timeouts that passed warm; the caches are warmed once and no limit
is raised (SB G-325). Katana's long-run recipe starts a long command in the background from its first
call (J-322), waits in one bounded `until grep`, and refuses `pgrep -f` of a name in the waiting
command's own line, which once matched itself and lost an hour (J-258). Neon Rain lost a 3.3-hour run
at a background task's two-hour limit, when its idle container was reclaimed, and made the run resume
horizon by horizon (J-081; its `docs/AGENT.md` "The machine"). Employee Evaluator's pre-push failed one
test in ten runs and deleted its clone, so the failing test's name was lost (J-139): a run's output is
kept in a file. AI Slop Block ran its cache-off gates detached and polled (J-051). A `;`-chained push
once sent a red commit to `main` (EE J-045); the tree record is what binds now (C-037).
