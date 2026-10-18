"""Authored path editing independent of any primitive consumer or viewport."""

from dataclasses import replace
from typing import TYPE_CHECKING, Any

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.native import curve_queries

from .construction_codec import tuples
from .object_operations import editable, install

if TYPE_CHECKING:
    from .session import Session


def selected(session: "Session", curve: str) -> Curve:
    item = editable(session, curve)
    if not isinstance(item, Curve):
        raise ValueError("Select a curve or fiber.")
    return item


def insert(session: "Session", curve: str, index: int, point: dict[str, Any]) -> str:
    item = selected(session, curve)
    if not 0 <= index <= len(item.points):
        raise ValueError("Point insertion index is outside the curve.")
    added = CurvePoint(**tuples(point))
    install(session, replace(item, points=(*item.points[:index], added, *item.points[index:])))
    return added.id


def remove(session: "Session", curve: str, point: str) -> None:
    item = selected(session, curve)
    if point not in {p.id for p in item.points}:
        raise ValueError("Unknown authored curve point.")
    install(session, replace(item, points=tuple(p for p in item.points if p.id != point)))


def subdivide(session: "Session", curve: str, segment: int, parameter: float) -> str:
    item = selected(session, curve)
    if item.engine == "ROUTED":
        raise ValueError("Insert an authored routing point; sampled paths are not editable knots.")
    changed = curve_queries.split(session.engine, item, segment, parameter)
    install(session, changed)
    return changed.points[segment + 1].id
