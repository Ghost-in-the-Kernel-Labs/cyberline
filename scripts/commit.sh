#!/usr/bin/env bash
# The gated commit (C-037, C-024, C-040): the landing, the only way a commit reaches `main` (a session's checkpoints on
# its own branch are scripts/save.sh, which never lands). In order, each refusal one line naming its step:
#   1. stage: the paths given, or everything (-a or -A); refused when nothing is staged
#   2. the secret scan over the staged diff (scripts/checks/secrets.py --diff)
#   3. the commit check (C-039): a staged change to an auto-execution surface (scripts/*.sh, a stack's gate.sh, an agent
#      file, a workflow: docs/SUPPLY-CHAIN.md's inventory) is refused unless the message names a decision id, so every
#      change to the gate is a recorded one; nothing is pinned to a hash
#   4. the tune-up rule (C-024): refused while a tune-up is due, eight or more commits on `main`'s first-parent line since
#      the last `tune-up:` one or, when newer, a stamped project's founding commit (its subject starts "stamped from"),
#      counted from and not toward (C-040: a session branch's saves are not landings and are never counted); a
#      `tune-up:` subject always passes. A line `Tune-up deferred through <sha>` in docs/HANDOFF.md, written only on Ghost's
#      word, moves the count's start to that commit when it is newer than the last tune-up
#   5. the fast loop (scripts/fast.sh)
#   6. the record: the staged tree must be the tree scripts/gate.sh passed on (.git/ghost/tree): the fast checks
#      (`scripts/gate.sh --fast`, the landing checkpoint, C-040) or the full gate; a fast record (.git/ghost/kind says
#      `fast`) adds the trailer `Gate: fast checks` to the message. With --docs-only (or GHOST_GATE=skip) and every
#      staged path under docs/, the record is not compared and the message gets the trailer `Gate: fast loop only`
#   7. the secret scan again, and the staged tree unchanged since step 6
#   8. the commit: `git commit-tree` of the recorded tree on the parent HEAD named at step 1, author Ghost and committer
#      Claude, then `git update-ref` from that parent, so a HEAD that moved meanwhile refuses it; never `git commit`
# Usage: scripts/commit.sh [-a | <paths>…] -F file | -m msg [--docs-only]     (-F - reads the message from stdin)
# A refusal leaves the index as it was before the script ran; the working tree is never touched. Never a git hook: an agent
# never installs one (C-034), and nothing checks a commit after it exists (C-037).
set -uo pipefail
cd "$(dirname "$0")/.."
TUNE_UP_EVERY=${TUNE_UP_EVERY:-8}
AUTHOR_NAME=Ghost
AUTHOR_EMAIL=118085043+ghost-in-the-kernel@users.noreply.github.com
COMMITTER_NAME=Claude
COMMITTER_EMAIL=noreply@anthropic.com
USAGE="usage: scripts/commit.sh [-a | <paths>…] -F file | -m msg [--docs-only]"

scratch=$(mktemp -d)
saved_index=""
committed=""
cleanup() {
  # A refusal puts the index back as the caller left it; a commit leaves it synced to the new HEAD.
  if [ -z "$committed" ] && [ -n "$saved_index" ]; then cp "$scratch/index" "$saved_index"; fi
  rm -rf "$scratch"
}
trap cleanup EXIT
refuse() { echo "commit: refused at $1"; exit 1; }

# The arguments: -a/-A or paths, one message, --docs-only.
all="" docs_only="" message="" paths=()
while [ "$#" -gt 0 ]; do
  case "$1" in
    -a|-A) all=1;;
    --docs-only) docs_only=1;;
    -m) [ "$#" -ge 2 ] && [ -z "$message" ] || refuse "the arguments ($USAGE)"; printf '%s\n' "$2" > "$scratch/message"; message=1; shift;;
    -F|--file)
      [ "$#" -ge 2 ] && [ -z "$message" ] || refuse "the arguments ($USAGE)"
      if [ "$2" = "-" ]; then cat > "$scratch/message"; else cat -- "$2" > "$scratch/message" || refuse "the arguments (no message file $2)"; fi
      message=1; shift;;
    -*) refuse "the arguments (unknown option $1; $USAGE)";;
    *) paths+=("$1");;
  esac
  shift
done
[ -n "$message" ] || refuse "the arguments (no message; $USAGE)"
[ -n "$all" ] || [ "${#paths[@]}" -gt 0 ] || refuse "the arguments (name the paths to stage, or -a for all; $USAGE)"
[ -z "$all" ] || [ "${#paths[@]}" -eq 0 ] || refuse "the arguments (-a and paths together; $USAGE)"
[ "${GHOST_GATE:-}" != "skip" ] || docs_only=1
git stripspace < "$scratch/message" > "$scratch/clean" && mv "$scratch/clean" "$scratch/message"
subject=$(head -1 "$scratch/message")
[ -n "$subject" ] || refuse "the arguments (the message is empty)"

# 1. Stage. The parent is named once, here: the commit is made on it or not at all.
branch=$(git symbolic-ref --short -q HEAD) || refuse "staging (HEAD is not on a branch)"
parent=$(git rev-parse --verify -q HEAD) || refuse "staging (the branch has no commit yet)"
saved_index=$(git rev-parse --git-path index)
if [ -f "$saved_index" ]; then cp "$saved_index" "$scratch/index"; else saved_index=""; fi
if [ -n "$all" ]; then git add -A || refuse "staging (git add failed)"; else git add -A -- "${paths[@]}" || refuse "staging (git add failed on the paths given)"; fi
git diff --cached --quiet && refuse "staging (nothing is staged: the paths hold no change)"

