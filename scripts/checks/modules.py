"""Every import under the modules' folders is one docs/modules.json allows, and a module with entry points is
reached only through them (test/test_modules.py; C-012). Imports are read by pattern, one family per file suffix.

Python: `import a.b`, `import json, a.b as c`, `from a.b import c`, `from ..leaf import x`, `from . import y`,
`from a import (b, c)`. Java: `import a.b.C;`, `import static a.b.C.d;`. TypeScript/JavaScript: `from "a/b"`
(import and export), `import "a/b"` (side effect), `import("a/b")` (dynamic), `require("a/b")` (and
`import x = require("a/b")`). C++: `#include "a/b.h"`. The module of an import is the segment after the package
prefix; `test/test_modules.py`'s table lists every form read, and a form it lacks is one row to add.
"""
import json
import os
import re
import sys
from pathlib import Path

from scripts.checks.common import matching, tracked_files

PY_IMPORT = re.compile(r"^[ \t]*import[ \t]+([\w.]+(?:[ \t]+as[ \t]+\w+)?(?:[ \t]*,[ \t]*[\w.]+(?:[ \t]+as[ \t]+\w+)?)*)", re.MULTILINE)
PY_FROM = re.compile(r"^[ \t]*from[ \t]+(\.*[\w.]*)[ \t]+import[ \t]+(\([^)]*\)|[\w*, \t]+)", re.MULTILINE)
JAVA_IMPORT = re.compile(r"^\s*import\s+(?:static\s+)?([\w.]+)\s*;", re.MULTILINE)
SCRIPT_IMPORT = re.compile(
    r"\bfrom\s*['\"]([^'\"]+)['\"]"  # import … from "x", export … from "x", across lines
    r"|^\s*import\s*['\"]([^'\"]+)['\"]"  # import "x" (a side effect)
    r"|\bimport\s*\(\s*['\"]([^'\"]+)['\"]\s*\)"  # import("x") (dynamic)
    r"|\brequire\s*\(\s*['\"]([^'\"]+)['\"]\s*\)",  # require("x"), import x = require("x")
    re.MULTILINE,
)
INCLUDE = re.compile(r"^\s*#include\s+\"([^\"]+)\"", re.MULTILINE)
SUFFIXES: tuple[str, ...] = (".py", ".java", ".ts", ".tsx", ".js", ".cpp", ".cc", ".hpp", ".h")
NATIVE: tuple[str, ...] = (".cpp", ".cc", ".hpp", ".h")  # quoted includes are the project's own; outside packages are not read there
NODE_BUILTINS = {"fs", "path", "os", "url", "util", "crypto", "http", "https", "child_process", "stream", "events", "buffer", "assert", "zlib", "net", "readline", "process"}
Import = tuple[str, tuple[str, ...]]  # (the target as written, the names imported from it)


def spec_of(root: Path) -> dict:
    """docs/modules.json parsed."""
    return json.loads((root / "docs" / "modules.json").read_text())


def module_of(path: Path, root: Path, spec: dict) -> str | None:
    """The module whose folder holds the file, or None: src/leaf/x.py with folder src/leaf gives "leaf"."""
    for name, entry in spec["modules"].items():
        if path.is_relative_to(root / entry["folder"]):
            return name
    return None


def bare(name: str) -> str:
    """A name without its alias: "sizes as s" gives "sizes"; "LIMIT" gives "LIMIT"."""
    return name.split(" as ")[0].strip()


def python_imports(source: str) -> list[Import]:
    """Python's imports: "import json, a.b as c" gives [("json", ()), ("a.b", ())]; "from ..leaf import x as y" gives [("..leaf", ("x",))]."""
    found: list[Import] = []
    for match in PY_IMPORT.finditer(source):
        found += [(bare(name), ()) for name in match.group(1).split(",")]
    for match in PY_FROM.finditer(source):
        names = re.sub(r"\s+", " ", match.group(2).strip("()")).split(",")
        found.append((match.group(1), tuple(bare(n) for n in names if bare(n) and bare(n) != "*")))
    return found


