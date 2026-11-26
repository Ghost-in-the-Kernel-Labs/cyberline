#!/usr/bin/env bash
# The TypeScript stack's gate, run by scripts/gate.sh when stacks/typescript/PRESENT exists: the lockfile install,
# the fast loop, typecheck, knip, the cooldown, advisories, then mutation with every survivor explained.
# With --fast (the fast checks, C-040) it stops after the fast loop and says `typescript gate: fast checks passed`.
set -euo pipefail
cd "$(dirname "$0")/../.."
[ "$(npm --version | cut -d. -f1)" -ge 11 ] || { echo "typescript gate: npm $(npm --version) is below 11 (package.json engines.npm; npm 10 crashes on vitest 4)"; exit 1; }
[ -d node_modules ] || npm ci --ignore-scripts || { echo "typescript gate: npm ci"; exit 1; }
npx vitest run --project unit || { echo "typescript gate: the fast loop"; exit 1; }
[ "${1:-}" != --fast ] || { echo "typescript gate: fast checks passed"; exit 0; }
npx tsc --noEmit || { echo "typescript gate: tsc"; exit 1; }
npx knip || { echo "typescript gate: knip (something floats: an unused export, file or dependency)"; exit 1; }
node scripts/cooldown.mjs --strict || { echo "typescript gate: a locked version younger than 7 days"; exit 1; }
npm audit --audit-level=high || { echo "typescript gate: a high or critical advisory"; exit 1; }
node scripts/weakened.mjs || true
node scripts/mutate.mjs || { echo "typescript gate: a surviving mutant with no line in docs/MUTATION.md"; exit 1; }
echo "typescript gate: passed"
