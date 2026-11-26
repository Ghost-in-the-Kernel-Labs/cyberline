"""docs/modules.json holds the modules' imports; and planted breaks, one per import form, are caught (C-012)."""
import json
import unittest

from scripts.checks import modules
from test.support import BROKEN, ROOT


class TheRepository(unittest.TestCase):
    def test_the_real_graph_holds(self) -> None:
        self.assertEqual(modules.problems(ROOT), [])

    def test_the_real_json_has_the_three_slots(self) -> None:
        spec = modules.spec_of(ROOT)
        self.assertEqual(spec["leaf"], "leaf")
        self.assertEqual(spec["modules"]["leaf"]["mayImport"], [])
        self.assertEqual(spec["modules"]["cli"]["mayImport"], ["project"])

    def test_the_planted_breaks_are_caught(self) -> None:
        self.assertEqual(modules.problems(BROKEN / "modules"), [
            "src/cli/Main.java imports leaf: cli may import only ['project']",
            "src/cli/ask.ts imports @anthropic-ai.sdk: a forbidden package; no module may import it unless its `outside` list names it (MOD-03)",
            "src/cli/defaulted.ts imports leaf: cli may import only ['project']",
            "src/cli/dynamic.ts imports leaf: cli may import only ['project']",
            "src/cli/dynamic_model.ts imports @anthropic-ai.sdk: a forbidden package; no module may import it unless its `outside` list names it (MOD-03)",
            "src/cli/from_package.py imports leaf: cli may import only ['project']",
            "src/cli/plain_require.js imports leaf: cli may import only ['project']",
            "src/cli/relative.ts imports leaf: cli may import only ['project']",
            "src/cli/required.ts imports leaf: cli may import only ['project']",
            "src/cli/several.py imports leaf: cli may import only ['project']",
            "src/cli/side_effect.ts imports leaf: cli may import only ['project']",
            "src/cli/typed.ts imports leaf: cli may import only ['project']",
            "src/cli/up_dots.py imports leaf: cli may import only ['project']",
            "src/cli/up_relative.py imports leaf: cli may import only ['project']",
            "src/project/fetch.py imports numpy.linalg: project may import only the outside packages ['requests']",
            "src/project/run.py reaches leaf.sizes.SECRET: leaf's entry points are ['leaf.sizes.LIMIT'] (MOD-04)",
        ])


# Every import form the check reads: (suffix, source, what raw_targets gives). A form the check misses is one row here,
# and a planted break under test/fixtures/broken/modules/ when it can cross modules (1.27).
FORMS = [
    (".py", "import a.b\n", [("a.b", ())]),
    (".py", "import json, app.leaf as l\n", [("json", ()), ("app.leaf", ())]),
    (".py", "from a.b import c, d as e\n", [("a.b", ("c", "d"))]),
    (".py", "from a.b import (\n    c,\n    d,\n)\n", [("a.b", ("c", "d"))]),
    (".py", "from a.b import *\n", [("a.b", ())]),
    (".py", "from ..leaf import x\n", [("..leaf", ("x",))]),
    (".py", "from . import y\n", [(".", ("y",))]),
    (".py", "from app import leaf\n", [("app", ("leaf",))]),
    (".py", "    import type\n", [("type", ())]),
    (".java", "import a.b.C;\n", [("a.b.C", ())]),
    (".java", "import static a.b.C.d;\n", [("a.b.C.d", ())]),
    (".ts", 'import { x } from "app/leaf/sizes";\n', [("app/leaf/sizes", ())]),
    (".ts", 'import type { X } from "app/leaf/sizes";\n', [("app/leaf/sizes", ())]),
    (".ts", 'import X from "app/leaf/sizes";\n', [("app/leaf/sizes", ())]),
    (".ts", 'import {\n  a,\n  b,\n} from "../leaf/sizes.js";\n', [("../leaf/sizes.js", ())]),
    (".ts", 'export * from "./other.js";\n', [("./other.js", ())]),
    (".ts", 'import "../x.js";\n', [("../x.js", ())]),
    (".ts", 'const m = await import("openai");\n', [("openai", ())]),
    (".ts", "import x = require('../leaf/sizes');\n", [("../leaf/sizes", ())]),
    (".js", "const y = require('app/leaf');\n", [("app/leaf", ())]),
    (".cpp", '#include "app/leaf/sizes.h"\n', [("app/leaf/sizes.h", ())]),
]


