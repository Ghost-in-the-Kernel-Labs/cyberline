"""docs/SUPPLY-CHAIN.md's rules a file can show (test/test_supply_chain.py; C-032, C-034): no hook, no folder-open
task, no worm artefact, and every workflow dispatch-only, SHA-pinned, least-privilege.

What the repository holds is read from git's file list (scripts/checks/common.py; C-001): a workflow git does not track
never runs on GitHub, so the workflow rules read the tracked ones. What the machine holds is read from the disk, on
purpose: a worm drops its files untracked and a hook runs from an untracked settings file, so the worm scan, the planted
folder's guard (which keeps the one folder that scan skips honest) and the hook rules walk the tree as it stands
(C-034, rule 7).

The agent files (4.4, C-039): every `.claude/agents/*.md` is listed in docs/SUPPLY-CHAIN.md's "Agent files" table with
its exact `tools:` line, its front matter holds no key outside AGENT_KEYS (Claude Code honours `permissionMode`, `hooks`
and `mcpServers` there, each a way to grant what the tools line does not), and the folder holds at most MAX_AGENTS files.
The folder is read from the disk, as the hooks are: an agent file a worm drops untracked is still loaded.

The auto-execution surfaces (C-039): every file that runs code by itself — the gate and commit scripts, each stack's
gate, the agent files, the workflows (SURFACES) — is listed in the "Auto-execution surfaces" table, and no row names a
file that is gone. Nothing is pinned to a hash: a change to a surface lands when its commit message names the decision
it carries (scripts/commit.sh, the commit check), which is what guards it. `python3 -I scripts/checks/supply_chain.py
--register` rewrites both tables from the tree as it stands.
"""
import json
import os
import re
import sys
from pathlib import Path

if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.checks.common import matching, tracked_files  # noqa: E402

WORM_FILES: frozenset[str] = frozenset({"setup_bun.js", "bun_environment.js", "Math_Symbol.js", "gh-token-monitor"})
# Folders never walked. git's and the installed packages are skipped at any depth; the venv, caches and every stack's
# tool output only at the root, where the stacks' anchored ignore entries (`/dist/`, `/reports/`) put them, so a worm
# file in a tracked `src/reports/` or `.claude/dist/` is still seen. A stack with another output folder adds it to
# ROOT_ONLY_DIRS (the TypeScript stack's .stryker-tmp, .tmp, dist, reports are here already).
SKIPPED_ANYWHERE: frozenset[str] = frozenset({".git", "node_modules"})
ROOT_ONLY_DIRS: frozenset[str] = frozenset({".venv", "mutants", "__pycache__", "build", ".stryker-tmp", ".tmp", "dist", "reports"})
PLANTED = Path("test") / "fixtures" / "broken" / "supply_chain"  # the one folder where the artefacts are planted on purpose
PLANTED_FILES: frozenset[str] = frozenset({".github/workflows/ci.yml", ".claude/settings.json", ".vscode/setup.mjs", "gh-token-monitor",
                                          "src/reports/setup_bun.js", "reports/setup_bun.js", "docs/SUPPLY-CHAIN.md",
                                          ".claude/agents/patch-reviewer.md", ".claude/agents/reputation-checker.md",
                                          ".claude/agents/third.md", "scripts/run.sh"})
FORBIDDEN_IN_WORKFLOWS: tuple[str, ...] = ("pull_request_target", "self-hosted", "toJSON(secrets)")
AGENTS = Path(".claude") / "agents"
AGENT_KEYS: frozenset[str] = frozenset({"name", "description", "tools", "model"})
MAX_AGENTS = 2  # the patch reviewer and the reputation checker (C-035); a third is a proposal for Ghost
DOC = Path("docs") / "SUPPLY-CHAIN.md"
AGENTS_HEADING = "## Agent files"
AGENTS_HEAD = "| Path | Tools |\n| --- | --- |\n"
SURFACES_HEADING = "## Auto-execution surfaces"
SURFACES_HEAD = "| Path | Kind |\n| --- | --- |\n"
# What runs code by itself, glob → kind. A stack's gate counts only while its PRESENT file exists in a stamped project;
# in this template every stack is present.
SURFACES: tuple[tuple[str, str], ...] = (("scripts/*.sh", "a script the gate or the commit runs"), ("stacks/*/gate.sh", "a stack's gate"),
                                         (".claude/agents/*.md", "an agent file"), (".github/workflows/*.y*ml", "a workflow"))


def ours(root: Path) -> list[Path]:
    """The disk, not git's list (a worm's files are untracked): every file under root but the ones git, the packages, the venv and the tools make: a folder in SKIPPED_ANYWHERE
    is not entered at any depth, one in ROOT_ONLY_DIRS only at the root ("reports/x" is skipped, "src/reports/x" is not)."""
    found = []
    for folder, names, files in os.walk(root):
        skipped = SKIPPED_ANYWHERE | (ROOT_ONLY_DIRS if Path(folder) == root else frozenset())
        names[:] = [n for n in names if n not in skipped]
        found += [Path(folder) / f for f in files if not (Path(folder) / f).relative_to(root).is_relative_to(PLANTED)]
    return sorted(found)


