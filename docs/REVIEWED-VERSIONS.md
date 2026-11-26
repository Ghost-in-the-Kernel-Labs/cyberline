# Reviewed versions: the record of every dependency update

One row per update read in by `docs/DEPENDENCY-REVIEW.md` (C-035). "From" is the last version the
project reviewed before this one, so the next review reads the whole range from "To". Verdict is the
reviewer's (SAFE, UNSAFE, UNSURE); Reputation is CLEAN or CONCERN; Decision is `automatic`, or
`Ghost: <the question, and the answer>`; a large bundled package says `large-bundle` in Notes.
`test/test_reviewed_versions.py` holds the shape, and `scripts/checks/dependency_review.py` fails the
fast loop on any pin with no row (a lockfile entry, a workflow's action, a Dockerfile's image digest, a
vendored manifest's row). On adoption every pin already held gets an `unreviewed baseline` row (Kind
`baseline`, From, Verdict and Reputation `—`): the pin is the first review's old side, taken as held
and not as read. The template has no dependencies; its baseline rows are the workflow's action and
the Java starter's image, which a stamped project carries with them.

| Date | Package | From | To | Kind | Verdict | Reputation | Decision | Journal | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-11-07 | actions/checkout | — | 11d5960a326750d5838078e36cf38b85af677262 | baseline | — | — | unreviewed baseline | J-071 | v4.4.0, pinned in the workflow before the record; the first review reads from this pin |
| 2026-11-07 | gradle:8.14.3-jdk21-noble | — | sha256:21bd311ed01360c189b8870c6b6e988199ff10f72d445d02fb39d3cff9da91d7 | baseline | — | — | unreviewed baseline | J-071 | the Java starter's image, pinned before the record; the first review reads from this pin |
