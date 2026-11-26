#!/usr/bin/env bash
# The gate: the check before a landing, the definition of done (C-032, C-037, C-040, AGT-07). There is no CI on push.
# It runs every step on the working tree as it stands, never on a commit. In order: the fast loop (timed), the key scan
# over the tree's changes, the slow tests, each stack's own gate where a stack is present, the generated files, the
# metrics.
# The fast checks: `scripts/gate.sh --fast` is the landing checkpoint (C-040): the fast loop, the key scan, each present
# stack's fast checks (its gate.sh run with --fast) and the generated files, no slow tests, no stack gate, no metrics; it
# records the tree as the full gate does, and `.git/ghost/kind` says `fast`, which scripts/commit.sh turns into the
# trailer `Gate: fast checks`. Its verdict line begins `gate (fast):`, its log is build/gate-fast.log and its times
# build/gate-fast-times.txt, so the full gate's files stay. The full gate is the release checkpoint: each tune-up pass
# (the two-run rule, docs/when/tune-up.md) and before a real project is stamped.
# The terminal shows only `== <step>: passed (N s)` per step and one verdict line last, `gate: passed …` or
# `gate: refused at …`; every step's output goes to build/gate.log, each step's seconds to build/gate-times.txt
# (below), so run it as it is: `scripts/gate.sh` (docs/when/long-run.md).
# build/gate-times.txt: one line per step run, in run order, `<seconds> <step>` (seconds to two decimals, the step's
# name as its `==` line gives it: `11.70 the fast loop`); a refused run's file ends at the step that refused. A
# tune-up reads it to report step times without rerunning the gate (docs/when/tune-up.md step 2).
# The tree record names its kind: .git/ghost/kind holds `full` or `fast`, written beside the tree, removed with it.
# The cold run: `GHOST_COLD=1 scripts/gate.sh` bypasses every cache a step keeps. Core's own steps keep none; the
# variable is exported to the stack gates (the TypeScript stack's mutate.mjs reads it as MUTATE_CACHE=0) and `--cold`
# is passed to scripts/metrics.py, which never writes a cold run's numbers to docs/AGENT.md. Its verdict line begins
# `gate (cold):`, its output goes to build/gate-cold.log and its times to build/gate-cold-times.txt, so the warm run's
# files stay; its minutes go to the journal's Cost line and the tune-up commit's verdict line only (C-024).
# The tree record: when every step passed and the tree did not change during the run, the SHA of that tree
# (scripts/checks/gate_record.py --tree, taken before the first step and after the last) goes to .git/ghost/tree, never
# committed; a red, interrupted or changed run writes none, and the record of an earlier run is removed at the start.
# One gate per clone: the lock is the folder .git/ghost/lock, made by mkdir and removed on exit, red or green.
# A red step names its failures: before the verdict the terminal gets the step's `FAIL:` and `ERROR:` lines from the log
# (unittest's test names; at most 40, then a count of the rest), so a failure that shows once in ten runs keeps its name
# (EE lost one). Nothing deletes the log: a red run leaves build/gate.log whole, and only the next run empties it.
set -uo pipefail
cd "$(dirname "$0")/.."
started=$(date +%s)
log=build/gate.log
times=build/gate-times.txt
cold=
fast=
kind=full
for arg in "$@"; do
  case "$arg" in
    --fast) fast=1; kind=fast; log=build/gate-fast.log; times=build/gate-fast-times.txt;;
    *) echo "gate: refused at the arguments (unknown argument $arg; usage: scripts/gate.sh [--fast])"; exit 1;;
  esac
done
if [ "${GHOST_COLD:-}" = 1 ]; then
  [ -z "$fast" ] || { echo "gate: refused at the arguments (the cold run is the full gate's: GHOST_COLD=1 scripts/gate.sh)"; exit 1; }
  cold=--cold; log=build/gate-cold.log; times=build/gate-cold-times.txt
fi
export GHOST_COLD
# verdict <line>: printed and logged; a cold run's begins `gate (cold):`, the fast checks' `gate (fast):`, in place of `gate:`.
verdict() {
  local line=$1
  [ -z "$cold" ] || line="gate (cold):${line#gate:}"
  [ -z "$fast" ] || line="gate (fast):${line#gate:}"
  echo "$line"; echo "$line" >> "$log"
}
stop() { verdict "gate: refused at $1"; exit 1; }

git_dir=$(git rev-parse --git-dir 2>/dev/null) || { echo "gate: refused at the lock (not a git repository: the record lives in .git/ghost)"; exit 1; }
ghost="$git_dir/ghost"
mkdir -p "$ghost" build
if ! mkdir "$ghost/lock" 2>/dev/null; then
  echo "gate: refused at the lock ($ghost/lock is held: another gate runs in this clone, or one was killed; remove the folder once none runs)"
  exit 1
