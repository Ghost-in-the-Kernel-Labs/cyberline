"""docs/GLOSSARY.md's enforced aliases appear in no governed document (test/test_glossary.py).

Carried from Neon Rain's scripts/checks/glossary.py with the "Not governed" line added (C-011). It reads git's file
list (scripts/checks/common.py; C-001): a document on disk that git does not track is not read.
"""
import re
from pathlib import Path

from scripts.checks.common import matching, tracked_files

CODE_SPAN = re.compile(r"```.*?```|`[^`\n]*`", re.DOTALL)


def enforced_aliases(glossary: str) -> list[str]:
    """The backticked words of the table's third column ("Not"): "| a | b | x, `nn` |" gives ["nn"]."""
    aliases: list[str] = []
    for line in glossary.splitlines():
        cells = line.split("|")
        if len(cells) >= 5:
            aliases += re.findall(r"`([^`]+)`", cells[3])
    return aliases


def not_governed(glossary: str) -> list[str]:
    """The paths a "Not governed:" line exempts: "Not governed: `a.md`, `docs/b.md`." gives ["a.md", "docs/b.md"]."""
    for line in glossary.splitlines():
        if line.startswith("Not governed:"):
            return re.findall(r"`([^`]+)`", line)
    return []


def uses(text: str, alias: str) -> int:
    """How often `alias` is used as a word, outside code spans and outside a quotation of the word alone, which names
    it rather than uses it: uses('a `nn`, never "nn", and an nn, "an nn"', "nn") gives 2.

    Case is ignored unless the alias is in capitals: `NN` matches "NN" but not "HAR-nn".
    """
    prose = CODE_SPAN.sub(" ", text)
    if not alias.isupper():
        prose, alias = prose.lower(), alias.lower()
    prose = re.sub(rf"[\"“]{re.escape(alias)}[\"”]", " ", prose)
    return len(re.findall(rf"\b{re.escape(alias)}\b", prose))


def documents(root: Path, exempt: list[str]) -> list[Path]:
    """The governed documents: every tracked .md at the root and under docs/, but the glossary and the exempt paths."""
    files = tracked_files(root)
    found = matching(files, root, "*.md") + matching(files, root, "docs/**/*.md")
    exempt_paths = [root / path for path in exempt]
    return [path for path in found if path.name != "GLOSSARY.md" and path not in exempt_paths]


def problems(root: Path) -> list[str]:
    """Each governed document that uses an enforced alias, with the alias and the count; [] when clean."""
    glossary = (root / "docs" / "GLOSSARY.md").read_text()
    aliases = enforced_aliases(glossary)
    found: list[str] = []
    for path in documents(root, not_governed(glossary)):
        text = path.read_text()
        found += [f"{path.name} uses {alias!r} {uses(text, alias)} times" for alias in aliases if uses(text, alias)]
    return found
