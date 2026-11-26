"""The secret scan (C-037, TODO 3.6): a key, token or private key in a tracked file or on a diff's added line is named by
file, line, pattern and fingerprint, never by its value, so the report cannot become the leak (SB G-570, Katana R-104).

    python3 -I scripts/checks/secrets.py          every tracked file (git ls-files; the tree outside git)
    python3 -I scripts/checks/secrets.py --diff   the added lines of a unified diff read on stdin (the commit path)

Each finding prints as `path:line pattern fingerprint`, the fingerprint the first 12 hex digits of the value's SHA-256;
exit 1 on a finding. A value that is not a secret (a fixture's made-up one) is allowed by its fingerprint and a reason,
one per line of docs/secret-allow.txt: `<fingerprint> <reason>`; never by a path. test/test_secrets.py holds it, and
builds every key it plants from fragments at run time, so no key-shaped literal is in the source.
"""
import hashlib
import math
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALLOW = Path("docs") / "secret-allow.txt"
GENERIC = "generic secret"
PRIVATE_KEY = "private key"
MIN_LENGTH = 20
MIN_ENTROPY = 3.5
BINARY_PROBE = 8000  # git's own heuristic: a NUL in the first 8000 bytes is a binary file
# The vendor forms, each bounded and linear. sk-ant- is Anthropic's and is read before OpenAI's sk-, which excludes it.
VENDOR: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("aws access key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("github token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,255}\b")),
    ("github fine-grained token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{22,255}\b")),
    ("slack token", re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,250}")),
    ("stripe live key", re.compile(r"\b[sr]k_live_[A-Za-z0-9]{20,247}\b")),
    ("google api key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}(?![0-9A-Za-z_-])")),
    ("anthropic key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,255}")),
    ("openai key", re.compile(r"\bsk-(?!ant-)(?:proj-|svcacct-|admin-)?[A-Za-z0-9_-]{20,255}")),
    (PRIVATE_KEY, re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |ENCRYPTED )?PRIVATE KEY-----")),
)
# `name = value` or `name: value`, the name holding one of the words, the value quoted or bare. The name starts where a
# word starts and is at most 40 characters on each side of its word, so no line costs more than linear time.
NAMED = re.compile(r"(?i)(?<![\w.-])[\w.-]{0,40}(?:key|token|secret|password|passwd|credential)[\w.-]{0,40}[\"']?\s*[:=]\s*[\"']?([A-Za-z0-9+/_.~=-]{20,512})")


@dataclass(frozen=True)
class Finding:
    """One secret's place and kind: str() gives `config/app.env:3 aws access key 9f86d081884c`, never the value."""
    path: str
    line: int
    pattern: str
    fingerprint: str

    def __str__(self) -> str:
        """The report line: `<path>:<line> <pattern> <fingerprint>`."""
        return f"{self.path}:{self.line} {self.pattern} {self.fingerprint}"


def entropy(value: str) -> float:
    """Shannon entropy in bits per character: entropy("aaaa") gives 0.0, entropy("abcd") gives 2.0."""
    counts = [value.count(c) for c in set(value)]
    return -sum(n / len(value) * math.log2(n / len(value)) for n in counts) if value else 0.0


def fingerprint(value: str) -> str:
    """The first 12 hex digits of the value's SHA-256: fingerprint("abc") gives "ba7816bf8f01"."""
    return hashlib.sha256(value.encode()).hexdigest()[:12]


def is_generic_value(value: str) -> bool:
    """Whether a named value reads as a secret: at least 20 characters at 3.5 bits each, holding a digit and a letter, as
    Suite Builder's named secret has it (SB G-570): is_generic_value("response.headers.authorization") is False, a code
    expression; a random 24-character mix of letters and digits is True."""
    has_both = re.search(r"[0-9]", value) is not None and re.search(r"[A-Za-z]", value) is not None
    return has_both and len(value) >= MIN_LENGTH and entropy(value) >= MIN_ENTROPY


def line_secrets(line: str, following: str) -> list[tuple[str, str]]:
    """Each (pattern, value) on one line; a private key's value is its header and the line after it, so one allowed key
    does not allow every key of its kind. A generic match inside a vendor match is not reported twice."""
    found: list[tuple[str, str]] = []
    spans: list[tuple[int, int]] = []
    for name, pattern in VENDOR:
        for match in pattern.finditer(line):
            found.append((name, match.group(0) + ("\n" + following if name == PRIVATE_KEY else "")))
            spans.append(match.span())
    for match in NAMED.finditer(line):
        value = match.group(1)
        inside = any(start < match.end(1) and match.start(1) < end for start, end in spans)
        if not inside and is_generic_value(value):
            found.append((GENERIC, value))
    return found


