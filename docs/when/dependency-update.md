# A dependency update, or a new dependency (C-035)

Read this when a task needs a package added, updated or removed, when a lockfile or a vendored
manifest would change, or when the cooldown or `npm outdated` names a newer version.

**A routine update** is a patch or a minor version of a package the project already holds, with
every layer of `docs/DEPENDENCY-REVIEW.md` green: past the cooldown (or a security fix the review
calls SAFE), no advisory against it, publisher and provenance unchanged, no install script or
Python startup file added or changed, the scan's hits explained, the patch reviewer SAFE over the
whole range since the last reviewed version, the reputation checker CLEAN. It comes in without
asking Ghost, with its row in `docs/REVIEWED-VERSIONS.md`. **Everything else goes to Ghost**, with one
paragraph (what the package is, what changed, what is uncertain, what you recommend): a new package,
a major version, a changed publisher or provenance, an install script added or changed, any
UNSAFE, UNSURE or CONCERN, a listing that flagged a link or a special file, or a layer that could not
run.

1. **A new dependency is Ghost's**: a one-line reason drafted for `theGhost.md`, a review of the
   whole package (not a diff) as `docs/DEPENDENCY-REVIEW.md` step 3 describes, why the project needs
   it; then stop and wait. Never add it to main first.
2. **An update** follows `docs/DEPENDENCY-REVIEW.md`, every layer, in order: the cooldown, the
   lockfile-only resolve listing every package the change brings in, the audit, publisher and
   provenance, the archives fetched into a new empty folder outside the project and unpacked and
   scanned by `scripts/review_scan.py --unpack` (the stack README has the fetch command), the patch
   reviewer (`.claude/agents/patch-reviewer.md`, one brief per package range from its last reviewed
   version), the reputation checker (`.claude/agents/reputation-checker.md`, given the package, the
   registry and the versions, never a repository path).
3. **Routine**: take it, its row in `docs/REVIEWED-VERSIONS.md` (the fast loop fails a lockfile entry
   with no row), one journal entry of class `decision` naming the layers' results, commit through
   `scripts/commit.sh`. Do not ask Ghost.
4. **Anything else**: the paragraph for Ghost under `docs/HANDOFF.md`'s "For Ghost", the lockfile
   put back, and stop. UNSAFE is reported to the registry if the evidence holds.
5. **Never** install anything UNSAFE, run anything inside an unpacked package, give either agent
   more than its tools, write a baseline row for an update, or edit a hash, a lock, a pin table or an
   allow-list to pass a check.

Why: Suite Builder, 2026-11-01. The old rule, "human approval for every dependency change", had the
maintainer approving what an agent put in front of him across several projects, and an approval
given to everything protects nothing; a worm's patch release passed every layer the old rule had
because none of them read what changed (`docs/DEPENDENCY-REVIEW.md`, "The threat").
