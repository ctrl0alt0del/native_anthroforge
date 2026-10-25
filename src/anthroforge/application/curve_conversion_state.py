"""Install source conversion and retained consumer correspondence in one transaction."""

from dataclasses import replace
from typing import Any

from anthroforge.core.surfaces import Surface

from . import object_operations, object_revisions


def install(session: Any, changed: Any) -> None:
    before = session.document.object(changed.id)
    retained = {p.id for p in changed.points}
    removed = {p.id for p in before.points} - retained
    objects = tuple(consumer(item, changed.id, removed) for item in session.document.objects)
    object_operations.install(session, changed, objects=objects)


def consumer(item: Any, curve: str, removed: set[str]) -> Any:
    if not removed or not isinstance(item, Surface) or not item.alignment:
        return item
    alignment = tuple(
        retained(value, removed) if use.curve == curve else value
        for use, value in zip(item.curves, item.alignment, strict=True)
    )
    return object_revisions.authored(item, replace(item, alignment=alignment))


def retained(value: Any, removed: set[str]) -> Any:
    if value.point in removed:
        raise ValueError("Retain the closed surface correspondence point or explicitly Realign.")
    stations = tuple(station for station in value.stations if station[0] not in removed)
    return replace(value, stations=stations)