def java_imports(source: str) -> list[Import]:
    """Java's imports: "import static a.b.C.d;" gives [("a.b.C.d", ())]."""
    return [(match.group(1), ()) for match in JAVA_IMPORT.finditer(source)]


def script_imports(source: str) -> list[Import]:
    """TypeScript's and JavaScript's: `import x from "a"`, `export * from "a"`, `import "a"`, `import("a")` and `require("a")` each give ("a", ())."""
    return [(next(group for group in match.groups() if group), ()) for match in SCRIPT_IMPORT.finditer(source)]


def native_includes(source: str) -> list[Import]:
    """C and C++'s quoted includes: '#include "app/leaf/sizes.h"' gives [("app/leaf/sizes.h", ())]."""
    return [(match.group(1), ()) for match in INCLUDE.finditer(source)]


FAMILIES = {".py": python_imports, ".java": java_imports, ".ts": script_imports, ".tsx": script_imports, ".js": script_imports}


def raw_targets(source: str, suffix: str) -> list[Import]:
    """Each import of a file with the suffix given, as written, by the reader of its family: ("from a.b import c", ".py") gives [("a.b", ("c",))]."""
    return FAMILIES.get(suffix, native_includes)(source)


def dotted(target: str) -> str:
    """A target written with slashes, as dots: "app/leaf/sizes.h" gives "app.leaf.sizes"."""
    return target.replace("/", ".").removesuffix(".h").removesuffix(".hpp")


def targets(source: str, suffix: str) -> list[Import]:
    """Each import's (target, names), dotted: ("from a.b import c, d", ".py") gives [("a.b", ("c", "d"))]."""
    return [(dotted(target), names) for target, names in raw_targets(source, suffix)]


def as_path(target: str) -> str:
    """A Python relative target as the relative path it means, a TypeScript one as written: "..leaf.sizes" gives "../leaf/sizes", "." gives "./"."""
    dots = len(target) - len(target.lstrip("."))
    if not dots or target[dots:].startswith("/"):
        return target
    rest = target[dots:].replace(".", "/")
    return ("./" if dots == 1 else "../" * (dots - 1)) + rest


def resolve(target: str, path: Path, root: Path, spec: dict) -> str:
    """A relative target (TypeScript "./", "../"; Python ".x", "..x") as a dotted target in our package when it lands in
    a module's folder, else as written.

    From src/cli/main.ts, "../leaf/sizes.js" with package "app." and leaf folder src/leaf gives "app.leaf.sizes";
    from src/cli/main.py, "..leaf.sizes" gives the same.
    """
    target = as_path(target)
    if not target.startswith(("./", "../")):
        return dotted(target)
    landed = Path(os.path.normpath(path.parent / target))
    for name, entry in spec["modules"].items():
        folder = root / entry["folder"]
        if landed.is_relative_to(folder):
            inside = [part for part in landed.relative_to(folder).with_suffix("").parts if part != "."] if landed != folder else []
            return ".".join([spec["package"].replace("/", ".").rstrip("."), name, *inside])
    return dotted(target)


def ours(target: str, package: str, spec: dict) -> str | None:
    """The module an import target names, if it is one of ours: with package "pkg." and modules {leaf}, "pkg.leaf.x" gives "leaf"."""
    prefix = package.replace("/", ".")
    rest = target.removeprefix(prefix).lstrip(".") if target.startswith(prefix) else None
    if rest is None:
        return None
    head = rest.split(".")[0]
    return head if head in spec["modules"] else None


def reached(target: str, names: tuple[str, ...], package: str) -> list[str]:
    """The dotted names an import reaches inside our package: ("pkg.leaf.sizes", ("A", "B")) gives ["leaf.sizes.A", "leaf.sizes.B"]."""
    inner = target.removeprefix(package.replace("/", ".")).lstrip(".")
    return [f"{inner}.{n}" for n in names] if names else [inner]


def joined(written: str, name: str) -> str:
    """A name imported from a Python target, as a target of its own: ("app", "leaf") gives "app.leaf", ("..", "leaf") gives "..leaf"."""
    return written + name if written.endswith(".") else f"{written}.{name}"


