"""Imported reference evidence is owned by live consumers, with history retaining old copies."""

from dataclasses import replace
from typing import Any

from anthroforge.core import graph_records

GROUPS = ("entities", "objects", "controls", "driving_shortcuts", "shortcuts")


def retained(document: Any, changes: dict[str, Any]) -> dict[str, Any]:
    if not document.external_references or not set(GROUPS) & changes.keys():
        return changes
    if "external_references" in changes:
        return changes
    before = {v.id: v for g in GROUPS for v in getattr(document, g)}
    after = {v.id: v for g in GROUPS for v in changes.get(g, getattr(document, g))}
    owners = {u.owner for r in document.external_references for u in r.uses}
    changed = {key for key in owners if before.get(key) is not after.get(key)}
    references = {k: graph_records.references(after[k]) for k in changed if k in after}
    rows = tuple(pruned(row, changed, references) for row in document.external_references)
    return dict(changes, external_references=tuple(r for r in rows if r.uses))


def pruned(row: Any, changed: set[str], references: Any) -> Any:
    uses = tuple(
        use
        for use in row.uses
        if use.owner not in changed
        or any(
            r.target == (row.target or row.id) and r.relationship == use.relationship
            for r in references.get(use.owner, ())
        )
    )
    return row if uses == row.uses else replace(row, uses=uses)
