"""Sorts the names (C-001)."""


def first(names: list[str]) -> str:
    """The first name, because the caller compares against it."""
    return sorted(names)[0]  # as J-080 found