# 2. The secret scan, over the staged diff.
scan() { git diff --cached --no-color --no-ext-diff | python3 -I scripts/checks/secrets.py --diff; }
findings=$(scan) || refuse "the secret scan (the staged diff holds a secret: $(echo "$findings" | paste -sd ';' -); nothing committed)"

# 3. The commit check (C-039): a staged surface needs a decision id somewhere in the message.
surface=$(git diff --cached --name-only | grep -E '^(scripts/[^/]+\.sh|stacks/[^/]+/gate\.sh|\.claude/agents/[^/]+\.md|\.github/workflows/[^/]+\.ya?ml)$' | head -1)
if [ -n "$surface" ] && ! grep -qE '\b[A-Z]{1,4}-[0-9]{3,}\b' "$scratch/message"; then
  refuse "the commit check ($surface runs code by itself: a change to it names the decision it carries, as C-nnn, in the message; C-039)"
fi

# 4. The tune-up rule. The deferral line is Ghost's word in docs/HANDOFF.md, read with one grep; the last one written counts.
# The count starts after the newest `tune-up:` commit, or after a stamped project's founding commit, whichever is newer,
# and runs along main's first-parent line only (C-040); a clone with no main yet counts HEAD's.
line=$(git rev-parse -q --verify refs/heads/main >/dev/null && echo refs/heads/main || echo HEAD)
last_tune_up=$(git log --first-parent --format='%H %s' "$line" | awk '$2 == "tune-up:" || ($2 == "stamped" && $3 == "from") {print $1; exit}')
start=$last_tune_up
deferred=$(grep -oE 'Tune-up deferred through [0-9a-f]{7,40}' docs/HANDOFF.md 2>/dev/null | tail -1 | awk '{print $4}')
if [ -n "$deferred" ]; then
  sha=$(git rev-parse --verify -q "$deferred^{commit}") && git merge-base --is-ancestor "$sha" "$line" || sha=""
  if [ -z "$sha" ]; then
    echo "commit: the deferral line names $deferred, not a commit on main's history; not honoured"
  elif [ -z "$start" ] || git merge-base --is-ancestor "$start" "$sha"; then
    start=$sha
  fi
fi
if [ -n "$start" ]; then count=$(git rev-list --first-parent --count "$start..$line"); else count=$(git rev-list --first-parent --count "$line"); fi
if [ -n "$start" ] && [ "$start" != "$last_tune_up" ]; then from=" (counted after the deferral through ${deferred})"; else from=""; fi
if [[ "$subject" == tune-up:* ]]; then
  echo "commit: tune-up accepted ($count commits since the last)"
elif [ "$count" -ge "$TUNE_UP_EVERY" ]; then
  refuse "the tune-up rule (a tune-up is due: $count commits since the last$from, every $TUNE_UP_EVERY: docs/when/tune-up.md)"
else
  echo "commit: $count of $TUNE_UP_EVERY commits since the last tune-up$from"
fi

# 5. The fast loop.
scripts/fast.sh >/dev/null 2>&1 || refuse "the fast loop (the fast loop is red: scripts/fast.sh)"

# 6. The record: the staged tree is the tree the gate passed on, or a docs/-only change says it was not compared.
staged=$(git write-tree) || refuse "the record (git write-tree failed)"
record_file="$(git rev-parse --git-dir)/ghost/tree"
recorded=$( [ -f "$record_file" ] && tr -d '[:space:]' < "$record_file" )
kind=$( [ -f "${record_file%tree}kind" ] && tr -d '[:space:]' < "${record_file%tree}kind" )
if [ -n "$docs_only" ]; then
  outside=$(git diff --cached --name-only | grep -v '^docs/' | head -1)
  [ -z "$outside" ] || refuse "the record (--docs-only, but $outside is not under docs/: run scripts/gate.sh --fast first)"
  git interpret-trailers --in-place --trailer "Gate: fast loop only" "$scratch/message"
  tree=$staged
elif [ -z "$recorded" ]; then
  refuse "the record (no tree recorded in $record_file: run scripts/gate.sh --fast first)"
elif [ "$staged" != "$recorded" ]; then
  refuse "the record (the staged tree ${staged:0:10} is not the tree the gate passed on, ${recorded:0:10}: run scripts/gate.sh --fast first)"
else
  tree=$recorded
  [ "$kind" != fast ] || git interpret-trailers --in-place --trailer "Gate: fast checks" "$scratch/message"
fi

# 7. The scan again: a step could have changed what is staged.
findings=$(scan) || refuse "the second secret scan (the staged diff holds a secret: $(echo "$findings" | paste -sd ';' -); nothing committed)"
[ "$(git write-tree)" = "$staged" ] || refuse "the second secret scan (the staged tree changed while the checks ran; nothing committed)"

# 8. The commit, from the tree, on the parent named at step 1; the branch moves only from that parent.
commit=$(GIT_AUTHOR_NAME=$AUTHOR_NAME GIT_AUTHOR_EMAIL=$AUTHOR_EMAIL GIT_COMMITTER_NAME=$COMMITTER_NAME \
  GIT_COMMITTER_EMAIL=$COMMITTER_EMAIL git commit-tree "$tree" -p "$parent" -F "$scratch/message") || refuse "the commit (git commit-tree failed)"
git update-ref -m "commit: $subject" "refs/heads/$branch" "$commit" "$parent" 2>/dev/null \
  || refuse "the commit (HEAD moved since staging: $branch is no longer ${parent:0:10}; nothing committed)"
committed=1
git reset -q
echo "commit: $(git rev-parse --short "$commit") $subject"
