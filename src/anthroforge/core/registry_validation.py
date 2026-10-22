"""Reuse relationship validation for qualified local tissue strategy edits.

Only exact TissueVCP records opt in. Every changed strategy is still validated
against current sources; new fields and any changed external definitions invalidate.
"""

from collections.abc import Mapping
from typing import Any

from . import snapshot_definitions
from .tissue_policy import validate
from .tissues import TissueVCP

LOCAL_STRATEGIES = frozenset(
    ("parts", "both_sides", "reverse", "resolution", "relaxation", "crop", "fields")
)


def same_relationships(before: Any, after: Any) -> bool:
    if snapshot_definitions.same(before, after):
        return True
    if type(before) is not TissueVCP or type(after) is not TissueVCP:
        return False
    return all(
        getattr(before, name) == getattr(after, name)
        for name in snapshot_definitions.definition_fields(TissueVCP)
        if name not in LOCAL_STRATEGIES
    )


def reusable(records: Mapping[str, Any], previous: Mapping[str, Any]) -> bool:
    if records.keys() != previous.keys() or not all(
        same_relationships(previous[key], item) for key, item in records.items()
    ):
        return False
    for key, item in records.items():
        if type(item) is TissueVCP and not snapshot_definitions.same(previous[key], item):
            validate(item, records)
    return True