def planted_problems(root: Path) -> list[str]:
    """The planted folder holds exactly its listed files, so nothing real can hide in the one place the scan skips."""
    folder = root / PLANTED
    if not folder.is_dir():
        return []
    present = {str(p.relative_to(folder)) for p in folder.rglob("*") if p.is_file()}
    return [f"{PLANTED}/{name} is not a listed planted break" for name in sorted(present - PLANTED_FILES)]


def worm_problems(root: Path) -> list[str]:
    """The named worm artefacts, anywhere; setup.mjs only inside .claude/ or .vscode/ (rule 7)."""
    found: list[str] = []
    for path in ours(root):
        where = path.relative_to(root)
        in_editor_dir = where.parts[0] in (".claude", ".vscode")
        if path.name in WORM_FILES or (path.name == "setup.mjs" and in_editor_dir):
            found.append(f"{where} is a known worm artefact: stop, change nothing, report it")
    return found


# Decision: C-034 (rule 4: no hooks, no folder-open tasks, no git hooks)
def hook_problems(root: Path) -> list[str]:
    """A Claude Code hook, a folder-open task, a git hook, or core.hooksPath."""
    found: list[str] = []
    for name in ("settings.json", "settings.local.json"):
        path = root / ".claude" / name
        if path.is_file() and "hooks" in json.loads(path.read_text()):
            found.append(f".claude/{name} has hooks")
    tasks = root / ".vscode" / "tasks.json"
    if tasks.is_file() and "folderOpen" in tasks.read_text():
        found.append(".vscode/tasks.json runs a task on folder open")
    git = root / ".git"
    if git.is_dir():
        found += [f".git/hooks/{p.name} is a git hook" for p in sorted((git / "hooks").glob("*")) if not p.name.endswith(".sample")]
        if (git / "config").is_file() and "hookspath" in (git / "config").read_text().lower():
            found.append(".git/config sets core.hooksPath")
    return found


def triggers(workflow: str) -> list[str]:
    """The trigger names of a workflow's `on:` block: "on:\\n  push:\\n  workflow_dispatch:\\n" gives ["push", "workflow_dispatch"]."""
    block = re.search(r"^on:\s*\n((?:[ \t]+.*\n?)+)", workflow, re.MULTILINE)
    if block is None:
        inline = re.search(r"^on:\s*\[?([\w, ]+)\]?\s*$", workflow, re.MULTILINE)
        return [t.strip() for t in inline.group(1).split(",")] if inline else []
    return re.findall(r"^  (\w+):", block.group(1), re.MULTILINE)


# Decision: C-032 (a workflow runs by hand only; pinned; least privilege)
def workflow_problems(root: Path) -> list[str]:
    """Each tracked workflow with a trigger but workflow_dispatch, an action not pinned to a 40-hex SHA, no `permissions: contents: read` first, or a forbidden feature."""
    found: list[str] = []
    for path in matching(tracked_files(root), root, ".github/workflows/*.y*ml"):
        text = path.read_text()
        where = path.relative_to(root)
        found += [f"{where} runs on {t}, not by hand only" for t in triggers(text) if t != "workflow_dispatch"]
        for uses in re.findall(r"uses:\s*([^\s#]+)", text):
            if not re.search(r"@[0-9a-f]{40}$", uses):
                found.append(f"{where} uses {uses}, not pinned to a commit SHA")
        permissions = re.search(r"^permissions:\s*\n\s+contents:\s*read\s*$", text, re.MULTILINE)
        if permissions is None or re.search(r"^permissions:", text, re.MULTILINE).start() > text.find("jobs:"):
            found.append(f"{where} does not start with permissions: contents: read")
        found += [f"{where} uses {word}" for word in FORBIDDEN_IN_WORKFLOWS if word in text]
    return found


def front_matter(text: str) -> list[str]:
    """The lines between a file's opening `---` and the next: "---\\nname: a\\n---\\nbody" gives ["name: a"]; none, []."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return []
    end = next((i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---"), len(lines))
    return lines[1:end]


def agent_files(root: Path) -> list[Path]:
    """Every file in .claude/agents/ on the disk, sorted (a worm's untracked file included)."""
    folder = root / AGENTS
    return sorted(p for p in folder.iterdir() if p.is_file() or p.is_symlink()) if folder.is_dir() else []


def table(root: Path, heading: str) -> dict[str, str]:
    """A two-column table under `heading` in docs/SUPPLY-CHAIN.md, first cell → second cell, backticks stripped; {} when absent."""
    doc = root / DOC
    text = doc.read_text() if doc.is_file() else ""
    section = text.split(heading, 1)[1].split("\n## ", 1)[0] if heading in text else ""
    found = {}
    for line in section.splitlines():
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) == 2 and cells[0] not in ("Path", "---"):
            found[cells[0]] = cells[1]
    return found


