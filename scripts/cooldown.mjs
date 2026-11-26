// The cooldown (C-034; Suite Builder G-254): no package version enters the lockfile until it has been public for
// 7 days. Each version package-lock.json holds that origin/main's did not is looked up on the registry; one
// published less than 7 days ago fails with --strict, named, with the day it may come in. No list of exceptions.
//   node scripts/cooldown.mjs --strict
import { execFileSync } from 'node:child_process';
import { existsSync, readFileSync, realpathSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

export const COOLDOWN_DAYS = 7;
const DAY = 24 * 60 * 60 * 1000;

/** The registry versions a lockfile holds, as name@version; links and non-registry entries are not dated. */
export function lockedVersions(lockText) {
  const packages = JSON.parse(lockText).packages ?? {};
  const out = new Set();
  for (const [path, entry] of Object.entries(packages)) {
    if (!path || entry.link || !entry.version || !String(entry.resolved ?? '').startsWith('https://registry.npmjs.org/')) continue;
    out.add(`${entry.name ?? path.slice(path.lastIndexOf('node_modules/') + 'node_modules/'.length)}@${entry.version}`);
  }
  return out;
}

/** The versions this lockfile brings that the one on origin/main did not; all of them when git cannot say. */
export function newVersions(lockText, baseLockText) {
  const base = baseLockText ? lockedVersions(baseLockText) : new Set();
  return [...lockedVersions(lockText)].filter((v) => !base.has(v));
}

/** Whether a publish time is younger than the cooldown, and the day it may come in. */
export function verdict(publishedAt, now = Date.now()) {
  const age = now - Date.parse(publishedAt);
  const allowedOn = new Date(Date.parse(publishedAt) + COOLDOWN_DAYS * DAY).toISOString().slice(0, 10);
  return { young: age < COOLDOWN_DAYS * DAY, allowedOn };
}

async function publishTime(nameAtVersion) {
  const at = nameAtVersion.lastIndexOf('@');
  const name = nameAtVersion.slice(0, at), version = nameAtVersion.slice(at + 1);
  const response = await fetch(`https://registry.npmjs.org/${name}`);
  if (!response.ok) return null;
  return (await response.json()).time?.[version] ?? null;
}

/** Whether this file is the one node was asked to run: its real path against argv[1]'s, so a path with a space, a `%`
 * or a symlink still runs, and an import (or `node -e`) does not (the form scripts/mutate.mjs uses). */
export function isDirectRun(moduleUrl, argv1) {
  if (!argv1 || !existsSync(argv1)) return false;
  return realpathSync(fileURLToPath(moduleUrl)) === realpathSync(argv1);
}

if (isDirectRun(import.meta.url, process.argv[1])) {
  const strict = process.argv.includes('--strict');
  if (!existsSync('package-lock.json')) {
    console.log('cooldown: no package-lock.json yet');
    process.exit(strict ? 1 : 0);
  }
  let base = null;
  try { base = execFileSync('git', ['show', 'origin/main:package-lock.json'], { encoding: 'utf8' }); } catch { base = null; }
  const young = [], unverified = [];
  for (const v of newVersions(readFileSync('package-lock.json', 'utf8'), base)) {
    const at = await publishTime(v);
    if (at === null) { unverified.push(v); continue; }
    const { young: isYoung, allowedOn } = verdict(at);
    if (isYoung) young.push(`${v} (published ${at.slice(0, 10)}, allowed on ${allowedOn})`);
  }
  for (const line of young) console.log(`cooldown: ${line}`);
  for (const v of unverified) console.log(`cooldown: ${v} NOT VERIFIED (no answer from the registry)`);
  process.exit(young.length || (strict && unverified.length) ? 1 : 0);
}
