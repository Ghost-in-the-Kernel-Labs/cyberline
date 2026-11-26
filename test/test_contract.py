"""The contract's invariants are in sequence and the leaf module names them both ways; planted breaks are caught (C-012)."""
import unittest
from pathlib import Path

from scripts.checks import contract, modules
from test.support import BROKEN, ROOT, scratch


def leaf_folder(root: Path) -> Path:
    """The leaf's folder as docs/modules.json names it: modules[leaf].folder under root, e.g. root/src/policy."""
    spec = modules.spec_of(root)
    return root / spec["modules"][spec["leaf"]]["folder"]


class TheRepository(unittest.TestCase):
    def test_the_template_contract_is_numbered(self) -> None:
        self.assertEqual(contract.numbering_problems((ROOT / "docs" / "CONTRACT.md").read_text()), [])

    def test_the_template_names_no_invariant_the_contract_lacks(self) -> None:
        document = (ROOT / "docs" / "CONTRACT.md").read_text()
        self.assertEqual(contract.reference_problems(document, leaf_folder(ROOT), held=False, root=ROOT), [])

    def test_the_planted_breaks_are_caught(self) -> None:
        root = BROKEN / "contract"
        document = (root / "docs" / "CONTRACT.md").read_text()
        self.assertEqual(contract.numbering_problems(document), ["invariant 2 is XX-03, expected XX-02"])
        self.assertEqual(contract.reference_problems(document, leaf_folder(root), held=True),
                         ["leaf/ names XX-09, which the contract does not have", "XX-03 is in the contract and nowhere in leaf/"])


class TheCheck(unittest.TestCase):
    def test_the_prefix_is_read_from_the_document(self) -> None:
        self.assertEqual(contract.prefix_of("## HAR-01 x\n"), "HAR")
        self.assertEqual(contract.numbering_problems("## HAR-01 x\n## HAR-02 y\n"), [])

    def test_a_duplicate_is_caught(self) -> None:
        self.assertEqual(contract.numbering_problems("## HAR-01 x\n## HAR-01 y\n"), ["HAR-01 appears 2 times", "invariant 2 is HAR-01, expected HAR-02"])

    def test_unheld_invariants_are_allowed_until_held(self) -> None:
        root = BROKEN / "contract"
        document = "## XX-01 a\n## XX-02 b\n"
        self.assertEqual(contract.reference_problems(document, leaf_folder(root), held=False), ["leaf/ names XX-09, which the contract does not have"])


class TheLeafNamedInModulesJson(unittest.TestCase):
    def test_the_leaf_is_resolved_from_the_json_not_assumed(self) -> None:
        root = BROKEN / "contract_policy"
        self.assertEqual(leaf_folder(root), root / "src" / "policy")
        self.assertEqual([p.name for p in (root / "src").iterdir()], ["policy"])

    def test_a_leaf_named_policy_is_held_both_ways(self) -> None:
        root = BROKEN / "contract_policy"
        document = (root / "docs" / "CONTRACT.md").read_text()
        self.assertEqual(contract.reference_problems(document, leaf_folder(root), held=True),
                         ["policy/ names XX-09, which the contract does not have", "XX-02 is in the contract and nowhere in policy/"])

    def test_a_leaf_named_policy_that_agrees_with_its_contract_has_no_problem(self) -> None:
        root = scratch()
        (root / "docs" / "modules.json").write_text((BROKEN / "contract_policy" / "docs" / "modules.json").read_text())
        (root / "src" / "policy").mkdir(parents=True)
        (root / "src" / "policy" / "x.py").write_text("# Invariant: XX-01\n# Invariant: XX-02\n")
        document = (BROKEN / "contract_policy" / "docs" / "CONTRACT.md").read_text()
        self.assertEqual(contract.reference_problems(document, leaf_folder(root), held=True), [])
