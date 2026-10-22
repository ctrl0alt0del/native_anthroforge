"""Author explicit open-loft correspondence through the normal evaluation lifecycle."""

from dataclasses import replace
from typing import Any

from anthroforge.core.surfaces import SurfaceAlignment

from . import object_operations, surface_operations
from .construction_policy import require_topology_edit


def configure(session: Any, target: str, mapping: dict[str, list[Any]], across: list[int]) -> None:
    item = surface_operations.editable(session, target)
    require_topology_edit(session.document, target)
    require_layout(item, mapping, across)
    alignment = tuple(aligned(session, use, mapping[use.curve]) for use in item.curves)
    item = replace(item, exact=True, alignment=alignment, across=tuple(across))
    object_operations.install(session, item)


def require_layout(item: Any, mapping: Any, across: Any) -> None:
    if item.kind not in ("LOFT", "BRANCHED") or set(mapping) != {u.curve for u in item.curves}:
        raise ValueError("Material correspondence requires every source of an open loft.")
    if item.kind == "BRANCHED":
        if across:
            raise ValueError("Branched correspondence uses connector sampling; leave across empty.")
    elif len(across) != len(item.curves) - 1:
        raise ValueError("Material correspondence requires one density per adjacent source pair.")


def aligned(session: Any, use: Any, values: list[Any]) -> SurfaceAlignment:
    curve = session.document.object(use.curve)
    if curve.closed or use.start not in (None, 0) or use.span not in (None, 1):
        raise ValueError("Material correspondence requires complete open source curves.")
    value = SurfaceAlignment(stations=tuple((str(key), float(station)) for key, station in values))
    require_points(curve, value)
    return value


def require_points(curve: Any, value: SurfaceAlignment) -> None:
    keys = [point.id for point in curve.points]
    selected = [key for key, _ in value.stations]
    endpoints = selected and selected[0] == keys[0] and selected[-1] == keys[-1]
    if not endpoints or not set(selected).issubset(keys):
        raise ValueError(
            "Material correspondence must include the source endpoints and existing points."
        )
    lookup = {key: index for index, key in enumerate(keys)}
    indices = [lookup[key] for key in selected]
    if indices != sorted(indices):
        raise ValueError("Material correspondence points must follow source order.")
