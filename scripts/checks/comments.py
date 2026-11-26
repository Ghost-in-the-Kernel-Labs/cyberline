"""A comment or docstring in code says what the code does and gives no reason in its own words (test/test_comments.py; C-042).

Read: the code git tracks under scripts/, test/ (test/fixtures/ aside), stacks/ and src/, by suffix or name: Python
(docstrings and `#` comments), the hash languages (`#` lines) and the slash languages (`//` lines and `/* */` blocks).
A comment is one docstring, or one run of comment lines on consecutive lines; a comment that follows code on its line
is read in Python only.

Named: a comment that holds a reason word (REASON), a date written `2026-11-26`, or the id of a record that is not a
decision of theGhost.md (`J-080`, `G-290`, `F-001`). A decision's id (C-042), an invariant's (AGT-05, two digits) and a
file's range of ids (`J-000-099.md`) pass, and so does the column heading Why.
Text between double quotes or backticks is a value and is not read.

Run: python3 -I scripts/checks/comments.py --list prints every comment named, one per line.
"""
import ast
import io
import re
import sys
import tokenize
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from scripts.checks.common import tracked_files  # noqa: E402

FOLDERS = ("scripts", "test", "stacks", "src")
FIXTURES = ("test", "fixtures")
HASH = (".sh", ".toml", ".yml", ".yaml", ".in", ".append", ".npmrc", ".gitattributes", ".clang-format", "Dockerfile", "CMakeLists.txt")
SLASH = (".mjs", ".js", ".ts", ".hpp", ".cpp", ".java", ".gradle")
REASON = re.compile(r"\b([Bb]ecause|[Ss]ince|[Ss]o that|[Ii]n order to|[Tt]he reason|why|[Oo]therwise)\b")
DATE = re.compile(r"\b20\d\d-\d\d-\d\d\b")
QUOTED = re.compile(r'"[^"]*"|`[^`]*`')
RECORD = re.compile(r"\b([A-Z]{1,4})-(\d{2,3})\b(?!-\d)")
NOT_RECORDS = ("SHA", "ISO", "RFC", "UTF")
HEADING = re.compile(r"^### ([A-Z]{1,4})-\d{3}:", re.MULTILINE)
LOG = "theGhost.md"


def decision_prefixes(root: Path) -> list[str]:
    """The letters theGhost.md's decisions carry, sorted: a log with "### C-001: x" and "### P-001: y" gives ["C", "P"];
    no log gives []."""
    log = root / LOG
    return sorted(set(HEADING.findall(log.read_text()))) if log.is_file() else []


def markers(text: str, prefixes: list[str]) -> list[str]:
    """What in a comment's text reads as a reason, in the order words, dates, ids, each once, quoted text aside:
    markers("Sorted, because J-080 said so on 2026-11-18 (C-009, AGT-05)", ["C"]) gives ["because", "2026-11-18", "J-080"],
    and the same text between backticks gives []."""
    text = QUOTED.sub("", text)
    words = [word.lower() for word in REASON.findall(text)]
    ids = [f"{letters}-{digits}" for letters, digits in RECORD.findall(text)
           if letters not in NOT_RECORDS and len(digits) == 3 and letters not in prefixes]
    return list(dict.fromkeys(words + DATE.findall(text) + ids))


def runs(lines: list[tuple[int, str]]) -> list[tuple[int, str]]:
    """Comment lines on consecutive line numbers joined into one comment at its first line:
    runs([(3, "a"), (4, "b"), (9, "c")]) gives [(3, "a b"), (9, "c")]."""
    joined: list[tuple[int, int, str]] = []
    for number, text in lines:
        if joined and joined[-1][1] == number - 1:
            first, _, held = joined[-1]
            joined[-1] = (first, number, f"{held} {text}")
        else:
            joined.append((number, number, text))
    return [(first, text) for first, _, text in joined]


