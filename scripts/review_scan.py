"""The rule-based scan of a dependency update's diff (docs/DEPENDENCY-REVIEW.md step 2; C-035).

    python3 -I scripts/review_scan.py --unpack <old-archive> <new-archive> <review-folder>
    python3 -I scripts/review_scan.py <review-folder>

With --unpack it makes the folder (new or empty, and never inside this repository) and unpacks each archive into old/
and new/: a tarball by `tar --no-same-owner --no-same-permissions`, so no owner and no mode bit (setuid) comes from the
archive and GNU tar refuses a member named with `..`; a zip (a wheel, a jar) by the standard library, which keeps no
owner or mode, its symlink and special members never written. Either way the scan first lists every entry of either
side that is neither a file nor a folder, `link: new/package/.npmrc -> /home/x/.npmrc` or `special: new/package/p`
(a FIFO, a device, a socket), into listing.txt, and opens none of them: `diff` follows a link and would copy its target,
a file outside the folder, into package.diff, and a FIFO would hang it. A listing that flagged anything stops the scan
before any diff is written, with one line naming what it flagged (exit 3); so does a folder inside this repository.

The folder holds old/ and new/, each the unpacked package. The scan pairs renamed bundled chunks (run.BPv-BBRv.js
with run.Cx91aQ0e.js) so a rebuild does not read as thousands of new lines, writes files.diff (files added and
removed), package.diff (the paired diff), scripts.diff (install hooks before and after) and scan.txt (every rule's
hit with its file and line), and exits 1 when there is any hit. A hit is not proof of malice; it is a hunk the
reviewer must explain. Fixed rules, no judgement, nothing to talk round. Nothing in the folder is executed.
"""
import json
import os
import re
import stat
import subprocess
import sys
import zipfile
from pathlib import Path

HOOKS: tuple[str, ...] = ("preinstall", "install", "postinstall", "prepare", "setup")
LARGE_FILE = 100 * 1024
RULES: tuple[tuple[str, str], ...] = (
    (r"\b(NPM_TOKEN|NODE_AUTH_TOKEN|GITHUB_TOKEN|GH_TOKEN|AWS_\w*KEY|AZURE_\w*SECRET|GOOGLE_APPLICATION_CREDENTIALS)\b|\.npmrc|\.pypirc|id_rsa", "token theft"),
    (r"\b(trufflehog|gitleaks)\b", "a secret scanner bundled in"),
    (r"\.github/workflows|actions/checkout|\bgit\s+push\b", "a foothold in CI"),
    (r"\bnpm (publish|whoami)\b|\btwine upload\b|registry\.npmjs\.org/-/|upload\.pypi\.org", "self-propagation"),
    (r"\b(curl|wget|powershell|Invoke-WebRequest)\b|\bbash -c\b", "running a second stage"),
    (r"webhook\.site|pastebin|ngrok|discord(app)?\.com/api/webhooks|\b\d{1,3}(\.\d{1,3}){3}\b", "sending data out"),
    (r"\beval\(|new Function\(|\batob\(|Buffer\.from\([^)]*['\"]base64['\"]|\bexec\(|\bcompile\(|__import__\(", "hiding code"),
    (r"[A-Za-z0-9+/=]{200,}|(\\x[0-9a-fA-F]{2}){40,}", "a long encoded string"),
    (r"JSON\.stringify\(process\.env\)|Object\.keys\(process\.env\)|dict\(os\.environ\)|os\.environ\.copy\(\)", "dumping secrets"),
)
HASHED = re.compile(r"^(.*?)[.-][A-Za-z0-9_-]{6,12}(\.[a-z]+)$")
REPOSITORY = Path(__file__).resolve().parents[1]
TAR_FLAGS: tuple[str, ...] = ("--no-same-owner", "--no-same-permissions")


class Refused(Exception):
    """A scan that stops before any diff: the folder is inside the repository, an archive would not unpack, or the
    listing flagged a link or a special file. Its message is the one line main prints."""


# Decision: C-035 (the review folder is outside the project; nothing in it is executed or followed)
def refuse_inside_repository(folder: Path) -> None:
    """Raises Refused when the folder is this repository's root or under it: a review folder is outside the project."""
    if folder.resolve().is_relative_to(REPOSITORY):
        raise Refused(f"refused: {folder} is inside the repository ({REPOSITORY}); make the review folder with mktemp -d")


def specials(root: Path, side: str) -> list[str]:
    """Every entry under root that is neither a file nor a folder, by lstat, never opened or followed: a symlink gives
    "link: new/package/.npmrc -> /home/x/.npmrc", a FIFO, device or socket gives "special: new/package/p"."""
    found = []
    for folder, names, files in os.walk(root):
        for name in sorted(names + files):
            path = Path(folder) / name
            mode = os.lstat(path).st_mode
            where = f"{side}/{path.relative_to(root).as_posix()}"
            if stat.S_ISLNK(mode):
                found.append(f"link: {where} -> {os.readlink(path)}")
            elif not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
                found.append(f"special: {where}")
    return sorted(found)