fi
trap 'rm -rf "$ghost/lock"' EXIT
trap 'exit 130' INT TERM
rm -f "$ghost/tree" "$ghost/kind"
: > "$log"
: > "$times"
git check-ignore -q "$log" || stop "the log (git does not ignore build/, so the gate's own log would change the tree)"

tree() { python3 -I scripts/checks/gate_record.py --tree 2>> "$log"; }
# key_scan: every change the tree holds against HEAD, untracked files included, through scripts/checks/secrets.py --diff;
# a finding is a fingerprint, never a value. A temporary index, so the real one is left as it was.
key_scan() {
  local index base status
  index=$(mktemp)
  cp "$(git rev-parse --git-path index)" "$index" 2>/dev/null || rm -f "$index"
  base=$(git rev-parse -q --verify HEAD) || base=$(git hash-object -t tree /dev/null)
  GIT_INDEX_FILE=$index git add -A && GIT_INDEX_FILE=$index git diff --cached --no-color --no-ext-diff "$base" | python3 -I scripts/checks/secrets.py --diff
  status=$?
  rm -f "$index"
  return "$status"
}
# failures <line>: the FAIL:/ERROR: lines of the log from that line on, at most 40, then how many more there are.
failures() {
  local names count
  names=$(tail -n "+$1" "$log" | grep -E '^(FAIL|ERROR): ') || return 0
  count=$(printf '%s\n' "$names" | wc -l)
  printf '%s\n' "$names" | head -40
  [ "$count" -le 40 ] || echo "... $((count - 40)) more in $log"
}
seconds_since() { awk -v a="$1" -v b="$(date +%s.%N)" 'BEGIN { printf "%.2f", b - a }'; }

# step <name> <refusal> <command…>: the command's output to the log, its seconds to the times file and the terminal.
step() {
  local name=$1 refusal=$2 begun secs first
  shift 2
  begun=$(date +%s.%N)
  echo "== $name" >> "$log"
  first=$(wc -l < "$log")
  "$@" >> "$log" 2>&1
  local status=$?
  secs=$(seconds_since "$begun")
  echo "$secs $name" >> "$times"
  [ "$status" -eq 0 ] || { failures "$first"; stop "$refusal"; }
  echo "== $name: passed ($secs s)"
}

before=$(tree) || stop "the record (git write-tree failed before the first step: build/gate.log)"

step "the fast loop" "the fast loop" scripts/fast.sh
fast_loop=$(awk '$0 ~ / the fast loop$/ { print $1 }' "$times")
step "the key scan" "the key scan (a secret in the tree's changes: build/gate.log names its fingerprint)" key_scan

# The stamp (scripts/stamp_text.py, drop_stamp_gate) deletes the next line by its text: a stamped project has no test_stamp.

for stack in stacks/*/gate.sh; do
  [ -f "$stack" ] || continue
  dir=$(dirname "$stack")
  name=$(basename "$dir")
  [ -f "$dir/PRESENT" ] || continue
  if [ -n "$fast" ]; then step "the $name stack's fast checks" "the $name stack's fast checks" bash "$stack" --fast
  else step "the $name stack's gate" "the $name stack's gate" bash "$stack"; fi
done

step "docs/decisions.md" "a stale docs/decisions.md" python3 -I scripts/decisions_index.py --check
step "docs/journal/INDEX.md" "a stale docs/journal/INDEX.md" python3 -I scripts/journal_index.py --check

gate_minutes=$(awk -v a="$started" -v b="$(date +%s)" 'BEGIN { printf "%.2f", (b - a) / 60 }')
[ -n "$fast" ] || step "the metrics" "a metric that regressed" python3 -I scripts/metrics.py --fast-loop "$fast_loop" --gate "$gate_minutes" $cold

after=$(tree) || stop "the record (git write-tree failed after the last step: build/gate.log)"
[ "$before" = "$after" ] || stop "the record (the tree changed while the gate ran: nothing recorded; run it again)"
echo "$after" > "$ghost/tree"
echo "$kind" > "$ghost/kind"

# The count is main's first-parent line only (C-040): a session branch's saves are not landings.
line=$(git rev-parse -q --verify refs/heads/main >/dev/null && echo refs/heads/main || echo HEAD)
count=$(git log --first-parent --format='%s' "$line" 2>/dev/null | awk 'BEGIN{n=0} /^tune-up:/ || /^stamped from/ {exit} {n++} END{print n}')
verdict "gate: passed; fast loop ${fast_loop}s, ${gate_minutes} min, $count commits since the last tune-up"
