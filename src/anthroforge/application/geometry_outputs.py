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
    if not targets:
        return
    changes = {}
    for field in ("entities", "objects"):
        before = getattr(session.document, field)
        after = tuple(pending_record(item, targets) for item in before)
        if after != before:
            changes[field] = after
    if changes:
        session.replace_document(**changes)


def pending_record(item: Any, targets: set[str]) -> Any:
    eligible = isinstance(item, Surface) or isinstance(item, SCP) and item.primitive is not None
    if eligible and item.id in targets and item.result.status != "pending":
        return replace(item, result=replace(item.result, status="pending"))
    return item


def failed(session: Any, target: str, error: str) -> None:
    item = session.document.registry.records.get(target)
    if isinstance(item, (SCP, Surface)):
        install(session, item, replace(item.result, status="failed", error=error))
