"""Geometry writer ownership shared by anatomical primitives and construction surfaces."""

from dataclasses import replace
from typing import Any

from anthroforge.core.entities import SCP
from anthroforge.core.surfaces import Surface

from . import surface_results


def items(document: Any) -> tuple[SCP | Surface, ...]:
    return (
        *[e for e in document.entities if e.primitive],
        *[o for o in document.objects if isinstance(o, Surface)],
    )


def get(document: Any, target: str) -> SCP | Surface:
    item = document.object(target)
    if not isinstance(item, (SCP, Surface)):
        raise ValueError("Object does not produce mesh geometry.")
    return item


def install(session: Any, item: SCP | Surface, result: Any) -> None:
    if isinstance(item, SCP):
        session.replace_entities({item.id: anatomical_result(item, result)}, authored=False)
    else:
        objects = tuple(
            surface_results.accepted(item, result) if o.id == item.id else o
            for o in session.document.objects
        )
        session.replace_document(objects=objects)


def anatomical_result(item: SCP, result: Any) -> SCP:
    return replace(
        item,
        asset=result.asset,
        result=result,
        result_generation=item.result_generation + 1,
        status=result.status,
        error=result.error,
    )


def pending(session: Any, targets: set[str]) -> None:
    entities = {
        e.id: replace(e, result=replace(e.result, status="pending"))
        for e in session.document.entities
        if e.id in targets and e.primitive
    }
    objects = tuple(
        replace(o, result=replace(o.result, status="pending"))
        if o.id in targets and isinstance(o, Surface)
        else o
        for o in session.document.objects
    )
    session.replace_entities(entities, authored=False)
    if objects != session.document.objects:
        session.replace_document(objects=objects)


def failed(session: Any, target: str, error: str) -> None:
    item = session.document.registry.records.get(target)
    if isinstance(item, (SCP, Surface)):
        install(session, item, replace(item.result, status="failed", error=error))
