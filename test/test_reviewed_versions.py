"""docs/REVIEWED-VERSIONS.md holds its shape; and planted bad rows are caught (C-035)."""
import unittest

from scripts.checks import dependency_review
from test.support import BROKEN, ROOT, scratch

HEAD = "| Date | Package | From | To | Kind | Verdict | Reputation | Decision | Journal | Notes |\n| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"


def row(verdict: str = "SAFE", reputation: str = "CLEAN", decision: str = "automatic", journal: str = "J-012") -> str:
    """One record row with the fields given: row() is a routine automatic update."""
    return f"| 2026-11-01 | vitest | 5.0.4 | 5.0.5 | patch | {verdict} | {reputation} | {decision} | {journal} | |\n"


NO_ROW = "has no row in docs/REVIEWED-VERSIONS.md (a review for an update or a new package; an \"unreviewed baseline\" row only on adoption)"


def baseline(package: str, version: str) -> str:
    """One unreviewed baseline row: baseline("a", "1.0.0")."""
    return f"| 2026-11-07 | {package} | — | {version} | baseline | — | — | unreviewed baseline | J-071 | |\n"


class TheRepository(unittest.TestCase):
    def test_the_real_record_holds(self) -> None:
        self.assertEqual(dependency_review.record_problems((ROOT / "docs" / "REVIEWED-VERSIONS.md").read_text()), [])

    def test_every_pin_the_repository_holds_has_a_row(self) -> None:
        self.assertEqual(dependency_review.problems(ROOT), [])

    @unittest.skipUnless((ROOT / "stacks" / "java" / "starter" / "Dockerfile").is_file(), "Ghost-Core only: a stamp keeps one stack")
    def test_core_s_pins_are_the_workflow_s_action_and_the_java_starter_s_image(self) -> None:
        self.assertEqual(sorted(name for _, name, _ in dependency_review.pins(ROOT)), ["actions/checkout", "gradle:8.14.3-jdk21-noble"])

    def test_the_planted_breaks_are_caught(self) -> None:
        planted = BROKEN / "dependency_review"
        self.assertEqual(dependency_review.record_problems((planted / "docs" / "REVIEWED-VERSIONS.md").read_text()), [
            "row '2026-11-09 a' baselines a package that already has a row: an update is read, never baselined",
            "row '2026-11-09 c' is a baseline row but its From is '0.9', not '—'",
            "row '2026-11-09 c' is a baseline row but its Verdict is 'SAFE', not '—'",
        ])
        self.assertEqual(dependency_review.pin_problems(planted), [
            f".github/workflows/w.yml: actions/setup-node {'2' * 40} {NO_ROW}",
            f"Dockerfile: node:22 sha256:{'3' * 64} {NO_ROW}",
            f"package-lock.json: b 2.0.0 {NO_ROW}",
            f"requirements.lock: pytest 8.3.0 {NO_ROW}",
            f"third_party/MANIFEST.md: lib-1.0.tar.gz {'4' * 64} {NO_ROW}",
        ])


class TheCheck(unittest.TestCase):
    def test_a_routine_row_holds(self) -> None:
        self.assertEqual(dependency_review.record_problems(HEAD + row()), [])

    def test_ghosts_answer_holds(self) -> None:
        self.assertEqual(dependency_review.record_problems(HEAD + row("UNSURE", "CLEAN", "Ghost: the new chunk is the parser; take it")), [])

    def test_an_automatic_unsure_is_caught(self) -> None:
        self.assertEqual(dependency_review.record_problems(HEAD + row("UNSURE")), ["row '2026-11-01 vitest' was automatic without SAFE and CLEAN"])

    def test_an_unsafe_taken_is_caught(self) -> None:
        self.assertEqual(dependency_review.record_problems(HEAD + row("UNSAFE", "CONCERN", "Ghost: take it anyway")), ["row '2026-11-01 vitest' is UNSAFE and not refused"])
        self.assertEqual(dependency_review.record_problems(HEAD + row("UNSAFE", "CONCERN", "Ghost: refused, reported to npm")), [])

    def test_a_row_without_a_journal_entry_is_caught(self) -> None:
        self.assertEqual(dependency_review.record_problems(HEAD + row(journal="")), ["row '2026-11-01 vitest' has no journal entry"])

    def test_a_narrow_row_is_caught(self) -> None:
        self.assertEqual(dependency_review.record_problems(HEAD + "| 2026-11-01 | vitest | 5.0.4 |\n"), ["row '2026-11-01 vitest' has 3 cells, not 10"])


class ThePins(unittest.TestCase):
    """4.5: a lockfile entry with no row fails; a baseline row names a pin held on adoption, never an update."""

    def test_a_lockfile_entry_added_without_a_row_fails_and_a_row_clears_it(self) -> None:
        root = scratch()
        (root / "package-lock.json").write_text('{"packages": {"": {}, "node_modules/a": {"version": "1.0.0"}}}')
        (root / "docs" / "REVIEWED-VERSIONS.md").write_text(HEAD)
        self.assertEqual(dependency_review.pin_problems(root), [f"package-lock.json: a 1.0.0 {NO_ROW}"])
        (root / "docs" / "REVIEWED-VERSIONS.md").write_text(HEAD + baseline("a", "1.0.0"))
        self.assertEqual(dependency_review.pin_problems(root), [])
        (root / "package-lock.json").write_text('{"packages": {"node_modules/a": {"version": "1.0.1"}}}')
        self.assertEqual(dependency_review.pin_problems(root), [f"package-lock.json: a 1.0.1 {NO_ROW}"])

    def test_a_baseline_row_holds_and_a_second_for_the_package_is_refused(self) -> None:
        self.assertEqual(dependency_review.record_problems(HEAD + baseline("a", "1.0.0")), [])
        self.assertEqual(dependency_review.record_problems(HEAD + baseline("a", "1.0.0") + baseline("a", "1.0.1")),
                         ["row '2026-11-07 a' baselines a package that already has a row: an update is read, never baselined"])

    def test_a_fixture_s_pins_are_not_the_repository_s(self) -> None:
        root = scratch()
        (root / "test" / "fixtures").mkdir(parents=True)
        (root / "test" / "fixtures" / "requirements.lock").write_text("x==1\n")
        self.assertEqual(dependency_review.pins(root), [])

    def test_a_stub_pin_and_a_local_action_are_not_pins(self) -> None:
        root = scratch()
        (root / "Dockerfile").write_text("FROM gcc:14.2.0@sha256:STAMP-the-digest\n")
        (root / ".github" / "workflows").mkdir(parents=True)
        (root / ".github" / "workflows" / "a.yml").write_text("      - uses: ./local\n      - uses: actions/x@v4\n")
        self.assertEqual(dependency_review.pins(root), [])