class TheCheck(unittest.TestCase):
    def test_every_form_is_read(self) -> None:
        for suffix, source, wanted in FORMS:
            with self.subTest(suffix=suffix, source=source):
                self.assertEqual(modules.raw_targets(source, suffix), wanted)

    def test_targets_are_dotted(self) -> None:
        self.assertEqual(modules.targets('import { x } from "app/leaf/sizes";\n', ".ts"), [("app.leaf.sizes", ())])
        self.assertEqual(modules.targets('#include "app/leaf/sizes.h"\n', ".h"), [("app.leaf.sizes", ())])

    def test_a_file_is_read_only_by_its_own_family(self) -> None:
        self.assertEqual(modules.raw_targets('import X from "app/leaf/sizes";\n', ".py"), [("X", ())])
        self.assertEqual(modules.raw_targets("import a.b\n", ".ts"), [])
        self.assertEqual(modules.raw_targets("import a.b\n", ".java"), [])

    def test_a_relative_import_is_resolved_against_the_importing_folder(self) -> None:
        root = BROKEN / "modules"
        spec = modules.spec_of(root)
        at = root / "src" / "cli" / "relative.ts"
        self.assertEqual(modules.resolve("../leaf/sizes.js", at, root, spec), "app.leaf.sizes")
        self.assertEqual(modules.resolve("../leaf", at, root, spec), "app.leaf")
        self.assertEqual(modules.resolve("./other.js", at, root, spec), "app.cli.other")
        self.assertEqual(modules.resolve("..leaf.sizes", at, root, spec), "app.leaf.sizes")
        self.assertEqual(modules.resolve(".", at, root, spec), "app.cli")
        self.assertEqual(modules.resolve("..leaf", root / "src" / "cli" / "deep" / "x.py", root, spec), "app.cli.leaf")
        self.assertIsNone(modules.ours(modules.resolve("../../elsewhere/x.js", at, root, spec), "app.", spec))

    def test_an_outside_import_is_not_ours(self) -> None:
        spec = {"modules": {"leaf": {}}}
        self.assertIsNone(modules.ours("json", "app.", spec))
        self.assertEqual(modules.ours("app.leaf.sizes", "app.", spec), "leaf")

    def test_a_leaf_that_imports_is_caught(self) -> None:
        root = BROKEN / "modules"
        spec = modules.spec_of(root)
        spec["modules"]["leaf"]["mayImport"] = ["cli"]
        from test.support import scratch
        copy = scratch()
        (copy / "docs" / "modules.json").write_text(json.dumps(spec))
        self.assertEqual(modules.problems(copy), ["the leaf module 'leaf' may import ['cli']; it imports nothing of ours (MOD-01)"])


class TheOutsideRules(unittest.TestCase):
    def built(self, outside: list[str] | None, source: str, suffix: str = ".py", forbidden: list[str] | None = None) -> list[str]:
        """The problems of a one-file project whose only module has `outside` (None: no key) and imports `source`; forbidden defaults to ["anthropic"]."""
        from test.support import scratch
        root = scratch()
        entry = {"folder": "src/a", "purpose": "p", "mayImport": [], "entryPoints": []}
        if outside is not None:
            entry["outside"] = outside
        (root / "docs" / "modules.json").write_text(json.dumps({"package": "app.", "leaf": "a", "forbidden": forbidden or ["anthropic"], "modules": {"a": entry}}))
        (root / "src" / "a").mkdir(parents=True)
        (root / "src" / "a" / ("x" + suffix)).write_text(source)
        return modules.problems(root)

    def test_a_module_without_the_key_is_not_checked(self) -> None:
        self.assertEqual(self.built(None, "import requests\n"), [])

    def test_the_standard_library_and_a_package_inside_a_listed_one_pass(self) -> None:
        self.assertEqual(self.built([], "import json\nfrom os import path\n"), [])
        self.assertEqual(self.built(["numpy"], "import numpy.linalg\n"), [])
        self.assertEqual(self.built([], 'import { readFileSync } from "node:fs";\n', ".ts"), [])
        self.assertEqual(self.built([], "import java.util.List;\n", ".java"), [])

    def test_a_package_that_only_starts_with_a_listed_name_is_outside(self) -> None:
        self.assertEqual(len(self.built(["numpy"], "import numpyx\n")), 1)

    def test_a_forbidden_package_is_refused_unless_the_module_names_it(self) -> None:
        self.assertEqual(len(self.built(None, "import anthropic\n")), 1)
        self.assertEqual(len(self.built([], "import anthropic\n")), 1)
        self.assertEqual(self.built(["anthropic"], "import anthropic\n"), [])

    def test_our_package_itself_is_not_an_outside_package(self) -> None:
        self.assertEqual(self.built([], "from app import VERSION\n"), [])

    def test_every_real_forbidden_package_is_refused_imported_or_dynamic(self) -> None:
        """Each package docs/modules.json forbids, by a Python import and by a TypeScript dynamic import (1.27)."""
        for name in modules.spec_of(ROOT)["forbidden"]:
            with self.subTest(package=name):
                python = f"import {name}\n" if not name.startswith("@") else ""
                found = self.built(None, python, forbidden=[name]) + self.built(None, f'const m = await import("{name}");\n', ".ts", forbidden=[name])
                self.assertEqual(len(found), 2 if python else 1, found)
                self.assertTrue(all("(MOD-03)" in line for line in found), found)

    def test_a_name_imported_from_a_package_counts_as_inside_it(self) -> None:
        self.assertEqual(len(self.built(None, "from google import genai\n", forbidden=["google.genai"])), 1)
        self.assertEqual(self.built(["google.genai"], "from google import genai\n", forbidden=["google.genai"]), [])

    def test_the_current_model_sdks_are_forbidden(self) -> None:
        forbidden = modules.spec_of(ROOT)["forbidden"]
        for name in ("google.genai", "@google/genai", "mistralai", "@mistralai/mistralai", "ai", "langchain", "langchain_core",
                     "langchain_openai", "@langchain/core", "llamaindex", "llama_index", "cohere", "groq"):
            self.assertIn(name, forbidden)
