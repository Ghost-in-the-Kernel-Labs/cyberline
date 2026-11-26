# Escalations: each failure handed one grade up, by kind

One row per escalation (C-027, C-028, C-036; `docs/when/escalation.md`). The grade that received it
writes it after the replay. Kinds: `missing-row` (no routing row for the task), `not-read` (the row
existed and was not followed), `wrong-row` (the row pointed at the wrong files), `stale-pointer` (a
pointer to a moved or deleted file), `hard` (the fix was hard with the right route), `no-replay` (the
agent could not say what it did), `no-advisor` (a worker that could not escalate: no Agent tool and
no one above it reachable). A conflict between agents is never a row: it stops the work at once and
goes to Ghost (C-029, `docs/when/conflict.md`). Three open rows of one kind go to Ghost under
HANDOFF's "For Ghost" for a routing pass; `test/test_registers.py` holds that.

| Date | Task | Kind | Route taken | What the next grade found | Open |
| --- | --- | --- | --- | --- | --- |
