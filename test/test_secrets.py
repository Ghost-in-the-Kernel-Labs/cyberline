"""scripts/checks/secrets.py finds every vendor form, a private key and a generic named value in a planted file and on a
diff's added lines, reports file, line, pattern and fingerprint and never the value, honours docs/secret-allow.txt by
fingerprint, and finds nothing in the tracked files (C-037, TODO 3.6). Every key here is assembled from fragments at
run time, so no key-shaped literal is in this file; the planted break's template holds slots, never keys."""
import hashlib
import string
import subprocess
import tempfile
import unittest
from pathlib import Path

from scripts.checks import secrets
from test.support import BROKEN, ROOT

ALNUM = string.ascii_letters + string.digits


def planted_values() -> dict[str, str]:
    """The template's slots, each filled with a value of its form built from fragments: {"aws": "AK" + "IA" + …, …}."""
    return {
        "aws": "AK" + "IA" + (string.ascii_uppercase + string.digits)[5:21],
        "github": "gh" + "p_" + ALNUM[:36],
        "github_pat": "github" + "_pat_" + ALNUM[10:32],
        "slack": "xo" + "xb-" + string.digits + "-" + ALNUM[:12],
        "stripe": "sk" + "_live_" + ALNUM[20:44],
        "google": "AI" + "za" + (ALNUM + "_-")[25:60],
        "openai": "sk" + "-proj-" + ALNUM[2:42],
        "anthropic": "sk" + "-ant-" + "api03-" + ALNUM[7:47],
        "private_key_header": "-----BEGIN " + "RSA " + "PRIVATE" + " KEY-----",
        "private_key_body": ALNUM * 2,
        "generic": ALNUM[::3],
        "low_entropy": "a1" * 12,
        "no_name": ALNUM[1::3],
    }


EXPECTED = [(3, "aws access key"), (4, "github token"), (5, "github fine-grained token"), (6, "slack token"),
            (7, "stripe live key"), (8, "google api key"), (9, "openai key"), (10, "anthropic key"), (11, "private key"),
            (13, "generic secret")]


def planted_root() -> Path:
    """A scratch folder holding the planted break filled in, as planted.env, and an empty docs/ folder."""
    root = Path(tempfile.mkdtemp(prefix="ghost-core-secrets-"))
    (root / "docs").mkdir()
    template = (BROKEN / "secrets" / "planted.env.in").read_text()
    (root / "planted.env").write_text(template.format(**planted_values()))
    return root


def diff_adding(path: str, lines: list[str], removed: list[str] = ()) -> str:
    """A unified diff of one file that removes `removed` and adds `lines` at line 1."""
    body = [f"-{line}" for line in removed] + [f"+{line}" for line in lines]
    return f"diff --git a/{path} b/{path}\n--- a/{path}\n+++ b/{path}\n@@ -1,{len(removed)} +1,{len(lines)} @@\n" + "\n".join(body) + "\n"


class TheRepository(unittest.TestCase):
    def test_no_tracked_file_holds_a_secret(self) -> None:
        self.assertEqual(secrets.problems(ROOT), [])

    def test_the_planted_break_s_template_holds_no_key(self) -> None:
        self.assertEqual(secrets.scan_text((BROKEN / "secrets" / "planted.env.in").read_text(), "planted.env.in"), [])


