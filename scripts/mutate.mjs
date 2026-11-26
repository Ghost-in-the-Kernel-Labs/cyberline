// One mutation run per source file, with only the tests that reach it (C-018; stacks/typescript/README.md).
//   node scripts/mutate.mjs                  every src/**/*.ts but *.gen.ts
//   node scripts/mutate.mjs src/leaf/caps.ts one file
// For each file, the test files under test/unit whose imports reach it (through the STAMP_ALIAS and relative imports) are
// MUTATE_TESTS, and Stryker runs with --mutate <file> (stryker.config.mjs: the command runner, G-290). A mutant no
// test kills (Survived, NoCoverage) is a survivor; each must have its line in docs/MUTATION.md, and a line there with
// no survivor behind it is stale. Red: a survivor not written up, a stale line, a source file no test reaches, and a
// run that kills nothing when there were mutants, because then the runner may have tested nothing. A file Stryker
// makes no mutant of (a types-only file: src/leaf/types.ts) is not that case; its report holds no entry for it.
// The cache: a file's report is kept under reports/mutation/cache/<key>.json, the key a SHA-256 over every
// byte that can change its verdict (keyInputs); a hit replays it and its line says `cached`. `--no-cache`,
// MUTATE_CACHE=0 or GHOST_COLD=1 (the cold gate, `GHOST_COLD=1 scripts/gate.sh`) runs every file and rewrites the
// cache (a tune-up pass, so the gate's time is the full run).
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, mkdirSync, readFileSync, readdirSync, realpathSync, renameSync, statSync, writeFileSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

