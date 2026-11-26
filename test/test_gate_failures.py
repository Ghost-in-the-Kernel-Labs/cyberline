"""A red gate names its failing tests before the verdict and keeps its log whole (3.13; C-001, EE J-139: a gate that
cleaned up after itself lost a one-in-ten failure's name). Built on test/support_git.py's scratch repository."""
import unittest

from test.support_git import gate, gated_repo


class TheFailingNames(unittest.TestCase):
    def test_a_red_step_names_its_failing_tests_before_the_verdict_and_keeps_its_log(self) -> None:
        root = gated_repo()
        (root / "scripts" / "fast.sh").write_text("#!/usr/bin/env bash\necho 'FAIL: earlier (a passing step printed it)'\n")
        names = [f"FAIL: test_{n} (test.test_x.TheX.test_{n})" for n in range(43)] + ["ERROR: test_e (test.test_y.TheY.test_e)"]
        (root / "scripts" / "decisions_index.py").write_text("import sys\n" + "".join(f"print({n!r})\n" for n in names) + "sys.exit(1)\n")
        lines = [line for line in gate(root).stdout.splitlines() if not line.startswith("== ")]
        self.assertEqual(lines, names[:40] + ["... 4 more in build/gate.log", "gate: refused at a stale docs/decisions.md"])
        log = (root / "build" / "gate.log").read_text()
        self.assertTrue(all(name in log for name in names), "the log is kept whole")
        self.assertTrue(log.endswith("gate: refused at a stale docs/decisions.md\n"))

    def test_a_red_step_without_test_names_prints_only_the_verdict(self) -> None:
        root = gated_repo()
        (root / "red").write_text("")
        self.assertEqual(gate(root).stdout.splitlines(), ["gate: refused at the fast loop"])
