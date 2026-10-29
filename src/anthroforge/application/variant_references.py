"""Copied construction retains independently repairable external declarations."""

from dataclasses import replace
from typing import Any
from uuid import uuid4

from anthroforge.core import graph_records


def allocate(document: Any, ids: dict[str, str]) -> tuple[Any, ...]:
    selected = tuple(r for r in document.external_references if any(u.owner in ids for u in r.uses))
    ids.update({row.id: str(uuid4()) for row in selected})
    return selected


def copy(rows: Any, ids: dict[str, str]) -> tuple[Any, ...]:
    return tuple(
        replace(
            row,
            id=ids[row.id],
            target=graph_records.key(row.target, ids),
            property=graph_records.rewritten(row.property, ids),
            instance=ids.get(row.instance, row.instance),
            uses=tuple(replace(use, owner=ids[use.owner]) for use in row.uses if use.owner in ids),
        )
        for row in rows
    )
