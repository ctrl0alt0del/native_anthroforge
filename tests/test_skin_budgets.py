"""Nested subtree reservations follow the addon metadata policy without double counting."""

from dataclasses import replace

from anthroforge.core.document import Document
from anthroforge.core.entities import SCP
from anthroforge.core.skin import Skin, SkinContributor, TopologySettings
from anthroforge.core.skin_budgets import errors


def fixture():
    bones = (
        SCP("Root", id="r"),
        SCP("Mid", id="m", parent="r"),
        SCP("Leaf", id="l", parent="m"),
        SCP("Sibling", id="s", parent="r"),
    )
    rules = tuple(
        SkinContributor(k, density_mode="SUBTREE_BUDGET", target_quads=n)
        for k, n in (("r", 6000), ("l", 2000), ("s", 3000))
    )
    return Document(entities=bones, skin=Skin(contributors=rules))


def test_nested_budget_counts_nearest_explicit_ancestor_only():
    document = fixture()
    assert not errors(document)
    rules = tuple(
        replace(s, target_quads=4500) if s.owner == "l" else s for s in document.skin.contributors
    )
    changed = replace(document, skin=replace(document.skin, contributors=rules))
    assert errors(changed) == ("Root: child budgets 7500 exceed 6000 target quads.",)


def test_top_level_budget_does_not_count_descendants_twice():
    document = fixture()
    skin = replace(document.skin, topology_settings=TopologySettings(target_quads=5000))
    assert errors(replace(document, skin=skin)) == (
        "Document: child budgets 6000 exceed 5000 target quads.",
    )
