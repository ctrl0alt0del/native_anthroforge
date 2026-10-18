"""Authored path editing independent of any primitive consumer or viewport."""

from dataclasses import replace
from typing import TYPE_CHECKING, Any

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_shapes import reshaped
from anthroforge.native import curve_queries

from .construction_codec import tuples
from .curve_edit_state import current
from .object_operations import editable, install

if TYPE_CHECKING:
    from .session import Session


def selected(session: "Session", curve: str) -> Curve:
    item = current(session, editable(session, curve))
    if not isinstance(item, Curve):
        raise ValueError("Select a curve or fiber.")
    return item


def configure(session: "Session", curve: str, **settings: Any) -> None:
    from anthroforge.core.curve_engines import decode

    from .construction_policy import require_topology_edit
    from .curve_sources import consumers

    item = selected(session, curve)
    if "kind" in settings:
        raise ValueError("Use a previewed conversion to change path engines.")
    config = replace(item.engine_settings, **settings)
    config = decode(item.engine, {k: v for k, v in vars_settings(config).items() if k != "kind"})
    if set(settings) & {"resolution", "samples"}:
        for consumer in consumers(session.document, {curve}):
            require_topology_edit(session.document, consumer)
    install(session, replace(item, engine_settings=config))


def vars_settings(settings: Any) -> dict[str, Any]:
    from dataclasses import asdict

    return asdict(settings)


def insert(session: "Session", curve: str, index: int, point: dict[str, Any]) -> str:
    item = selected(session, curve)
    if not 0 <= index <= len(item.points):
        raise ValueError("Point insertion index is outside the curve.")
    added = CurvePoint(**tuples(point))
    install(session, reshaped(item, points=(*item.points[:index], added, *item.points[index:])))
    return added.id


def remove(session: "Session", curve: str, point: str) -> None:
    item = selected(session, curve)
    if point not in {p.id for p in item.points}:
        raise ValueError("Unknown authored curve point.")
    install(session, reshaped(item, points=tuple(p for p in item.points if p.id != point)))


def subdivide(session: "Session", curve: str, segment: int, parameter: float) -> str:
    item = selected(session, curve)
    if item.engine == "ROUTED":
        raise ValueError("Insert an authored routing point; sampled paths are not editable knots.")
    changed = curve_queries.split(session.engine, item, segment, parameter)
    install(session, changed)
    return changed.points[segment + 1].id