def unzip(archive: Path, into: Path, side: str) -> list[str]:
    """A zip's members written under into, no owner and no mode kept; a symlink member is listed by the text it holds
    and a special member by its name, neither written (a member with no file type, as many zips write, is a file); a member named with `..` or from the root refuses the archive."""
    flagged = []
    with zipfile.ZipFile(archive) as packed:
        for info in packed.infolist():
            parts = Path(info.filename).parts
            if info.filename.startswith("/") or ".." in parts:
                raise Refused(f"refused: {archive.name} has a member named {info.filename!r}")
            mode = info.external_attr >> 16
            if stat.S_ISLNK(mode):
                flagged.append(f"link: {side}/{info.filename} -> {packed.read(info).decode('utf-8', 'replace')}")
            elif stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR):
                flagged.append(f"special: {side}/{info.filename}")
            else:
                packed.extract(info, into)
    return flagged


def unpack(archive: Path, into: Path, side: str) -> list[str]:
    """One archive into a new folder: a zip by unzip(), anything else by tar with TAR_FLAGS; returns what the zip
    flagged (tar's links stay on disk for specials() to list). A tar that exits non-zero refuses with its first line."""
    into.mkdir(parents=True)
    if zipfile.is_zipfile(archive):
        return unzip(archive, into, side)
    done = subprocess.run(["tar", "-xf", str(archive.resolve()), "-C", str(into), *TAR_FLAGS], capture_output=True, text=True)
    if done.returncode != 0:
        raise Refused(f"refused: tar could not unpack {archive.name}: {(done.stderr.strip().splitlines() or ['exit ' + str(done.returncode)])[0]}")
    return []


def prepare(old: Path, new: Path, folder: Path) -> list[str]:
    """The review folder made (new or empty, outside the repository) with old/ and new/ unpacked; what the zips flagged."""
    refuse_inside_repository(folder)
    if folder.exists() and any(folder.iterdir()):
        raise Refused(f"refused: {folder} is not empty; make a new one with mktemp -d")
    return unpack(old, folder / "old", "old") + unpack(new, folder / "new", "new")


def listing(folder: Path, flagged: list[str]) -> None:
    """Writes listing.txt (what the unpacking flagged and what lstat finds on either side) and raises Refused, naming
    each on one line, when it holds anything: nothing flagged is ever diffed."""
    found = flagged + specials(folder / "old", "old") + specials(folder / "new", "new")
    (folder / "listing.txt").write_text("\n".join(found) + "\n" if found else "no links or special files\n")
    if found:
        raise Refused(f"refused to diff: the listing flagged {len(found)}: " + "; ".join(found))


def package_root(side: Path) -> Path:
    """The unpacked package's root: side/package when the archive had that folder (npm), else side itself."""
    return side / "package" if (side / "package").is_dir() else side


def files_of(root: Path) -> list[str]:
    """Every file under the root, relative, sorted: a package with lib/a.js and package.json gives both."""
    return sorted(str(p.relative_to(root)) for p in root.rglob("*") if p.is_file())


def unhashed(name: str) -> str:
    """A hashed chunk's name without its hash: "run.BPv-BBRv.js" gives "run.js"; "index.js" stays."""
    match = HASHED.match(name)
    return f"{match.group(1)}{match.group(2)}" if match else name


def pairings(old: list[str], new: list[str]) -> dict[str, str]:
    """Renamed chunks paired across the sides, old→new, wherever an unhashed name belongs to one file on each side."""
    by_old = {}
    by_new = {}
    for name in old:
        by_old.setdefault(unhashed(name), []).append(name)
    for name in new:
        by_new.setdefault(unhashed(name), []).append(name)
    paired = {}
    for key, olds in by_old.items():
        news = by_new.get(key, [])
        if len(olds) == 1 and len(news) == 1 and olds[0] != news[0]:
            paired[olds[0]] = news[0]
    return paired


def apply_pairings(root: Path, renames: dict[str, str]) -> None:
    """Renames each chunk in the folder to its unhashed name, so the two sides diff file to file."""
    for name in renames:
        path = root / name
        path.rename(path.parent / unhashed(path.name))


def hooks_of(root: Path) -> dict[str, str]:
    """The install hooks a manifest declares: package.json's scripts named in HOOKS; setup.py's presence for PyPI."""
    manifest = root / "package.json"
    if manifest.is_file():
        scripts = json.loads(manifest.read_text(errors="replace")).get("scripts", {})
        return {k: v for k, v in scripts.items() if k in HOOKS}
    return {"setup.py": "present"} if (root / "setup.py").is_file() else {}