def python_comments(source: str) -> list[tuple[int, str]]:
    """A Python file's docstrings and `#` comments as (line, text), by line; source that does not parse gives []:
    a file whose first line is the docstring m and whose second is `x = 1  # one` gives [(1, "m"), (2, "one")]."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []
    found = [(getattr(node, "lineno", 1), " ".join(ast.get_docstring(node).split())) for node in ast.walk(tree)
             if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and ast.get_docstring(node)]
    hashes = [(token.start[0], token.string.lstrip("#").strip()) for token in tokenize.generate_tokens(io.StringIO(source).readline)
              if token.type == tokenize.COMMENT]
    return sorted(found + runs(hashes))


def hash_comments(source: str) -> list[tuple[int, str]]:
    """The `#` comments that open their line, a `#!` first line aside, as (line, text):
    hash_comments("#!/bin/sh\\n# a\\n# b\\nx=1 # c\\n") gives [(2, "a b")]."""
    lines = [(number, line.strip().lstrip("#").strip()) for number, line in enumerate(source.splitlines(), 1)
             if line.strip().startswith("#") and not line.startswith("#!")]
    return runs(lines)


def slash_comments(source: str) -> list[tuple[int, str]]:
    """The `//` comments that open their line and the lines of each `/* */` block, as (line, text):
    slash_comments("// a\\nx();\\n/* b\\n * c */\\n") gives [(1, "a"), (3, "b c")]."""
    lines: list[tuple[int, str]] = []
    inside = False
    for number, line in enumerate(source.splitlines(), 1):
        stripped = line.strip()
        if inside or stripped.startswith(("//", "/*")):
            lines.append((number, stripped.strip("/* ").strip()))
        if stripped.startswith("/*") or inside:
            inside = "*/" not in stripped
    return runs(lines)


def comments(path: Path) -> list[tuple[int, str]]:
    """A file's comments as (line, text) by its suffix or name; a kind of file that is not read gives []:
    a file a.sh holding "# a" gives [(1, "a")], a file a.json gives []."""
    kind = path.suffix or path.name
    if kind not in (".py", *HASH, *SLASH) and path.name not in HASH:
        return []
    source = path.read_text(errors="replace")
    if kind == ".py":
        return python_comments(source)
    return slash_comments(source) if kind in SLASH else hash_comments(source)


def governed(root: Path) -> list[Path]:
    """The tracked files under FOLDERS, test/fixtures/ aside, sorted: [root/"scripts/fast.sh", root/"test/test_todo.py"]."""
    kept = []
    for path in tracked_files(root):
        parts = path.relative_to(root).parts
        if parts[0] in FOLDERS and parts[:2] != FIXTURES:
            kept.append(path)
    return kept


def named(root: Path) -> list[tuple[str, int, list[str], str]]:
    """Every comment that gives a reason, as (file, line, markers, text), by file and line:
    [("scripts/x.py", 3, ["because"], "Sorted, because the caller compares.")]."""
    prefixes = decision_prefixes(root)
    found = []
    for path in governed(root):
        for line, text in comments(path):
            marks = markers(text, prefixes)
            if marks:
                found.append((path.relative_to(root).as_posix(), line, marks, text))
    return found


def problems(root: Path) -> list[str]:
    """One line per comment that gives a reason; none gives []:
    ["scripts/x.py:3 gives a reason in a comment (because); say what, and refer to a decision by id (C-042)"]."""
    return [f"{name}:{line} gives a reason in a comment ({', '.join(marks)}); say what, and refer to a decision by id (C-042)"
            for name, line, marks, _ in named(root)]


def main(argv: list[str]) -> int:
    """Prints the problems, or with --list each named comment's file, line, markers and text; 1 when any is named."""
    root = Path(__file__).resolve().parent.parent.parent
    found = named(root)
    if "--list" in argv:
        for name, line, marks, text in found:
            print(f"{name}:{line} [{', '.join(marks)}] {text}")
    else:
        print("\n".join(problems(root)))
    print(f"comments: {len(found)} give a reason")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
