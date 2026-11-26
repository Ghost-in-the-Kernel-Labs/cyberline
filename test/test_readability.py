"""The core's own Python holds the Python stack's readability rules: the checks are the code the maintainer audits by
test rather than by eye (stacks/python/README.md, Neon Rain R-015)."""
import importlib.util
import unittest

from test.support import ROOT

CANDIDATES = (ROOT / "scripts" / "checks" / "readability.py", ROOT / "stacks" / "python" / "starter" / "scripts" / "checks" / "readability.py")
SOURCE = next((p for p in CANDIDATES if p.is_file()), None)


def load() -> object:
    """The readability module from wherever it lives: the template's starter, or a Python project's scripts/checks/."""
    spec = importlib.util.spec_from_file_location("stack_readability", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


readability = load() if SOURCE else None


@unittest.skipIf(readability is None, "not a Python-stack project: the readability rules are the stack's")
class TheCore(unittest.TestCase):
    def test_the_core_python_is_readable(self) -> None:
        readability.OUR_CODE = ("scripts", "test")
        self.assertEqual(readability.problems(ROOT), [])

    def test_a_planted_long_function_is_caught(self) -> None:
        source = "def f() -> int:\n    \"\"\"d\"\"\"\n" + "    x = 1\n" * 40 + "    return x\n"
        self.assertEqual(readability.source_problems(source, "x.py"), ["x.py:1 f is 43 lines, at most 39"])

    def test_a_missing_docstring_is_caught(self) -> None:
        self.assertEqual(readability.source_problems("def f() -> int:\n    return 1\n", "x.py"), ["x.py:1 f has no docstring (one with a concrete example)"])

    def test_star_args_are_caught(self) -> None:
        self.assertEqual(readability.source_problems("def f(*a: int) -> None:\n    \"\"\"d\"\"\"\n", "x.py"), ["x.py:1 f takes *args or **kwargs"])
