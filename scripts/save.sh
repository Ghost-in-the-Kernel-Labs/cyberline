#!/usr/bin/env bash
# The save (C-040): a session's checkpoint on its own branch, so no turn ends with a dirty tree or an unpushed commit
# and nothing re-prompts about one. It is not a landing: nothing here reaches `main` (scripts/commit.sh, then
# scripts/ship.sh, are the only way there). In order, each refusal one line naming its step:
#   1. the branch: refused on `main`; a session's branch is `claude/<session>` or `agent/<name>`
#   2. stage everything (`git add -A`)
#   3. the key scan over the staged diff (scripts/checks/secrets.py --diff); a finding is named by fingerprint, never printed
#   4. the commit: a plain `git commit`, author Ghost and committer Claude, when anything is staged; with nothing staged
#      an earlier commit may still want pushing, so the save goes on
#   5. the push: `git push -u origin HEAD`, when a remote `origin` exists; without one the line says so
# No gate, no fast loop, no tune-up count: a save is scanned, a landing passes the fast checks (`scripts/gate.sh
# --fast`), a release passes the full gate (C-040's three checkpoints). One line last: `save: <short> → origin/<branch>`,
# `save: <short> on <branch> (no origin)`, `save: nothing to commit; pushed` or `save: refused at <step> (<why>)`.
# Usage: scripts/save.sh -m msg | -F file     (-F - reads the message from stdin)
set -uo pipefail
cd "$(dirname "$0")/.."
AUTHOR_NAME=Ghost
AUTHOR_EMAIL=118085043+ghost-in-the-kernel@users.noreply.github.com
COMMITTER_NAME=Claude
COMMITTER_EMAIL=noreply@anthropic.com
USAGE="usage: scripts/save.sh -m msg | -F file"

scratch=$(mktemp -d)
trap 'rm -rf "$scratch"' EXIT
refuse() { echo "save: refused at $1"; exit 1; }

message=""
while [ "$#" -gt 0 ]; do
  case "$1" in
    -m) [ "$#" -ge 2 ] && [ -z "$message" ] || refuse "the arguments ($USAGE)"; printf '%s\n' "$2" > "$scratch/message"; message=1; shift;;
    -F|--file)
      [ "$#" -ge 2 ] && [ -z "$message" ] || refuse "the arguments ($USAGE)"
      if [ "$2" = "-" ]; then cat > "$scratch/message"; else cat -- "$2" > "$scratch/message" || refuse "the arguments (no message file $2)"; fi
      message=1; shift;;
    *) refuse "the arguments (unknown argument $1; $USAGE)";;
  esac
  shift
done
[ -n "$message" ] || refuse "the arguments (no message; $USAGE)"
git stripspace < "$scratch/message" > "$scratch/clean" && mv "$scratch/clean" "$scratch/message"
[ -n "$(head -1 "$scratch/message")" ] || refuse "the arguments (the message is empty)"

# 1. The branch.
branch=$(git symbolic-ref --short -q HEAD) || refuse "the branch (HEAD is not on a branch)"
[ "$branch" != main ] || refuse "the branch (on main: a save goes to a session branch, claude/<session> or agent/<name>; main is landed through scripts/commit.sh and scripts/ship.sh)"

# 2. Stage everything.
git add -A || refuse "staging (git add failed)"

# 3. The key scan.
findings=$(git diff --cached --no-color --no-ext-diff | python3 -I scripts/checks/secrets.py --diff) \
  || refuse "the key scan (the staged diff holds a secret: $(echo "$findings" | paste -sd ';' -); nothing committed)"

# 4. The commit.
committed=""
if ! git diff --cached --quiet; then
  GIT_AUTHOR_NAME=$AUTHOR_NAME GIT_AUTHOR_EMAIL=$AUTHOR_EMAIL GIT_COMMITTER_NAME=$COMMITTER_NAME GIT_COMMITTER_EMAIL=$COMMITTER_EMAIL \
    git commit -q -F "$scratch/message" || refuse "the commit (git commit failed)"
  committed=$(git rev-parse --short HEAD)
fi

# 5. The push.
if ! git remote get-url origin >/dev/null 2>&1; then
  [ -n "$committed" ] || refuse "the push (nothing to commit, and no remote origin to push to)"
  echo "save: $committed on $branch (no origin)"
  exit 0
fi
git push -q -u origin HEAD || refuse "the push (git push origin $branch failed; the commit stands on $branch)"
if [ -n "$committed" ]; then echo "save: $committed → origin/$branch"; else echo "save: nothing to commit; pushed $branch"; fi
