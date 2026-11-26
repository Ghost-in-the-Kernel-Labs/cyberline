"""No instruction names a model; only docs/when/grades.md maps grades to models (test/test_grades.py; C-036).

Governs what an agent is instructed by: CLAUDE.md, docs/when/*.md but grades.md, docs/paths/*.md,
docs/AGENT.md, docs/HANDOFF.md, README.md and every file under scripts/stamp_templates/. A model's name
(Haiku, Sonnet, Opus, Fable: a whole word, any case) there is a failure, unless it is inside a backtick
code span or a fenced block, where it is a value (an Agent tool's `model: "opus"`), not an instruction.
The records say who did what and are exempt (EXEMPT); they are also outside the governed paths. It reads git's file
list (scripts/checks/common.py; C-001): a file on disk that git does not track is not read.
"""
import re
from pathlib import Path

from scripts.checks.common import matching, tracked_files

MODEL = re.compile(r"\b(haiku|sonnet|opus|fable)\b", re.IGNORECASE)
FENCED = re.compile(r"^```.*?^```", re.MULTILINE | re.DOTALL)
SPAN = re.compile(r"(`+)(?:(?!\1).)+?\1")
MAP = "docs/when/grades.md"
GOVERNED: tuple[str, ...] = ("CLAUDE.md", "docs/when/*.md", "docs/paths/*.md", "docs/AGENT.md", "docs/HANDOFF.md",
                             "README.md", "scripts/stamp_templates/*")
EXEMPT: tuple[str, ...] = ("theGhost.md", "docs/journal/", "docs/NAVIGATION-LOG.md", "docs/ESCALATIONS.md", "docs/FINDINGS.md",
                           "docs/LESSONS*.md", "docs/SHARED-DECISIONS-DRAFT.md", "docs/LINEAGE.md", "docs/GHOST-IN-THE-KERNEL.md")


def blanked(match: re.Match[str]) -> str:
    """The matched text with every character but a newline made a space: "`a`" gives "   "."""
    return re.sub(r"[^\n]", " ", match.group(0))


def outside_code(text: str) -> str:
    """The text with fenced blocks and code spans blanked, so line numbers and columns hold.

    "a `opus` b" gives "a        b"; a fenced block naming a model keeps its lines, blank.
    """
    return SPAN.sub(blanked, FENCED.sub(blanked, text))


def governed(root: Path) -> list[Path]:
    """The files the check reads under root, sorted, the map left out: CLAUDE.md, docs/when/x.md, ..."""
    files = tracked_files(root)
    found = {path for pattern in GOVERNED for path in matching(files, root, pattern)}
    return sorted(path for path in found if path.relative_to(root).as_posix() != MAP)


def named(text: str) -> list[tuple[int, str]]:
    """Each model name outside code, with its line: "a\\nthe Opus agent `opus`" gives [(2, "Opus")]."""
    found: list[tuple[int, str]] = []
    for number, line in enumerate(outside_code(text).splitlines(), start=1):
        found += [(number, match.group(1)) for match in MODEL.finditer(line)]
    return found


# Decision: C-036 (the grade-to-model map lives in one file; a model's name anywhere else is refused)
def problems(root: Path) -> list[str]:
    """Each model name in a governed file: "docs/when/x.md:3 names Sonnet; name the grade (docs/when/grades.md)"."""
    found: list[str] = []
    for path in governed(root):
        for number, word in named(path.read_text()):
            found.append(f"{path.relative_to(root).as_posix()}:{number} names {word}; name the grade ({MAP})")
    return found