def scan_lines(numbered: list[tuple[int, str]], path: str) -> list[Finding]:
    """The findings in (line number, text) pairs of one file, each line read with the one after it."""
    found: list[Finding] = []
    for at, (number, text) in enumerate(numbered):
        following = numbered[at + 1][1] if at + 1 < len(numbered) else ""
        found += [Finding(path, number, name, fingerprint(value)) for name, value in line_secrets(text, following)]
    return found


def scan_text(text: str, path: str) -> list[Finding]:
    """The findings in one file's text, lines numbered from 1: a line `aws = <an AWS key>` in x.env at line 2 gives
    [Finding("x.env", 2, "aws access key", <its fingerprint>)]."""
    return scan_lines(list(enumerate(text.splitlines(), start=1)), path)


HUNK = re.compile(r"^@@ -\d+(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def added_lines(diff_text: str) -> dict[str, list[tuple[int, str]]]:
    """The added lines of a unified diff by the new file's path, each with its line number in the new file. A hunk is
    read by its counts, so an added line that begins `++` or `--` is never mistaken for a header; a deleted file
    (`+++ /dev/null`) adds nothing."""
    files: dict[str, list[tuple[int, str]]] = {}
    path, number, old_left, new_left = "", 0, 0, 0
    for line in diff_text.splitlines():
        if old_left > 0 or new_left > 0:
            kind, text = line[:1], line[1:]
            if kind == "+":
                files.setdefault(path, []).append((number, text))
            if kind in "+ " and line:
                number, new_left = number + 1, new_left - 1
            if kind in "- " or not line:
                old_left -= 1
            continue
        hunk = HUNK.match(line)
        if line.startswith("+++ "):
            path = re.sub(r"^b/", "", line[4:].split("\t")[0])
        elif hunk:
            old_left = int(hunk.group(1) or 1)
            number, new_left = int(hunk.group(2)), int(hunk.group(3) or 1)
    return files


def scan_diff(diff_text: str) -> list[Finding]:
    """The findings on a diff's added lines only: a key the diff removes is not reported, one it adds is."""
    return [f for path, lines in added_lines(diff_text).items() if path != "/dev/null" for f in scan_lines(lines, path)]


def allowed(root: Path) -> tuple[set[str], list[str]]:
    """The allowed fingerprints of docs/secret-allow.txt, and its malformed lines: a line `9f86d081884c a fixture's
    made-up key` allows that fingerprint; a line without a reason, or with another length of fingerprint, is a problem."""
    path = root / ALLOW
    fingerprints: set[str] = set()
    problems: list[str] = []
    for number, line in enumerate(path.read_text().splitlines() if path.is_file() else [], start=1):
        if not line.strip() or line.startswith("#"):
            continue
        if re.fullmatch(r"[0-9a-f]{12} \S.*", line):
            fingerprints.add(line[:12])
        else:
            problems.append(f"{ALLOW}:{number} is not `<12-hex fingerprint> <reason>`")
    return fingerprints, problems


SKIPPED_FOLDERS = {".git", "__pycache__", "build", "node_modules", ".venv", "mutants"}


def tracked_files(root: Path) -> list[str]:
    """The files git tracks under root, relative; outside git, every file not in a run's folder (.git, build, …)."""
    listed = subprocess.run(["git", "-C", str(root), "ls-files", "-z"], capture_output=True)
    if listed.returncode == 0 and (root / ".git").exists():
        return [name for name in listed.stdout.decode("utf-8", "replace").split("\0") if name]
    walked = (p.relative_to(root) for p in root.rglob("*") if p.is_file())
    return sorted(str(p) for p in walked if not SKIPPED_FOLDERS.intersection(p.parts))


def scan_tree(root: Path) -> list[Finding]:
    """The findings in every tracked file that is on disk and is text (no NUL in its first 8000 bytes)."""
    found: list[Finding] = []
    for name in tracked_files(root):
        path = root / name
        data = path.read_bytes() if path.is_file() else b""
        if b"\0" not in data[:BINARY_PROBE]:
            found += scan_text(data.decode("utf-8", "replace"), name)
    return found


def reported(findings: list[Finding], root: Path) -> list[str]:
    """The report lines: each finding whose fingerprint is not allowed, then the allow file's malformed lines."""
    fingerprints, problems = allowed(root)
    return [str(f) for f in findings if f.fingerprint not in fingerprints] + problems


def problems(root: Path) -> list[str]:
    """Every unallowed secret in the tracked files, and every malformed allow line; [] when the tree holds none."""
    return reported(scan_tree(root), root)


def main(argv: list[str]) -> int:
    """The command line: no argument scans the tracked files, `--diff` a unified diff on stdin; exit 1 on a finding."""
    lines = reported(scan_diff(sys.stdin.read()), ROOT) if argv == ["--diff"] else problems(ROOT)
    for line in lines:
        print(line)
    print(f"secrets: {len(lines)} found" if lines else "secrets: none found")
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