def large_or_minified(root: Path, added: list[str]) -> list[str]:
    """Added files over LARGE_FILE bytes, or minified (a line over 1,000 characters), as hits."""
    hits = []
    for name in added:
        path = root / name
        size = path.stat().st_size
        if size > LARGE_FILE:
            hits.append(f"{name}: new file of {size // 1024} KB (where a payload hides)")
        elif path.suffix in (".js", ".mjs", ".cjs", ".py") and any(len(line) > 1000 for line in path.read_text(errors="replace").splitlines()[:50]):
            hits.append(f"{name}: new minified file (where a payload hides)")
    return hits


STARTUP = re.compile(r"(^|/)([^/]+\.pth|sitecustomize\.py|usercustomize\.py)$")


def startup_files(old_root: Path, new_root: Path, new: list[str]) -> list[str]:
    """Each `.pth`, sitecustomize.py or usercustomize.py the new side adds or changes, as a hit: Python runs them at every
    interpreter start, installed or not imported (a wheel's door, as an install hook is npm's). Never routine."""
    return [f"{name}: a Python startup file {'changed' if (old_root / name).is_file() else 'added'} (runs at every interpreter start; never routine)"
            for name in new if STARTUP.search(name) and (not (old_root / name).is_file() or (old_root / name).read_bytes() != (new_root / name).read_bytes())]


def scan_lines(diff: str) -> list[str]:
    """Each rule's hit in the diff's added lines, with the file and the line: "lib/a.js:+ eval(x) (hiding code)"."""
    hits = []
    current = "?"
    for line in diff.splitlines():
        if line.startswith("+++ "):
            path = line[4:].split("\t")[0]
            current = path.split("/new/", 1)[1].removeprefix("package/") if "/new/" in path else path
        elif line.startswith("+") and not line.startswith("+++"):
            for pattern, why in RULES:
                if re.search(pattern, line):
                    hits.append(f"{current}: {line[1:].strip()[:120]} ({why})")
    return hits


def scan(folder: Path, flagged: list[str] | None = None) -> list[str]:
    """Runs the whole scan on a review folder and writes its four files; returns the hits. Refused (nothing diffed) for a
    folder inside the repository or a listing that flagged anything, the unpacking's own flags among them."""
    refuse_inside_repository(folder)
    listing(folder, flagged or [])
    old_root, new_root = package_root(folder / "old"), package_root(folder / "new")
    old_files, new_files = files_of(old_root), files_of(new_root)
    renames = pairings(old_files, new_files)
    apply_pairings(old_root, renames)
    apply_pairings(new_root, {v: k for k, v in renames.items()})
    old_files, new_files = files_of(old_root), files_of(new_root)
    added = sorted(set(new_files) - set(old_files))
    removed = sorted(set(old_files) - set(new_files))
    (folder / "files.diff").write_text(f"paired {len(renames)} renamed chunks\n" + "".join(f"+ {n}\n" for n in added) + "".join(f"- {n}\n" for n in removed))
    diff = subprocess.run(["diff", "-ruN", str(old_root), str(new_root)], capture_output=True, text=True, errors="replace").stdout
    (folder / "package.diff").write_text(diff)
    old_hooks, new_hooks = hooks_of(old_root), hooks_of(new_root)
    (folder / "scripts.diff").write_text(f"old: {json.dumps(old_hooks, sort_keys=True)}\nnew: {json.dumps(new_hooks, sort_keys=True)}\n")
    hits = [f"{k}: install hook {'changed' if k in old_hooks else 'added'}: {v} (the worm's door)" for k, v in new_hooks.items() if old_hooks.get(k) != v]
    hits += startup_files(old_root, new_root, new_files)
    hits += large_or_minified(new_root, added)
    hits += scan_lines(diff)
    (folder / "scan.txt").write_text("\n".join(hits) + ("\n" if hits else "no hits\n"))
    return hits


def main(argv: list[str]) -> int:
    """Unpacks (with --unpack) and scans the folder named; prints the hits; 1 when there are any, 3 when refused."""
    if len(argv) not in (1, 4) or (len(argv) == 4) != (argv[0] == "--unpack"):
        print(__doc__)
        return 2
    folder = Path(argv[-1]).absolute()
    try:
        flagged = prepare(Path(argv[1]), Path(argv[2]), folder) if len(argv) == 4 else []
        hits = scan(folder.resolve(), flagged)
    except Refused as refusal:
        print(f"review scan: {refusal}")
        return 3
    print("\n".join(hits) if hits else "review scan: no hits")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
