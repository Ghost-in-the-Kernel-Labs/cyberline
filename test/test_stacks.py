"""Each stack under stacks/ has its README, its gate ending in one verdict line, and a starter; and the core gate runs
a stack only when it is present (item 0.13)."""
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

try:
    from scripts import stamp
except ImportError:  # a stamped project does not carry the stamp
    stamp = None
from test.support import ROOT

STACKS = ROOT / "stacks"


def present() -> list[str]:
    """The stacks marked PRESENT: [] in the template, one name in a stamped project."""
    return sorted(p.name for p in STACKS.iterdir() if (p / "PRESENT").is_file())


class TheStacks(unittest.TestCase):
    def names(self) -> list[str]:
        """The stacks present, sorted: ["java", "python"]."""
        return sorted(p.name for p in STACKS.iterdir() if p.is_dir())

    def starter_required(self) -> bool:
        """The template keeps every stack's starter; a stamped project has copied its one stack's to the root."""
        return not present()

    def test_each_stack_has_its_three_parts(self) -> None:
        for name in self.names():
            with self.subTest(stack=name):
                self.assertTrue((STACKS / name / "README.md").is_file())
                self.assertTrue((STACKS / name / "gate.sh").is_file())
                if self.starter_required():
                    self.assertTrue((STACKS / name / "starter").is_dir())

    def test_each_gate_ends_with_its_verdict_and_names_its_fast_loop(self) -> None:
        for name in self.names():
            with self.subTest(stack=name):
                text = (STACKS / name / "gate.sh").read_text()
                self.assertEqual(text.count(f'echo "{name} gate: passed"'), 1)
                self.assertTrue(text.startswith("#!/usr/bin/env bash"))

    def test_each_readme_states_the_five_rules(self) -> None:
        for name in self.names():
            with self.subTest(stack=name):
                text = (STACKS / name / "README.md").read_text()
                for rule in ("Fast loop", "Dependencies", "Cooldown", "Mutation", "Readability"):
                    self.assertIn(f"| {rule} |", text)

    def test_the_template_has_four_stacks_and_a_stamped_project_one(self) -> None:
        if present():
            self.assertEqual(self.names(), present())
        else:
            self.assertEqual(self.names(), ["cpp", "java", "python", "typescript"])

    def test_the_core_gate_runs_a_stack_only_when_present(self) -> None:
        text = (ROOT / "scripts" / "gate.sh").read_text()
        self.assertIn('[ -f "$dir/PRESENT" ] || continue', text)
        self.assertIn('else step "the $name stack\'s gate" "the $name stack\'s gate" bash "$stack"; fi', text)
        self.assertIn('step "the $name stack\'s fast checks" "the $name stack\'s fast checks" bash "$stack" --fast', text)


def typescript_file(relative: str) -> Path:
    """A TypeScript starter file: in the template under stacks/typescript/starter/, in a stamped project at the root."""
    template = STACKS / "typescript" / "starter" / relative
    return template if template.exists() else ROOT / relative


