"""What every doc test shares: the repository root, and a scratch root a planted break is built in."""
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BROKEN = ROOT / "test" / "fixtures" / "broken"


def scratch() -> Path:
    """A fresh empty directory with a docs/ folder, e.g. /tmp/ghost-core-abc123."""
    root = Path(tempfile.mkdtemp(prefix="ghost-core-"))
    (root / "docs").mkdir()
    return root
