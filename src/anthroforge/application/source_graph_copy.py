"""Copy owned construction once; retain ordinary external parents and anatomical targets."""

from dataclasses import replace
from typing import Any
from uuid import uuid4

from anthroforge.core.construction import Curve
from anthroforge.core.points import Anchor
from anthroforge.core.surfaces import Surface

from . import curve_copy, curve_independence, junction_copies, surface_independence
from .construction_copy import remap_result
from .curve_copy_resources import Copies


def required(document: Any, root: str) -> set[str]:
    found, pending = set(), {root}
    while pending:
        found |= pending
        children = {
            use.curve
            for key in pending
            if isinstance(item := document.object(key), Surface)
            for use in item.curves
        }
        curves = {key for key in found | children if isinstance(document.object(key), Curve)}
        pending = (children | surface_independence.required_sources(document, curves)) - found
    return found


def identities(document: Any, selected: set[str]) -> dict[str, str]:
    mapping = {key: str(uuid4()) for key in selected}
    for key in selected:
        item = document.object(key)
        if isinstance(item, Curve):
            mapping.update(curve_copy.mapping(item))
        if isinstance(item, Surface):
            keys = {b.id for b in item.branches} | set(item.accepted_parts) - {"main"}
            mapping.update({value: str(uuid4()) for value in keys})
    return junction_copies.identities(document, mapping)


def record(item: Any, copier: Copies) -> Any:
    if isinstance(item, Curve):
        return copier.record(item)
    mapping = copier.identities
    changed = (
        curve_independence.remapped_surface(item, mapping) if isinstance(item, Surface) else item
    )
    if not isinstance(item, (Anchor, Surface)):
        raise ValueError("This construction graph has no independent-copy contract.")
    return remapped_record(changed, mapping)


def remapped_record(item: Any, mapping: dict[str, str]) -> Any:
    return replace(
        item,
        id=mapping[item.id],
        name=item.name + " copy",
        parent=mapping.get(item.parent, item.parent),
        owners=tuple(mapping.get(key, key) for key in item.owners),
        result=remap_result(item.result, mapping),
    )


def clone(session: Any, source: str) -> tuple[Any, dict[str, str], Any]:
    selected = required(session.document, source)
    mapping = identities(session.document, selected)
    copier = Copies(session.resources, mapping)
    objects = tuple(
        record(item, copier) for item in session.document.objects if item.id in selected
    )
    junctions = junction_copies.records(session.document, mapping)
    return objects, mapping, junctions
