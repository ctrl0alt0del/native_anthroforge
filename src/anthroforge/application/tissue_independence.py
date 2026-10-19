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
    return str(changed.source)


def remapped(item: Any, mapping: dict[str, str]) -> Any:
    return replace(
        item,
        source=mapping[item.source],
        parts=tuple(replace(p, id=mapping.get(p.id, p.id)) for p in item.parts),
        base_state=replace(
            item.base_state, parts=tuple(mapping.get(k, k) for k in item.base_state.parts)
        ),
    )