@unittest.skipUnless((STACKS / "typescript").is_dir(), "no TypeScript stack in this tree")
class TheTypeScriptStarter(unittest.TestCase):
    def test_no_file_names_the_nonexistent_command_runner_package(self) -> None:
        for name in ("package.json", "knip.json"):
            with self.subTest(file=name):
                self.assertNotIn("@stryker-mutator/command-runner", typescript_file(name).read_text())

    def test_mutation_covers_src_only(self) -> None:
        text = typescript_file("stryker.config.mjs").read_text()
        self.assertIn("mutate: ['src/**/*.ts', '!src/**/*.gen.ts'],", text)
        self.assertNotIn("scripts/*.mjs'", text)

    def test_the_mutation_runner_is_not_the_stub(self) -> None:
        text = typescript_file("scripts/mutate.mjs").read_text()
        self.assertNotIn("not wired yet", text)
        self.assertNotIn("process.exit(1);\n", text.split("if (isDirectRun(", 1)[0])
        for part in ("reports', 'mutation', 'cache'", "MUTATE_CACHE", "--no-cache", "DYNAMIC", "no mutant was killed", "(stale)"):
            with self.subTest(part=part):
                self.assertIn(part, text)

    def test_the_cache_folder_is_ignored_and_the_mutation_document_is_there(self) -> None:
        starter = STACKS / "typescript" / "starter" / "gitignore.append"
        ignore = starter if starter.exists() else ROOT / ".gitignore"
        self.assertIn("/reports/", ignore.read_text().splitlines())
        self.assertIn("## Survivors", typescript_file("docs/MUTATION.md").read_text())

    def test_vitest_is_started_by_node_not_npx(self) -> None:
        text = typescript_file("stryker.config.mjs").read_text()
        self.assertIn("node node_modules/vitest/vitest.mjs run", text)
        self.assertNotIn("npx vitest", text)

    def test_the_readme_states_the_stack_facts(self) -> None:
        text = (STACKS / "typescript" / "README.md").read_text()
        for fact in ("`Bundler` when it is bundled for a browser", "has no Docker daemon", "unit tests import no `node:` module"):
            with self.subTest(fact=fact):
                self.assertIn(fact, text)

    def test_the_npm_major_is_pinned_and_enforced(self) -> None:
        self.assertEqual(json.loads(typescript_file("package.json").read_text())["engines"]["npm"], ">=11")
        self.assertIn("engine-strict=true", typescript_file(".npmrc").read_text().splitlines())

    def test_the_gate_refuses_an_npm_major_below_11_in_one_line(self) -> None:
        text = (STACKS / "typescript" / "gate.sh").read_text()
        self.assertRegex(text, r'npm --version \| cut -d\. -f1\)" -ge 11 \] \|\| \{ echo "typescript gate: npm [^\n]*below 11[^\n]*exit 1')

    def run_cooldown(self, flags: list[str]) -> subprocess.CompletedProcess:
        """cooldown.mjs run with node in an empty directory, so there is no package-lock.json."""
        empty = Path(tempfile.mkdtemp(prefix="ghost-core-cooldown-"))
        return subprocess.run(["node", str(typescript_file("scripts/cooldown.mjs")), *flags], cwd=empty, capture_output=True, text=True)

    @unittest.skipUnless(shutil.which("node"), "node is absent: the script's text is asserted instead")
    def test_cooldown_with_no_lockfile_says_so_and_fails_only_under_strict(self) -> None:
        strict = self.run_cooldown(["--strict"])
        self.assertEqual((strict.returncode, strict.stdout.strip()), (1, "cooldown: no package-lock.json yet"))
        relaxed = self.run_cooldown([])
        self.assertEqual((relaxed.returncode, relaxed.stdout.strip()), (0, "cooldown: no package-lock.json yet"))

    @unittest.skipUnless(shutil.which("node"), "node is absent: the script's text is asserted instead")
    def test_cooldown_runs_from_a_path_with_a_space_a_percent_and_a_symlink(self) -> None:
        """1.31: the direct-run check compares real paths, so a folder named `a b%20c` or a symlinked script still runs
        (the old `file://${argv[1]}` comparison did nothing there and exited 0 under --strict)."""
        folder = Path(tempfile.mkdtemp(prefix="ghost-core-cooldown-")) / "a b%20c"
        folder.mkdir()
        script = folder / "cooldown.mjs"
        script.write_text(typescript_file("scripts/cooldown.mjs").read_text())
        (folder / "link.mjs").symlink_to(script)
        empty = Path(tempfile.mkdtemp(prefix="ghost-core-cooldown-"))
        for path in (script, folder / "link.mjs"):
            with self.subTest(path=path.name):
                run = subprocess.run(["node", str(path), "--strict"], cwd=empty, capture_output=True, text=True)
                self.assertEqual((run.returncode, run.stdout.strip()), (1, "cooldown: no package-lock.json yet"))

    @unittest.skipIf(shutil.which("node"), "node is present: the script is run instead")
    def test_cooldown_text_guards_the_lockfile_read(self) -> None:
        text = typescript_file("scripts/cooldown.mjs").read_text()
        self.assertRegex(text, r"existsSync\('package-lock.json'\)[\s\S]*no package-lock.json yet[\s\S]*process.exit\(strict \? 1 : 0\)")
        self.assertIn("realpathSync(fileURLToPath(moduleUrl)) === realpathSync(argv1)", text)


OUTPUT_FOLDERS = {
    "python": ["build/", "mutants/", ".mutmut-cache", ".pytest_cache/", ".ruff_cache/"],
    "java": ["build/", ".gradle/"],
    "typescript": ["build/", "node_modules/", ".stryker-tmp/", "reports/", ".tmp/", "dist/"],
    "cpp": ["build/"],
}


GRAPH = ROOT / "test" / "fixtures" / "typescript-graph"
# 1.30: run inside `node`, the runner's own functions on the graph fixture; one JSON line of what they found.
PROBE = """
const m = await import(process.argv[1]);
const [graph, scratch] = [process.argv[2], process.argv[3]];
const { readFileSync, existsSync } = await import('node:fs');
const { join, relative } = await import('node:path');
const rel = (f) => relative(graph, f);
const src = join(graph, 'src');
const sources = [join(src, 'a.ts'), join(src, 'b.ts')];
const map = m.testsFor(sources, [join(graph, 'test', 'unit', 'b.test.ts')], src);
const text = (p) => (existsSync(p) ? readFileSync(p, 'utf8') : undefined);
const setup = m.configured(graph, text);
const read = (f) => text(join(graph, f));
const key = (r) => m.cacheKey(m.keyInputs('src/a.ts', ['test/unit/b.test.ts'], [], r, { node: 'x' }, setup));
const changed = (name) => (f) => (f === name ? 'changed' : read(f));
console.log(JSON.stringify({
  reached: Object.fromEntries(Object.entries(map).map(([s, t]) => [rel(s), t.map(rel)])),
  index: m.resolveImport(join(scratch, 'x.ts'), './lib/index.js', src) && rel(m.resolveImport(join(scratch, 'x.ts'), './lib/index.js', src)),
  dirIndex: m.resolveImport(join(scratch, 'x.ts'), './lib.js', src) !== null,
  missing: m.resolveImport(join(graph, 'src', 'a.ts'), './gone.js', src),
  setup,
  setupKeyed: key(changed('test/setup.ts')) !== key(read),
  baseKeyed: key(changed('tsconfig.strict.json')) !== key(read),
  sameKey: key(read) === key(read),
  directRun: m.isDirectRun(import.meta.url, process.argv[1]),
  cacheBy: [{}, { MUTATE_CACHE: '0' }, { GHOST_COLD: '1' }, { GHOST_COLD: '0' }].map((env) => m.options([], env).cache),
}));
"""