def tools_line(path: Path) -> str:
    """A file's front-matter tools line, or "" when it has none or more than one."""
    tools = [line.strip() for line in front_matter(path.read_text(errors="replace")) if line.startswith("tools:")]
    return tools[0] if len(tools) == 1 else ""


# Decision: C-035 (the reviewers are read-only by construction: their tools lines are listed, their keys allow-listed)
def agent_problems(root: Path) -> list[str]:
    """Each agent file unlisted, granted another tools line or a key outside AGENT_KEYS; a row with no file; a third file."""
    found: list[str] = []
    files, listed = agent_files(root), table(root, AGENTS_HEADING)
    if len(files) > MAX_AGENTS:
        found.append(f"{AGENTS} holds {len(files)} files, more than {MAX_AGENTS}: a new agent is Ghost's to approve")
    for path in files:
        where = path.relative_to(root).as_posix()
        if path.is_symlink() or path.suffix != ".md":
            found.append(f"{where} is not an agent file (a link, or not .md)")
            continue
        keys = sorted({line.split(":", 1)[0].strip() for line in front_matter(path.read_text(errors="replace")) if re.match(r"^[A-Za-z][\w-]*\s*:", line)} - AGENT_KEYS)
        found += [f"{where} has front-matter key {key!r}, outside {sorted(AGENT_KEYS)}" for key in keys]
        if where not in listed:
            found.append(f"{where} is not listed in {DOC.as_posix()}'s Agent files table")
        elif listed[where] != tools_line(path):
            found.append(f"{where} has tools line {tools_line(path)!r}, listed {listed[where]!r}")
    present = {p.relative_to(root).as_posix() for p in files}
    return found + [f"{where} is listed in {DOC.as_posix()} but missing" for where in sorted(set(listed) - present)]


def surfaces(root: Path) -> dict[str, str]:
    """Every tracked file SURFACES names, path → kind, sorted by path."""
    found = {}
    for glob, kind in SURFACES:
        for path in matching(tracked_files(root), root, glob):
            found[path.relative_to(root).as_posix()] = kind
    return dict(sorted(found.items()))


# Decision: C-039 (the surfaces are an inventory, not pins: a change to one names its decision in the commit)
def surface_problems(root: Path) -> list[str]:
    """Each surface not in the Auto-execution surfaces table, and each row naming a file that is gone."""
    present, listed = surfaces(root), table(root, SURFACES_HEADING)
    found = [f"{where} runs code by itself and is not listed in {DOC.as_posix()}'s Auto-execution surfaces table" for where in present if where not in listed]
    return found + [f"{where} is listed as a surface in {DOC.as_posix()} but is gone" for where in sorted(set(listed) - set(present))]


def rewritten(text: str, heading: str, head: str, rows: str) -> str:
    """`text` with the table under `heading` replaced by `head` + `rows`, its prose kept; unchanged when the heading is absent."""
    if heading not in text:
        return text
    before, rest = text.split(heading, 1)
    body, tail = (rest.split("\n## ", 1) + [""])[:2]
    prose = body.split("\n| Path |", 1)[0].rstrip("\n")
    return f"{before}{heading}{prose}\n\n{head}{rows}" + (f"\n## {tail}" if tail else "")


def register(root: Path) -> str:
    """docs/SUPPLY-CHAIN.md with both tables rewritten from the tree as it stands; written, and returned."""
    doc = root / DOC
    text = doc.read_text()
    agents = "".join(f"| `{p.relative_to(root).as_posix()}` | `{tools_line(p)}` |\n" for p in agent_files(root))
    surface_rows = "".join(f"| `{where}` | {kind} |\n" for where, kind in surfaces(root).items())
    text = rewritten(rewritten(text, AGENTS_HEADING, AGENTS_HEAD, agents), SURFACES_HEADING, SURFACES_HEAD, surface_rows)
    doc.write_text(text)
    return text


def problems(root: Path) -> list[str]:
    """Everything the supply-chain rules refuse that a file can show; [] when the repository holds."""
    return worm_problems(root) + hook_problems(root) + workflow_problems(root) + agent_problems(root) + surface_problems(root) + planted_problems(root)


def main(argv: list[str]) -> int:
    """`--register` rewrites both tables and prints their rows; no argument prints the problems; exit 1 on any."""
    root = Path(__file__).resolve().parents[2]
    if argv == ["--register"]:
        register(root)
        print("\n".join([f"agent {path}: {tools}" for path, tools in table(root, AGENTS_HEADING).items()]
                        + [f"surface {path}: {kind}" for path, kind in table(root, SURFACES_HEADING).items()]))
        return 0
    found = problems(root)
    print("\n".join(found) if found else "supply chain: holds")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
