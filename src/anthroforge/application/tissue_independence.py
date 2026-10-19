"""Detach a tissue's construction graph without duplicating external support surfaces."""

from dataclasses import replace
from typing import Any

from . import object_operations, source_graph_copy
from .tissue_operations import tissue


def independent(session: Any, target: str) -> str:
    item = tissue(session, target)
    objects, mapping, junctions = source_graph_copy.clone(session, item.source)
    session.replace_document(
        objects=(*session.document.objects, *objects),
        junctions=(*session.document.junctions, *junctions),
    )
    changed = remapped(item, mapping)
    object_operations.install(session, changed)
    remap_regions(session, item.id, mapping)
    return str(changed.source)


def remapped(item: Any, mapping: dict[str, str]) -> Any:
    return replace(
        item,
        source=mapping[item.source],
        parts=tuple(replace(p, id=mapping.get(p.id, p.id)) for p in item.parts),
        base_state=replace(
            item.base_state, parts=tuple(mapping.get(k, k) for k in item.base_state.parts)
        ),
        **{name: remapped_material(getattr(item, name), mapping) for name in MATERIALS},
    )


MATERIALS = ("rest_material", "intrinsic_material", "final_material")


def remap_regions(session: Any, target: str, mapping: dict[str, str]) -> None:
    for item in session.document.objects:
        rows = getattr(item, "stack_relationships", ())
        changed = tuple(region_reference(row, item.id, target, mapping) for row in rows)
        if rows != changed:
            object_operations.install(session, replace(item, stack_relationships=changed))


def region_reference(row: Any, owner: str, target: str, mapping: dict[str, str]) -> Any:
    cover = owner if row.cover == "SELF" else row.other
    if cover != target:
        return row
    return replace(
        row, regions=tuple((mapping.get(part, part), face) for part, face in row.regions)
    )


def remapped_material(state: Any, mapping: dict[str, str]) -> Any:
    if state is None:
        return None
    return replace(
        state,
        parts=tuple(replace(p, id=mapping.get(p.id, p.id)) for p in state.parts),
        base_state=replace(
            state.base_state, parts=tuple(mapping.get(k, k) for k in state.base_state.parts)
        ),
    )