@unittest.skipUnless((STACKS / "typescript").is_dir() and shutil.which("node"), "no TypeScript stack, or no node")
class TheMutationRunnerRunsOnAGraph(unittest.TestCase):
    """1.30: the runner's graph and key functions, executed by node on test/fixtures/typescript-graph/."""

    def probe(self) -> dict:
        """What the runner's functions say of the fixture, run in node with the scratch folder for the index case."""
        scratch = Path(tempfile.mkdtemp(prefix="ghost-core-graph-"))
        (scratch / "lib").mkdir()
        (scratch / "lib" / "index.ts").write_text("export const x = 1;\n")
        runner = typescript_file("scripts/mutate.mjs").resolve().as_uri()
        result = subprocess.run(["node", "--input-type=module", "-e", PROBE, runner, str(GRAPH), str(scratch)],
                                capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout.strip().splitlines()[-1])

    def test_a_nodenext_graph_reaches_every_source(self) -> None:
        found = self.probe()
        self.assertEqual(found["reached"], {"src/a.ts": ["test/unit/b.test.ts"], "src/b.ts": ["test/unit/b.test.ts"]})
        self.assertIsNone(found["missing"])
        self.assertTrue(found["dirIndex"])
        self.assertTrue(found["index"].endswith("lib/index.ts"), found["index"])

    def test_the_key_names_setup_files_and_the_extends_chain(self) -> None:
        found = self.probe()
        self.assertEqual(found["setup"], ["test/setup.ts", "tsconfig.base.json", "tsconfig.strict.json"])
        self.assertTrue(found["setupKeyed"])
        self.assertTrue(found["baseKeyed"])
        self.assertTrue(found["sameKey"])

    def test_an_import_is_not_a_direct_run(self) -> None:
        self.assertFalse(self.probe()["directRun"])

    def test_the_cold_gate_bypasses_the_cache(self) -> None:
        """3.9: GHOST_COLD=1, which scripts/gate.sh exports, is MUTATE_CACHE=0; any other value leaves the cache on."""
        self.assertEqual(self.probe()["cacheBy"], [True, False, False, True])


@unittest.skipIf(present(), "a stamped project does not stamp")
class TheStampedIgnores(unittest.TestCase):
    def stamped(self, stack: str) -> Path:
        """The template stamped on one stack as far as its stack is chosen, git-initialised so check-ignore answers."""
        target = Path(tempfile.mkdtemp(prefix="ghost-core-ignores-")) / "project"
        target.mkdir()
        stamp.copy_template(target, stamp.tree_files())
        stamp.choose_stack(target, stack)
        subprocess.run(["git", "-C", str(target), "init", "-q"], check=True)
        return target

    def test_each_starter_carries_its_ignore_entries(self) -> None:
        for stack in OUTPUT_FOLDERS:
            with self.subTest(stack=stack):
                self.assertTrue((STACKS / stack / "starter" / stamp.IGNORE_APPEND).is_file())

    def test_every_stacks_build_and_mutation_output_is_ignored_in_a_stamped_tree(self) -> None:
        for stack, folders in OUTPUT_FOLDERS.items():
            target = self.stamped(stack)
            self.assertFalse((target / stamp.IGNORE_APPEND).exists())
            for folder in folders:
                with self.subTest(stack=stack, folder=folder):
                    probe = target / folder.rstrip("/") / "x" if folder.endswith("/") else target / folder
                    probe.parent.mkdir(parents=True, exist_ok=True)
                    probe.write_text("x")
                    result = subprocess.run(["git", "-C", str(target), "check-ignore", "-q", str(probe.relative_to(target))])
                    self.assertEqual(result.returncode, 0, f"{folder} is not ignored in a {stack} tree")

    def test_the_entries_are_appended_once(self) -> None:
        lines = (self.stamped("typescript") / ".gitignore").read_text().splitlines()
        self.assertEqual(lines.count("/build/"), 1)
        self.assertEqual(lines.count("/node_modules/"), 1)
