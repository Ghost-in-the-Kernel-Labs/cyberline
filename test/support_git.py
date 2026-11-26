"""What the gate, commit and ship tests share: scratch git repositories holding copies of scripts/commit.sh or
scripts/gate.sh, the gate's tree record written as a passing gate writes it, and the two scripts run as an agent runs
them (C-037). test/test_gates.py, test/test_gate_failures.py, test/test_ship.py and test/test_metrics.py build on it."""
import os
import subprocess
import tempfile
from pathlib import Path

from scripts.checks import gate_record
from test.support import ROOT

COMMIT = str(ROOT / "scripts" / "commit.sh")
SECRETS = ROOT / "scripts" / "checks" / "secrets.py"


def git_out(root: Path, args: list[str]) -> str:
    """git's output in the scratch repository, stripped: git_out(root, ["log", "-1", "--format=%s"]) gives the subject."""
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout.strip()


def repo_with(commits: int) -> Path:
    """A scratch git repository with the given number of plain commits and a copy of the scripts commit.sh needs: itself,
    the secret scan and a fast loop stub that passes."""
    root = Path(tempfile.mkdtemp(prefix="ghost-core-gate-"))
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.name", "Someone"], check=True)
    subprocess.run(["git", "-C", str(root), "config", "user.email", "someone@example.invalid"], check=True)
    (root / "scripts" / "checks").mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "scripts" / "commit.sh").write_text(Path(COMMIT).read_text())
    (root / "scripts" / "checks" / "secrets.py").write_text(SECRETS.read_text())
    (root / "scripts" / "fast.sh").write_text("#!/usr/bin/env bash\nexit 0\n")
    for name in ("commit.sh", "fast.sh"):
        (root / "scripts" / name).chmod(0o755)
    if commits:
        subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", "plain 0"], check=True)
    # The rest as empty commits on main in one git process: the count is all the tune-up rule reads.
    stream = "".join(f"commit refs/heads/main\ncommitter Someone <someone@example.invalid> 1700000000 +0000\ndata {len(f'plain {n}')}\nplain {n}\n" + ("from refs/heads/main^0\n" if n == 1 else "") for n in range(1, commits))
    if stream:
        subprocess.run(["git", "-C", str(root), "fast-import", "--quiet"], input=stream, text=True, check=True)
    return root


def record(root: Path) -> str:
    """Writes the tree as it stands to .git/ghost/tree, as a passing scripts/gate.sh would, and gives its SHA."""
    sha = gate_record.tree(root)
    (root / ".git" / "ghost").mkdir(exist_ok=True)
    (root / ".git" / "ghost" / "tree").write_text(sha + "\n")
    return sha


def run_commit(root: Path, args: list[str], stdin: str | None = None, env: dict | None = None) -> subprocess.CompletedProcess:
    """scripts/commit.sh in the scratch repository with the arguments given: run_commit(root, ["-a", "-m", "x"])."""
    full = dict(os.environ, **(env or {}))
    return subprocess.run(["bash", "scripts/commit.sh", *args], cwd=root, input=stdin, capture_output=True, text=True, env=full)


def attempt(root: Path, subject: str) -> subprocess.CompletedProcess:
    """One commit of everything through the gated commit with the subject given, a file changed and the gate recorded first."""
    (root / "next.txt").write_text(subject)
    record(root)
    return run_commit(root, ["-a", "-m", subject])


# The gate's steps in a scratch repository: each a stub that says it ran, so the log can be told from the terminal. A
# Python step writes a file when the file touch-me exists, as a step that changes the tree; the fast loop is red when
# the file red exists. A stamped project's gate has no slow tests (scripts/stamp.py drop_stamp_gate).
STUB_FAST = "#!/usr/bin/env bash\necho \"stub fast loop ran $*\"\n[ ! -f red ]\n"
STUB_PY = "import pathlib, time\nprint('stub step ran')\nif pathlib.Path('touch-me').exists():\n    pathlib.Path('changed.txt').write_text(str(time.time_ns()))\n"


def gated_repo() -> Path:
    """A scratch git repository with one commit, a copy of scripts/gate.sh and scripts/checks/gate_record.py, stub steps
    and a .gitignore of /build/, the real one's rule."""
    root = Path(tempfile.mkdtemp(prefix="ghost-core-tree-"))
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    (root / "scripts" / "checks").mkdir(parents=True)
    for name in ("scripts/gate.sh", "scripts/checks/gate_record.py", "scripts/checks/secrets.py"):
        (root / name).write_text((ROOT / name).read_text())
    (root / "scripts" / "fast.sh").write_text(STUB_FAST)
    for name in ("gate.sh", "fast.sh"):
        (root / "scripts" / name).chmod(0o755)
    for name in ("decisions_index.py", "journal_index.py", "metrics.py"):
        (root / "scripts" / name).write_text(STUB_PY)
    (root / ".gitignore").write_text("/build/\n")
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=Ghost", "-c", "user.email=g@example.invalid", "commit", "-q", "-m", "start"], check=True)
    return root


def gate(root: Path) -> subprocess.CompletedProcess:
    """The scratch repository's gate, run as an agent runs it: `scripts/gate.sh`, nothing redirected, and warm though the
    real gate that runs this test is cold (it exports GHOST_COLD)."""
    env = {k: v for k, v in os.environ.items() if k != "GHOST_COLD"}
    return subprocess.run(["bash", "scripts/gate.sh"], cwd=root, capture_output=True, text=True, env=env)


def recorded(root: Path) -> str | None:
    """The scratch repository's tree record, read as commit.sh and ship.sh will read it."""
    return gate_record.record(root)
