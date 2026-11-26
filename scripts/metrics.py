"""Measure docs/AGENT.md's metrics, print the table, exit 1 if an armed metric regressed (C-022, C-023).

    python3 -I scripts/metrics.py [--fast-loop SECONDS] [--gate MINUTES] [--cold] [--write]

--write records the measurements in AGENT.md's Measured column, and refuses while a metric has regressed.
--cold says the timings came from a cold run (`GHOST_COLD=1 scripts/gate.sh` passes it): the table takes the warm
run only, so `--cold --write` prints one line and exits 1 (docs/when/tune-up.md step 2; C-024).
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from scripts.checks import agent_table, metrics  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
AGENT = ROOT / "docs" / "AGENT.md"
COLD_WRITE = ("metrics: refused: a cold run's numbers go to the journal's Cost line and the tune-up commit, never to "
              "docs/AGENT.md; write the warm run's (docs/when/tune-up.md step 2)")


def main() -> int:
    """Prints one line per metric and a summary line; 1 when an armed metric regressed."""
    parser = argparse.ArgumentParser(description="docs/AGENT.md's metrics")
    parser.add_argument("--fast-loop", type=float, default=None)
    parser.add_argument("--gate", type=float, default=None)
    parser.add_argument("--cold", action="store_true")
    parser.add_argument("--write", action="store_true")
    options = parser.parse_args()
    if options.cold and options.write:
        print(COLD_WRITE)
        return 1
    values = metrics.measure(ROOT, options.fast_loop, options.gate)
    rows = agent_table.table(AGENT.read_text())
    regressed = 0
    for name, value in values.items():
        state = agent_table.verdict(rows[name]["target"], rows[name]["measured"], value)
        regressed += state == "regressed"
        print(f"{name:40} {agent_table.shown(value):>8}  {rows[name]['target']:>8}  {state}")
    if options.write and not regressed:
        AGENT.write_text(agent_table.rewritten(AGENT.read_text(), values))
    measured = sum(1 for value in values.values() if value is not None)
    written = ", written" if options.write and not regressed else ""
    print(f"metrics: {measured} of {len(values)} measured, {regressed} regressed{written}")
    return 1 if regressed else 0


if __name__ == "__main__":
    sys.exit(main())
