#!/usr/bin/env bash
# The fast loop: every doc check and unit test, no data, no network, nothing installed (C-022, C-032).
# Run after every edit. Python 3 standard library only; -I ignores the environment and the current directory.
# With arguments, only those test modules: `scripts/fast.sh test.test_stamp` (or test_stamp, or test/test_stamp.py).
# Each becomes discover's -p pattern, since `-m unittest test.test_stamp` under -I finds the standard library's
# `test` package, and a module given to discover as a positional argument is read as its start folder (all of test/).
# A name that matches no file runs no test, which unittest reports as a failure.
set -euo pipefail
cd "$(dirname "$0")/.."
if [ "$#" -eq 0 ]; then
  exec python3 -I -m unittest discover -s test -t . -p 'test_*.py'
fi
status=0
for module in "$@"; do
  name=$(basename "${module%.py}")
  python3 -I -m unittest discover -s test -t . -p "${name##*.}.py" || status=1
done
exit "$status"
