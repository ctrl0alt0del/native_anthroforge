"""Accepted layout identity belongs to the result, including while authored edits are Manual."""

from dataclasses import replace
from typing import Any

from anthroforge.core.surfaces import Surface


def accepted(item: Surface, result: Any) -> Surface:
    if result.status != "ready":
        return replace(item, result=result)
    parts = ("main", *(branch.id for branch in item.branches))
    return replace(item, result=result, accepted_kind=item.kind, accepted_parts=parts)
