"""The contract document's invariants are numbered in sequence, and the leaf module and the document name the same
set (test/test_contract.py; C-012, CONTRACT XX-01). Carried from Neon Rain's harness_doc.py, prefix read from the file."""
import re
from pathlib import Path

from scripts.checks.common import tracked_files

HEADING = re.compile(r"^## ([A-Z]{2,4})-(\d{2}) ", re.MULTILINE)
SUFFIXES: tuple[str, ...] = (".py", ".java", ".ts", ".tsx", ".js", ".cpp", ".cc", ".hpp", ".h")


def prefix_of(document: str) -> str:
    """The invariants' prefix: a document whose first heading is "## HAR-01 x" gives "HAR"; none gives "XX"."""
    match = HEADING.search(document)
    return match.group(1) if match else "XX"


def invariants(document: str) -> list[str]:
    """The invariant ids in order: ["HAR-01", "HAR-02"]."""
    return [f"{p}-{n}" for p, n in HEADING.findall(document)]


def numbering_problems(document: str) -> list[str]:
    """Headings XX-01, XX-02, ... each once and with no gap."""
    numbers = invariants(document)
    prefix = prefix_of(document)
    found = [f"{n} appears {numbers.count(n)} times" for n in sorted(set(numbers)) if numbers.count(n) > 1]
    for position, number in enumerate(numbers, start=1):
        if number != f"{prefix}-{position:02d}":
            return found + [f"invariant {position} is {number}, expected {prefix}-{position:02d}"]
    return found


def code_references(folder: Path, prefix: str, root: Path | None = None) -> set[str]:
    """Every XX-nn named anywhere in the folder's source (a comment or a docstring counts); empty if no folder. The files
    are git's list for root (the repository the folder is in; C-001), so an untracked file is not read; without a root,
    the folder's own list (a fixture: walked)."""
    found: set[str] = set()
    for path in tracked_files(root or folder) if folder.is_dir() else []:
        if folder in path.parents and path.suffix in SUFFIXES:
            found |= set(re.findall(rf"\b{prefix}-\d{{2}}\b", path.read_text(errors="replace")))
    return found


def reference_problems(document: str, folder: Path, held: bool, root: Path | None = None) -> list[str]:
    """Both directions: what the code names that the document lacks (always), and, once `held`, what the document has that the code never names; root as code_references takes it."""
    prefix = prefix_of(document)
    documented = set(invariants(document))
    cited = code_references(folder, prefix, root)
    found = [f"{folder.name}/ names {n}, which the contract does not have" for n in sorted(cited - documented)]
    if held:
        found += [f"{n} is in the contract and nowhere in {folder.name}/" for n in sorted(documented - cited)]
    return found