def units(written: str, names: tuple[str, ...], path: Path, root: Path, spec: dict) -> list[Import]:
    """The imports one statement makes, resolved. A from-import whose target is none of our modules but whose names are
    ("from app import leaf", "from .. import leaf") gives each such name as an import of its own, [("app.leaf", ())];
    any other statement gives itself, [(resolved target, names)]."""
    target = resolve(written, path, root, spec)
    if not names or ours(target, spec["package"], spec) is not None:
        return [(target, names)]
    named = [resolve(joined(written, name), path, root, spec) for name in names]
    inner: list[Import] = [(each, ()) for each in named if ours(each, spec["package"], spec) is not None]
    return inner or [(target, names)]


def within(target: str, name: str) -> bool:
    """Whether the dotted target is the package `name` or inside it: ("numpy.linalg", "numpy") and ("@a.b.c", "@a/b") are True, ("numpyx", "numpy") False."""
    package = dotted(name)
    return target == package or target.startswith(package + ".")


def is_stdlib(written: str, target: str, path: Path) -> bool:
    """Whether an import is the stack's own standard library: Python's module names, Java's java. and javax., Node's `node:` and core modules."""
    head = target.split(".")[0]
    if path.suffix == ".py":
        return head in sys.stdlib_module_names
    if path.suffix == ".java":
        return head in ("java", "javax")
    return written.startswith("node:") or written in NODE_BUILTINS


def outside_problems(path: Path, written: str, imported: Import, module: str, spec: dict) -> list[str]:
    """What an outside import breaks: a forbidden package (MOD-03) unless the module's `outside` names it, or a package its
    `outside` list lacks. A name imported from the target counts as inside it: "from google import genai" is google.genai."""
    target, names = imported
    if written.startswith(".") or path.suffix in NATIVE or is_stdlib(written, target, path) or target == dotted(spec["package"]).rstrip("."):
        return []
    candidates = [target, *(f"{target}.{name}" for name in names)]
    listed = spec["modules"][module].get("outside")
    named = listed is not None and any(within(each, name) for each in candidates for name in listed)
    if not named and any(within(each, name) for each in candidates for name in spec.get("forbidden", [])):
        return [f"imports {target}: a forbidden package; no module may import it unless its `outside` list names it (MOD-03)"]
    if listed is not None and not named:
        return [f"imports {target}: {module} may import only the outside packages {listed}"]
    return []


# Decision: C-012 (a new module or a new import between modules is a decision an agent proposes and stops)
def file_problems(path: Path, root: Path, spec: dict) -> list[str]:
    """Every module rule one file breaks: an import of a module not in mayImport, or past its entry points."""
    module = module_of(path, root, spec)
    if module is None:
        return []
    allowed = spec["modules"][module]["mayImport"]
    where = str(path.relative_to(root))
    found: list[str] = []
    for written, names in raw_targets(path.read_text(errors="replace"), path.suffix):
        for target, reach in units(written, names, path, root, spec):
            other = ours(target, spec["package"], spec)
            if other is None:
                found += [f"{where} {text}" for text in outside_problems(path, written, (target, reach), module, spec)]
            if other is None or other == module:
                continue
            if other not in allowed:
                found.append(f"{where} imports {other}: {module} may import only {allowed}")
                continue
            points = spec["modules"][other].get("entryPoints", [])
            found += [f"{where} reaches {name}: {other}'s entry points are {points} (MOD-04)" for name in reached(target, reach, spec["package"]) if points and name not in points and name != other]
    return found


def problems(root: Path) -> list[str]:
    """Every module rule broken in the tracked files under the modules' folders (scripts/checks/common.py; C-001); []
    when the folders do not exist yet."""
    spec = spec_of(root)
    files = tracked_files(root)
    found: list[str] = []
    for entry in spec["modules"].values():
        for path in matching(files, root, f"{entry['folder']}/**/*"):
            if path.suffix in SUFFIXES:
                found += file_problems(path, root, spec)
    leaf = spec.get("leaf")
    if leaf in spec["modules"] and spec["modules"][leaf]["mayImport"]:
        found.append(f"the leaf module {leaf!r} may import {spec['modules'][leaf]['mayImport']}; it imports nothing of ours (MOD-01)")
    return sorted(found)
