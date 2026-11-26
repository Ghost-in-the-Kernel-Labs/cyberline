"""TODO.md is a chain in order, its first open item has a check, every phase ends with a tune-up pass (a reopened
phase, one whose tune-up pass DONE.md already holds, with at most three new items may end with a tune-up commit
instead), DONE.md shares none of its items, and no item's heading appears twice in DONE.md (test/test_todo.py; C-016,
C-024, docs/when/tune-up.md "A reopened phase").

The waiting phase (ASB-010, NR's `moved`): an item that waits on something outside the repository carries a `Waits on:`
line and sits in the last phase, headed "## Phase W: waiting on Ghost", with a `Moved: from Phase N` line naming the
phase its number belongs to; every item there carries both lines, the phase is last, and it needs no tune-up pass. The
chain's rules (order under numbered phases, the first item's check, the passes) read the file without it.

The waiting kinds (4.7): `Waits on:` names Ghost (his choice, approval or ruling), counsel, another project, or the items a
waiting tune-up pass waits on, in words; and two kinds with a shape, for what a session lacks: `Waits on: environment (<host
or tool>)`, a host the session's network allow-list blocks or a machine or tool it does not have (docs/SUPPLY-CHAIN.md,
"The hosts a session needs"), and `Waits on: reference (<what>)`, licensed reference material that lives on a private mount,
never in the repository (C-033). A line that opens with either word and lacks the parenthesised what is refused.

Carried from Neon Rain's scripts/checks/todo.py with the tune-up rule added.
"""
import re
from collections import Counter

ITEM = re.compile(r"^### (\d+)\.(\d+) (.*)$", re.MULTILINE)
PHASE = re.compile(r"^## Phase (\d+)", re.MULTILINE)
WAITING = re.compile(r"^## Phase W: waiting on Ghost[ \t]*$", re.MULTILINE)
NEXT_PHASE = re.compile(r"^## ", re.MULTILINE)
# The two kinds with a shape (4.7): opened by the word, in any case; held to "<kind> (<what>)" with nothing after.
SHAPED_KIND = re.compile(r"^Waits on: (environment|reference)\b", re.MULTILINE | re.IGNORECASE)
SHAPED = re.compile(r"^Waits on: (environment|reference) \([^()\n]*[^()\s][^()\n]*\)[ \t]*$")
PASS = "Tune-up pass"
CLOSERS = (PASS, "Tune-up commit")
# Ghost, 2026-11-07, provisional (docs/HANDOFF.md "Settled by Ghost"): moved only by a decision from the Cost record.
REOPENED_LIMIT = 3


def items(text: str) -> list[tuple[int, int]]:
    """The items' numbers in file order: "### 0.5 x" gives (0, 5)."""
    return [(int(phase), int(step)) for phase, step, _ in ITEM.findall(text)]


def order_problems(todo: str) -> list[str]:
    """Phases ascending, items ascending, and each item under its own phase's heading."""
    found: list[str] = []
    phases = [int(p) for p in PHASE.findall(todo)]
    if phases != sorted(phases):
        found.append(f"phases out of order: {phases}")
    numbers = items(todo)
    if numbers != sorted(numbers):
        found.append(f"items out of order: {[f'{a}.{b}' for a, b in numbers]}")
    for match in ITEM.finditer(todo):
        heading = PHASE.findall(todo[: match.start()])
        if not heading or int(heading[-1]) != int(match.group(1)):
            found.append(f"item {match.group(1)}.{match.group(2)} is not under Phase {match.group(1)}")
    return found


def first_item_problems(todo: str) -> list[str]:
    """The first open item's body (up to the next heading) has a `Check:` line."""
    match = ITEM.search(todo)
    if match is None:
        return []
    rest = todo[match.end():]
    following = re.search(r"^#{2,3} ", rest, flags=re.MULTILINE)
    body = rest[: following.start()] if following else rest
    if re.search(r"^Check:", body, flags=re.MULTILINE):
        return []
    return [f"the first open item, {match.group(1)}.{match.group(2)}, has no Check: line"]


def by_phase(text: str) -> dict[int, list[tuple[int, str]]]:
    """Each phase's items in file order: "### 1.2 x" gives {1: [(2, "x")]}."""
    found: dict[int, list[tuple[int, str]]] = {}
    for phase, step, title in ITEM.findall(text):
        found.setdefault(int(phase), []).append((int(step), title))
    return found


def reopened_since(done: list[tuple[int, str]]) -> int | None:
    """For one phase's items in DONE.md: None when none is its tune-up pass (the phase was never closed); else how many
    items DONE.md holds of it after its last tune-up pass or commit, the reopening's items already done."""
    if not any(title.startswith(PASS) for _, title in done):
        return None
    last = max(step for step, title in done if title.startswith(CLOSERS))
    return sum(1 for step, title in done if step > last)


# Decision: C-024 (a reopened phase of at most three new items closes by a tune-up commit; Ghost, 2026-11-07)
def reopened_problems(phase: int, open_items: list[tuple[int, str]], since: int) -> list[str]:
    """A reopened phase ends with a tune-up commit or pass, and with more than REOPENED_LIMIT new items (done since the
    reopening, and open before its closing item) only with a pass."""
    title = open_items[-1][1]
    if not title.startswith(CLOSERS):
        return [f"Phase {phase} is reopened (DONE.md holds its tune-up pass); end it with a \"Tune-up commit\" or "
                f"\"Tune-up pass\" item: its last item is {title!r}"]
    new = since + len(open_items) - 1
    if new > REOPENED_LIMIT and not title.startswith(PASS):
        return [f"Phase {phase} is reopened with {new} new items, more than {REOPENED_LIMIT}; close it by a "
                f"\"Tune-up pass\", not {title!r}"]
    return []


