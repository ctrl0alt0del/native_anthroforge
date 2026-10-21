"""Import explicit open-loft correspondence through the normal edit/evaluation lifecycle."""

from dataclasses import replace
from typing import Any

from anthroforge.core.surfaces import SurfaceAlignment

from . import object_operations, surface_operations
from .construction_policy import require_topology_edit


def configure(session: Any, target: str, mapping: dict[str, list[Any]], across: list[int]) -> None:
    item = surface_operations.editable(session, target)
    require_topology_edit(session.document, target)
    if item.kind != "LOFT" or set(mapping) != {use.curve for use in item.curves}:
        raise ValueError("Material correspondence requires every source of an ordinary open loft.")
    if len(across) != len(item.curves) - 1:
        raise ValueError("Material correspondence requires one density per adjacent source pair.")
    alignment = tuple(aligned(session, use, mapping[use.curve]) for use in item.curves)
    item = replace(item, exact=True, alignment=alignment, across=tuple(across))
    object_operations.install(session, item)


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
    if (
        not selected
        or selected[0] != keys[0]
        or selected[-1] != keys[-1]
        or not set(selected).issubset(keys)
    ):
        raise ValueError(
            "Material correspondence must include the source endpoints and existing points."
        )
    if [keys.index(key) for key in selected] != sorted(keys.index(key) for key in selected):
        raise ValueError("Material correspondence points must follow source order.")