// STAMP_ALIAS: the import alias for src/, from package.json's "imports" ("#<prefix>/*": "./src/*"); scripts/stamp.py
// fills it with "#<prefix in lower case>/", so a stamped project's tests import "#st/leaf/caps".
export const STAMP_ALIAS = '#p/';
// fileURLToPath, not URL.pathname: a path holding a space or a `%` stays the path it is.
const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const SRC = join(ROOT, 'src');
const TESTS = join(ROOT, 'test', 'unit');
const DOC = join(ROOT, 'docs', 'MUTATION.md');
const REPORT = join(ROOT, 'reports', 'mutation', 'mutation.json');
const CACHE = join(ROOT, 'reports', 'mutation', 'cache');
// A quote bounds the first form, so a multi-line `import {\n a,\n b\n} from '…'` is read and a string holding the word
// "from" is not.
const IMPORT = /(?:^|\n)\s*(?:import|export)[^'"]*?from\s+['"]([^'"]+)['"]|(?:^|\n)\s*import\s+['"]([^'"]+)['"]/g;
const SURVIVOR = /^- (\S+):(\d+) (\S+) /;
// A dynamic `import('…')`: a test's vi.hoisted block loads its fakes this way, and `specifiers` does not read it.
const DYNAMIC = /\bimport\s*\(\s*['"]([^'"]+)['"]\s*\)/g;
const CODE = /\.[cm]?[jt]sx?$/;
// A file that reads what no import names (the file system, a child process, the environment, a glob): its run can
// change with bytes the key cannot see, so a file whose tests load one is never cached.
const UNSEEN = /^(node:)?(fs|fs\/promises|child_process|worker_threads)$/;
const UNSEEN_TEXT = /\bprocess\.env\b|\bimport\.meta\.glob\b/;
// The files beside the source and its tests whose bytes can change a verdict, in the key's order: the two configs (Stryker's and vitest's); the transform's settings and the module type; every resolved package, not only the three named (a
// transitive one such as the transformer can change a verdict); the runner itself. What vitest loads by configuration
// rather than by import is keyed too (`configured`): its setup files and every tsconfig the `extends` chain names.
export const KEYED = ['stryker.config.mjs', 'vitest.config.ts', 'tsconfig.json', 'package.json', 'package-lock.json', 'scripts/mutate.mjs'];
export const TOOLS = ['vitest', '@stryker-mutator/core', 'vite'];

/** Every file under `dir` whose name ends with `suffix`, sorted; [] when the folder is missing. */
export function walk(dir, suffix) {
  if (!existsSync(dir)) return [];
  const out = [];
  for (const name of readdirSync(dir).sort()) {
    const path = join(dir, name);
    if (statSync(path).isDirectory()) out.push(...walk(path, suffix));
    else if (name.endsWith(suffix)) out.push(path);
  }
  return out;
}

/** The paths a specifier's base can be, in order: itself, `.ts` and `/index.ts` added, and for the `.js` a NodeNext
 * import must write ("./caps.js", "./caps.mjs", "./caps.cjs", "./caps.jsx") the TypeScript source it stands for
 * ("./caps.ts", "./caps.mts", "./caps.cts", "./caps.tsx") and that name's `/index.ts`. */
export function candidates(base) {
  const out = [base, `${base}.ts`, join(base, 'index.ts')];
  const js = /\.([cm]?)js(x?)$/.exec(base);
  if (js) {
    const stem = base.slice(0, -js[0].length);
    out.push(`${stem}.${js[1]}ts${js[2]}`, join(stem, 'index.ts'));
  }
  return out;
}

/** The file an import names, or null for a package: "<alias>leaf/caps" and "<alias>leaf/caps.js" are src/leaf/caps.ts;
 * "./x" and "./x.js" are beside `from`. */
export function resolveImport(from, spec, src = SRC) {
  let base;
  if (spec.startsWith(STAMP_ALIAS)) base = join(src, spec.slice(STAMP_ALIAS.length));
  else if (spec.startsWith('.')) base = resolve(dirname(from), spec);
  else return null;
  for (const candidate of candidates(base)) {
    if (existsSync(candidate) && statSync(candidate).isFile()) return candidate;
  }
  return null;
}

/** The import specifiers in a source text, in order: `import { a } from "x"` and `import "x"` both count. */
export function specifiers(text) {
  return [...text.matchAll(IMPORT)].map((m) => m[1] ?? m[2]);
}

/** Every file a test reaches through its imports, transitively (the test itself excluded). */
export function reaches(test, src = SRC) {
  const seen = new Set();
  const stack = [test];
  while (stack.length) {
    const file = stack.pop();
    for (const spec of specifiers(readFileSync(file, 'utf8'))) {
      const target = resolveImport(file, spec, src);
      if (target && !seen.has(target)) { seen.add(target); stack.push(target); }
    }
  }
  return seen;
}

/** For each source file, the test files that reach it: { [source]: [test, ...] }. */
export function testsFor(sources, tests, src = SRC) {
  const map = Object.fromEntries(sources.map((s) => [s, []]));
  for (const test of tests) for (const file of reaches(test, src)) if (file in map) map[file].push(test);
  return map;
}

/** The survivors in a Stryker JSON report for one file: [{ line, mutator, replacement }]. */
export function survivors(report, file) {
  const entry = Object.entries(report.files ?? {}).find(([path]) => path === file || path.endsWith(`/${file}`));
  if (!entry) return [];
  return entry[1].mutants
    .filter((m) => m.status === 'Survived' || m.status === 'NoCoverage')
    .map((m) => ({ line: m.location.start.line, mutator: m.mutatorName, replacement: m.replacement ?? '' }));
}

/** The killed count in a report for one file. */
export function killed(report, file) {
  const entry = Object.entries(report.files ?? {}).find(([path]) => path === file || path.endsWith(`/${file}`));
  return entry ? entry[1].mutants.filter((m) => m.status === 'Killed' || m.status === 'Timeout').length : 0;
}

/** How many mutants Stryker made in one file: 0 for a file the report does not hold, such as a types-only file. */
export function mutantCount(report, file) {
  const entry = Object.entries(report.files ?? {}).find(([path]) => path === file || path.endsWith(`/${file}`));
  return entry ? entry[1].mutants.length : 0;
}

/** The survivors docs/MUTATION.md writes up, as "file:line mutator" keys. */
export function writtenUp(doc) {
  const keys = new Set();
  for (const line of doc.split('\n')) {
    const m = SURVIVOR.exec(line);
    if (m) keys.add(`${m[1]}:${m[2]} ${m[3]}`);
  }
  return keys;
}

/** Every specifier a file loads by: the static ones `specifiers` reads, then each `import('…')`. */
export function loads(text) {
  return [...specifiers(text), ...[...text.matchAll(DYNAMIC)].map((m) => m[1])];
}

/** The file a load names, its `?raw` or other query dropped (a golden, a fixture, package.json); null for a package. */
export function resolveLoad(from, spec, src = SRC) {
  return resolveImport(from, spec.replace(/\?.*$/, ''), src);
}

/** Every file reachable from `roots` by `next` (a file's loads, resolved), the roots included, sorted. */
export function closure(roots, next) {
  const seen = new Set(roots);
  const stack = [...roots];
  while (stack.length) for (const target of next(stack.pop())) if (!seen.has(target)) { seen.add(target); stack.push(target); }
  return [...seen].sort();
}

/** Whether a file's text reads something no import names, so a key over bytes cannot see what its run depends on. */
export function readsUnseen(text) {
  return UNSEEN_TEXT.test(text) || loads(text).some((spec) => UNSEEN.test(spec));
}

/** The tool versions in the key: Node's whole version (a patch can change a builtin a test calls), and each of TOOLS as
 * package-lock.json resolves it ('missing' when it does not). */
export function toolVersions(lockText, node) {
  const packages = JSON.parse(lockText).packages ?? {};
  return { node, ...Object.fromEntries(TOOLS.map((t) => [t, packages[`node_modules/${t}`]?.version ?? 'missing'])) };
}

/** The setup files a vitest config names, read from its text (it is TypeScript, so it is not run to read it), in order
 * and each once: `setupFiles: ['./test/setup.ts']` or `setupFiles: './a.ts'` gives ["test/setup.ts"] or ["a.ts"]. */
export function setupFiles(configText) {
  const found = [];
  for (const m of configText.matchAll(/\bsetupFiles\s*:\s*(\[[^\]]*\]|'[^']*'|"[^"]*")/g)) {
    for (const q of m[1].matchAll(/['"]([^'"]+)['"]/g)) {
      const path = q[1].replace(/^\.\//, '');
      if (!found.includes(path)) found.push(path);
    }
  }
  return found;
}

/** Every tsconfig the `extends` chain from `start` names, `start` excluded, relative to `root` and in order; a relative
 * name is beside the file that names it, a package's under node_modules; a missing file ends its branch and is still
 * keyed (as missing). `readText(path)` gives a file's text or undefined. */
export function extendsChain(root, start, readText) {
  const chain = [];
  const stack = [start];
  while (stack.length) {
    const file = stack.shift();
    const text = readText(join(root, file));
    const m = text === undefined ? null : /"extends"\s*:\s*("[^"]*"|\[[^\]]*\])/.exec(text);
    for (const q of m ? m[1].matchAll(/"([^"]+)"/g) : []) {
      const named = q[1].startsWith('.') ? join(dirname(file), q[1]) : join('node_modules', q[1]);
      const next = relative(root, resolve(root, named.endsWith('.json') ? named : `${named}.json`));
      if (next !== start && !chain.includes(next)) { chain.push(next); stack.push(next); }
    }
  }
  return chain;
}

/** The files vitest and the transform load by configuration, not by import: the setup files vitest.config.ts names and
 * the tsconfig.json `extends` chain, relative to `root`. */
export function configured(root, readText) {
  const vitest = readText(join(root, 'vitest.config.ts'));
  return [...(vitest === undefined ? [] : setupFiles(vitest)), ...extendsChain(root, 'tsconfig.json', readText)];
}

/** The key's inputs, in a fixed order : the source; its tests, in MUTATE_TESTS's order; every other file they
 * load, sorted (the sources they import, helpers, goldens and fixtures: a change in any can change a verdict); KEYED;
 * the configured files (setup files, extended tsconfigs); the tool versions. Each is [role and path, bytes],
 * `read(path)` giving undefined for a missing file. */
export function keyInputs(file, tests, loaded, read, versions, setup = []) {
  const named = new Set([file, ...tests]);
  return [
    [`source ${file}`, read(file)],
    ...tests.map((t) => [`test ${t}`, read(t)]),
    ...[...loaded].filter((f) => !named.has(f)).sort().map((f) => [`loads ${f}`, read(f)]),
    ...KEYED.map((f) => [`config ${f}`, read(f)]),
    ...setup.map((f) => [`configured ${f}`, read(f)]),
    ['tools', JSON.stringify(versions)],
  ];
}

/** A SHA-256 over the inputs, each framed by its name and length, so no two different input lists share a key. */
export function cacheKey(inputs) {
  const hash = createHash('sha256');
  for (const [name, bytes] of inputs) {
    const body = bytes === undefined ? undefined : typeof bytes === 'string' ? new TextEncoder().encode(bytes) : bytes;
    hash.update(`${name}\0${body === undefined ? 'missing' : body.length}\0`);
    if (body !== undefined) hash.update(body);
  }
  return hash.digest('hex');
}

/** A stored report for `file` under `key`, or null: a missing, unreadable or mismatched record is a miss, never read. */
export function lookup(store, key, file) {
  const text = store.get(key);
  if (text === undefined) return null;
  try {
    const record = JSON.parse(text);
    if (record.key === key && record.file === file && record.report && typeof record.report === 'object') return record.report;
  } catch { /* a torn or foreign record is a miss */ }
  return null;
}

/** Store a fresh run's report under its key, with the key and file inside so a misplaced record is never read. */
export function remember(store, key, file, report) {
  store.set(key, JSON.stringify({ key, file, report }));
}

/** The command line: the files named, and whether the cache may be read (`--no-cache`, MUTATE_CACHE=0 or the cold
 * gate's GHOST_COLD=1 say no). */
export function options(argv, env) {
  const cold = env.MUTATE_CACHE === '0' || env.GHOST_COLD === '1';
  return { files: argv.filter((a) => a !== '--no-cache'), cache: !argv.includes('--no-cache') && !cold };
}

// The store on disk: one file per key, written beside its name and renamed, so a run cut short leaves no torn record.
const disk = {
  get: (key) => (existsSync(join(CACHE, `${key}.json`)) ? readFileSync(join(CACHE, `${key}.json`), 'utf8') : undefined),
  set: (key, text) => {
    mkdirSync(CACHE, { recursive: true });
    const part = join(CACHE, `${key}.${process.pid}.part`);
    writeFileSync(part, text);
    renameSync(part, join(CACHE, `${key}.json`));
  },
};

function run(file, tests) {
  const env = { ...process.env, MUTATE_TESTS: tests.map((t) => relative(ROOT, t)).join(' ') };
  execFileSync('npx', ['stryker', 'run', '--mutate', file], { cwd: ROOT, env, stdio: 'inherit' });
  return JSON.parse(readFileSync(REPORT, 'utf8'));
}

/** Whether this file is the one node was asked to run: its real path against argv[1]'s, so a path with a space, a `%`
 * or a symlink still runs, and an import (or `node -e`) does not. */
export function isDirectRun(moduleUrl, argv1) {
  if (!argv1 || !existsSync(argv1)) return false;
  return realpathSync(fileURLToPath(moduleUrl)) === realpathSync(argv1);
}

if (isDirectRun(import.meta.url, process.argv[1])) {
  const { files, cache } = options(process.argv.slice(2), process.env);
  const chosen = files.map((p) => resolve(ROOT, p));
  const sources = (chosen.length ? chosen : walk(SRC, '.ts')).filter((f) => !f.endsWith('.gen.ts'));
  const tests = walk(TESTS, '.test.ts').filter((f) => !f.endsWith('.int.test.ts'));
  const map = testsFor(sources, tests);
  const written = writtenUp(existsSync(DOC) ? readFileSync(DOC, 'utf8') : '');
  const read = (rel) => (existsSync(join(ROOT, rel)) ? readFileSync(join(ROOT, rel)) : undefined);
  const next = (path) => (CODE.test(path) ? loads(readFileSync(path, 'utf8')).map((s) => resolveLoad(path, s)).filter(Boolean) : []);
  const text = (path) => (existsSync(path) ? readFileSync(path, 'utf8') : undefined);
  const setup = configured(ROOT, text);
  const setupCode = setup.filter((f) => CODE.test(f) && existsSync(join(ROOT, f))).map((f) => join(ROOT, f));
  const versions = toolVersions(readFileSync(join(ROOT, 'package-lock.json'), 'utf8'), process.versions.node);
  const used = new Set();
  const problems = [];
  for (const source of sources) {
    const file = relative(ROOT, source);
    if (!map[source].length) { problems.push(`${file}: no test reaches it; a gate that runs nothing is not a gate`); continue; }
    const rels = map[source].map((t) => relative(ROOT, t));
    // A setup file runs before every test, so what it loads is in the closure as what a test loads is.
    const loaded = closure([...map[source], ...setupCode], next).map((f) => relative(ROOT, f));
    const unseen = loaded.find((f) => CODE.test(f) && readsUnseen(readFileSync(join(ROOT, f), 'utf8')));
    const keyNow = () => cacheKey(keyInputs(file, rels, loaded, read, versions, setup));
    const key = keyNow();
    let report = cache && !unseen ? lookup(disk, key, file) : null;
    const hit = report !== null;
    // A file changed while Stryker ran gives a report of neither version: it is used for this run and never stored.
    if (!hit) { report = run(file, map[source]); if (!unseen && keyNow() === key) remember(disk, key, file, report); }
    const found = survivors(report, file);
    const dead = killed(report, file);
    if (!dead && mutantCount(report, file)) problems.push(`${file}: no mutant was killed; the runner may have tested nothing (G-290)`);
    for (const s of found) {
      const key = `${file}:${s.line} ${s.mutator}`;
      if (written.has(key)) used.add(key);
      else problems.push(`${key} survived (${JSON.stringify(s.replacement)}) and docs/MUTATION.md has no line for it`);
    }
    const how = hit ? ', cached' : unseen ? `, uncacheable (${unseen} reads what no import names)` : '';
    console.log(`mutate: ${file}: ${dead} killed, ${found.length} survived${how}, tests: ${rels.join(' ')}`);
  }
  if (!chosen.length) for (const key of written) if (!used.has(key)) problems.push(`docs/MUTATION.md writes up ${key}, which no longer survives (stale)`);
  for (const p of problems) console.log(`mutate: ${p}`);
  console.log(`mutate: ${sources.length} file(s), ${problems.length} problem(s)`);
  process.exit(problems.length ? 1 : 0);
}