class TheScan(unittest.TestCase):
    def test_the_planted_break_is_caught_form_by_form(self) -> None:
        root = planted_root()
        found = secrets.scan_tree(root)
        self.assertEqual([(f.path, f.line, f.pattern) for f in found], [("planted.env", n, p) for n, p in EXPECTED])

    def test_the_report_never_holds_a_value(self) -> None:
        report = "\n".join(secrets.problems(planted_root()))
        for slot, value in planted_values().items():
            with self.subTest(slot=slot):
                self.assertNotIn(value, report)

    def test_the_fingerprint_is_the_first_twelve_hex_of_the_sha256(self) -> None:
        value = planted_values()["aws"]
        (finding,) = secrets.scan_text(f"x = {value}\n", "a.txt")
        self.assertEqual(str(finding), f"a.txt:1 aws access key {hashlib.sha256(value.encode()).hexdigest()[:12]}")

    def test_two_private_keys_of_one_kind_have_two_fingerprints(self) -> None:
        header = planted_values()["private_key_header"]
        one, two = (secrets.scan_text(f"{header}\n{body}\n", "k.pem")[0].fingerprint for body in (ALNUM, ALNUM[::-1]))
        self.assertNotEqual(one, two)

    def test_a_named_value_needs_its_length_its_entropy_a_digit_and_a_letter(self) -> None:
        self.assertEqual(secrets.entropy("abcd"), 2.0)
        cases = {ALNUM[::3]: True, ALNUM[::3][:19]: False, "a1" * 12: False, string.ascii_letters[::2]: False,
                 "response.headers.authorization": False}
        for value, expected in cases.items():
            with self.subTest(value=value[:6]):
                self.assertEqual(bool(secrets.scan_text(f"token = {value}", "t")), expected)

    def test_a_name_without_a_secret_word_is_not_read(self) -> None:
        self.assertEqual(secrets.scan_text(f"colour = {ALNUM[::3]}", "t"), [])

    def test_outside_git_the_tree_is_walked_and_run_folders_skipped(self) -> None:
        root = planted_root()
        (root / "build").mkdir()
        (root / "build" / "out.env").write_text((root / "planted.env").read_text())
        self.assertEqual(secrets.tracked_files(root), ["planted.env"])


class TheDiff(unittest.TestCase):
    def test_an_added_key_is_found_at_its_new_line(self) -> None:
        aws = planted_values()["aws"]
        found = secrets.scan_diff(diff_adding("conf/app.env", ["# config", f"KEY_ID={aws}"]))
        self.assertEqual([(f.path, f.line, f.pattern) for f in found], [("conf/app.env", 2, "aws access key")])

    def test_a_removed_key_is_not_reported(self) -> None:
        aws = planted_values()["aws"]
        self.assertEqual(secrets.scan_diff(diff_adding("conf/app.env", ["KEY_ID=rotated"], removed=[f"KEY_ID={aws}"])), [])

    def test_an_added_line_that_looks_like_a_header_is_still_read(self) -> None:
        aws = planted_values()["aws"]
        found = secrets.scan_diff(diff_adding("notes.md", [f"++ b/{aws}", "-- x"]))
        self.assertEqual([(f.line, f.pattern) for f in found], [(1, "aws access key")])

    def test_line_numbers_follow_the_context(self) -> None:
        aws = planted_values()["aws"]
        diff = f"--- a/x.env\n+++ b/x.env\n@@ -10,3 +10,4 @@\n one\n-two\n+TWO\n three\n+K={aws}\n"
        self.assertEqual([f.line for f in secrets.scan_diff(diff)], [13])

    def test_the_command_line_reads_a_diff_and_refuses_without_the_value(self) -> None:
        aws = planted_values()["aws"]
        result = subprocess.run(["python3", "-I", "scripts/checks/secrets.py", "--diff"], cwd=ROOT, capture_output=True, text=True,
                                input=diff_adding("x.env", [f"K={aws}"]))
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(aws, result.stdout)
        self.assertEqual(result.stdout.splitlines(), [f"x.env:1 aws access key {secrets.fingerprint(aws)}", "secrets: 1 found"])
        clean = subprocess.run(["python3", "-I", "scripts/checks/secrets.py", "--diff"], cwd=ROOT, capture_output=True, text=True,
                               input=diff_adding("x.env", ["K=1"]))
        self.assertEqual((clean.returncode, clean.stdout), (0, "secrets: none found\n"))


class TheAllowList(unittest.TestCase):
    def test_an_allowed_fingerprint_is_not_reported_and_another_still_is(self) -> None:
        root = planted_root()
        aws = secrets.fingerprint(planted_values()["aws"])
        (root / "docs" / "secret-allow.txt").write_text(f"# fingerprints\n{aws} a made-up key of the planted break\n")
        report = secrets.problems(root)
        self.assertEqual(len(report), len(EXPECTED) - 1)
        self.assertFalse(any(aws in line for line in report))

    def test_a_line_without_a_reason_is_refused(self) -> None:
        root = planted_root()
        aws = secrets.fingerprint(planted_values()["aws"])
        (root / "docs" / "secret-allow.txt").write_text(f"{aws}\n")
        self.assertIn("docs/secret-allow.txt:1 is not `<12-hex fingerprint> <reason>`", secrets.problems(root))
