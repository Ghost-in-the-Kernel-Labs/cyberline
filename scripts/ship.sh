#!/usr/bin/env bash
# The ship (C-037, C-031): the only push, and the only one any document names. It fetches main, refuses uncommitted
# changes, refuses a HEAD whose tree is not the tree scripts/gate.sh passed on (.git/ghost/tree), refuses a push that is
# not a fast-forward of origin/main, pushes HEAD to main (never forced, never another branch) and prints one line,
# `ship: <short> → origin/main`, or `ship: refused at <step> (<why>)`. A remote with no main yet takes the first ship.
# Usage: scripts/ship.sh
set -uo pipefail
cd "$(dirname "$0")/.."
refuse() { echo "ship: refused at $1"; exit 1; }

head=$(git rev-parse --verify -q 'HEAD^{commit}') || refuse "HEAD (no commit to ship)"
git ls-remote --exit-code --heads origin main >/dev/null 2>&1
case $? in
  0) git fetch -q origin +refs/heads/main:refs/remotes/origin/main || refuse "the fetch (git fetch origin main failed)"; first="";;
  2) first=1;;
  *) refuse "the fetch (origin did not answer)";;
esac
[ -z "$(git status --porcelain)" ] || refuse "the working tree (uncommitted changes: commit them through scripts/commit.sh, or put them away)"
record_file="$(git rev-parse --git-dir)/ghost/tree"
recorded=$( [ -f "$record_file" ] && tr -d '[:space:]' < "$record_file" )
[ -n "$recorded" ] || refuse "the record (gate first: no tree recorded; run scripts/gate.sh)"
tree=$(git rev-parse "$head^{tree}")
[ "$tree" = "$recorded" ] || refuse "the record (gate first: HEAD's tree ${tree:0:10} is not the tree the gate passed on, ${recorded:0:10})"
[ -n "$first" ] || git merge-base --is-ancestor refs/remotes/origin/main "$head" \
  || refuse "the fast-forward (fetch and rebuild: main moved; rebase onto origin/main, run scripts/gate.sh and commit again)"
git push -q origin "$head:refs/heads/main" || refuse "the push (git refused it; nothing forced)"
echo "ship: $(git rev-parse --short "$head") → origin/main"