# Decision: C-024 (a tune-up that is not a numbered item does not happen)
def tune_up_problems(todo: str, done: str = "") -> list[str]:
    """Each phase's last item is a tune-up pass: its title starts "Tune-up pass"; a phase DONE.md shows reopened is held
    by reopened_problems instead."""
    found: list[str] = []
    closed = by_phase(done)
    for phase, open_items in by_phase(todo).items():
        since = reopened_since(closed.get(phase, []))
        if since is not None:
            found += reopened_problems(phase, open_items, since)
        elif not open_items[-1][1].startswith(PASS):
            found.append(f"Phase {phase}'s last item is {open_items[-1][1]!r}, not a tune-up pass")
    return found


def twice_problems(done: str) -> list[str]:
    """Each item number DONE.md heads more than once, by the same parse as TODO.md's (items): a doubled file or a moved
    item pasted twice. "### 0.9 x" twice gives ["0.9 appears 2 times in DONE.md"]."""
    return [f"{a}.{b} appears {n} times in DONE.md" for (a, b), n in sorted(Counter(items(done)).items()) if n > 1]


def split_waiting(todo: str) -> tuple[str, str]:
    """TODO.md as (the chain, the waiting phase): the waiting phase runs from its heading to the next "## " heading or
    the end; ("…", "") when there is none. "## Phase 1: a\n…## Phase W: waiting on Ghost\n### 1.3 x\n" gives the text
    before the W heading, then the W heading and 1.3."""
    heading = WAITING.search(todo)
    if heading is None:
        return todo, ""
    following = NEXT_PHASE.search(todo, heading.end())
    end = following.start() if following else len(todo)
    return todo[: heading.start()] + todo[end:], todo[heading.start(): end]


def bodies(text: str) -> list[tuple[int, int, str]]:
    """Each item's number and body, up to the next heading: "### 2.5 x\n\nWaits on: y\n" gives [(2, 5, "\n\nWaits on: y\n")]."""
    found: list[tuple[int, int, str]] = []
    for match in ITEM.finditer(text):
        following = re.compile(r"^#{2,3} ", re.MULTILINE).search(text, match.end())
        found.append((int(match.group(1)), int(match.group(2)), text[match.end(): following.start() if following else len(text)]))
    return found


def kind_problems(phase: int, step: int, body: str) -> list[str]:
    """Each `Waits on:` line of an item that opens with environment or reference without its shape: "Waits on: environment"
    gives ["item 4.2 waits on environment without its shape: `Waits on: environment (<what>)`"]; "Waits on: environment
    (api.osv.dev)" and "Waits on: Ghost's ruling" give []."""
    found: list[str] = []
    for match in SHAPED_KIND.finditer(body):
        if not SHAPED.match(body[match.start():].split("\n", 1)[0]):
            kind = match.group(1).lower()
            found.append(f"item {phase}.{step} waits on {kind} without its shape: `Waits on: {kind} (<what>)`")
    return found


# Decision: C-016 (an item that waits on something outside the repository is moved to the waiting phase; ASB-010)
def waiting_problems(todo: str) -> list[str]:
    """A `Waits on:` item outside the waiting phase; a waiting item without `Waits on:`, or without a `Moved: from Phase N`
    naming its own number's phase; a numbered phase after the waiting phase; waiting items out of numeric order."""
    chain, waiting = split_waiting(todo)
    found = [f"item {a}.{b} has a Waits on: line; move it to \"## Phase W: waiting on Ghost\" with a Moved: line"
             for a, b, body in bodies(chain) if re.search(r"^Waits on:", body, re.MULTILINE)]
    for phase, step, body in bodies(waiting):
        if not re.search(r"^Waits on: \S", body, re.MULTILINE):
            found.append(f"item {phase}.{step} is in the waiting phase without a Waits on: line")
        found += kind_problems(phase, step, body)
        moved = re.search(r"^Moved: from Phase (\d+)\b", body, re.MULTILINE)
        if moved is None or int(moved.group(1)) != phase:
            found.append(f"item {phase}.{step} is in the waiting phase without \"Moved: from Phase {phase}\"")
    if waiting and PHASE.search(todo, todo.index(waiting) + len(waiting)):
        found.append("the waiting phase is not the last phase: a numbered phase follows it")
    if items(waiting) != sorted(items(waiting)):
        found.append(f"waiting items out of order: {[f'{a}.{b}' for a, b in items(waiting)]}")
    return found


def problems(todo: str, done: str) -> list[str]:
    """Everything wrong with TODO.md given DONE.md; [] when the chain holds. The chain's rules read it without the
    waiting phase (split_waiting), which is exempt from the pass rule."""
    chain, _ = split_waiting(todo)
    both = sorted(set(items(todo)) & set(items(done)))
    shared = [f"{a}.{b} is in both TODO.md and DONE.md" for a, b in both]
    return (order_problems(chain) + first_item_problems(chain) + tune_up_problems(chain, done) + waiting_problems(todo)
            + shared + twice_problems(done))
