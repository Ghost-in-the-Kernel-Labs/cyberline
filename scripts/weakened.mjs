// Lists test weakenings in the working tree against origin/main and never fails: a removed assertion, a `skip`
// or `only` added, an exact matcher loosened (toBe → toBeTruthy, toEqual → toMatchObject), a deleted test file.
// The commit message says why each was right (C-018: a test is never weakened to make code pass).
import { execFileSync } from 'node:child_process';

const diff = execFileSync('git', ['diff', 'origin/main', '--', 'test'], { encoding: 'utf8' });
const removed = diff.split('\n').filter((l) => l.startsWith('-') && !l.startsWith('---'));
const added = diff.split('\n').filter((l) => l.startsWith('+') && !l.startsWith('+++'));
const findings = [];
for (const l of removed) if (/\bexpect\(/.test(l)) findings.push(`assertion removed: ${l.slice(1).trim()}`);
for (const l of added) if (/\.(skip|only)\(/.test(l)) findings.push(`skip/only added: ${l.slice(1).trim()}`);
for (const l of added) if (/toBeTruthy|toMatchObject|toBeDefined/.test(l)) findings.push(`matcher loosened?: ${l.slice(1).trim()}`);
const deleted = execFileSync('git', ['diff', 'origin/main', '--diff-filter=D', '--name-only', '--', 'test'], { encoding: 'utf8' }).trim();
for (const f of deleted.split('\n').filter(Boolean)) findings.push(`test file deleted: ${f}`);
for (const f of findings) console.log(`weakened: ${f}`);
console.log(`weakened: ${findings.length} finding(s); the commit says why each was right`);
