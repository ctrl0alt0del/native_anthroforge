"""Authored path editing independent of any primitive consumer or viewport."""

from dataclasses import replace
from typing import TYPE_CHECKING, Any

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_engines import decode
from anthroforge.core.curve_shapes import reshaped
from anthroforge.native import curve_queries

from .construction_codec import tuples
from .construction_policy import require_topology_edit
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
    item = selected(session, curve)
    if "kind" in settings:
        raise ValueError("Use curve.engine to change path engines.")
    config = configured_engine(item, settings)
    config = decode(item.engine, {k: v for k, v in vars_settings(config).items() if k != "kind"})
    if set(settings) & {"resolution", "samples"}:
        require_topology_edit(session.document, curve)
    install(session, replace(item, engine_settings=config))


def change_engine(
    session: "Session", curve: str, engine: str, settings: dict[str, Any] | None = None
) -> None:
    from .parametric_operations import switch

    item = selected(session, curve)
    if item.engine == engine and settings is None:
        return
    if settings is not None:
        return configured_switch(session, item, engine, settings)
    require_topology_edit(session.document, curve)
    if "PARAMETRIC" in (item.engine, engine):
        install(session, switch(session, item, engine))
        return
    settings = {"samples": max(64, len(item.points))} if engine == "ROUTED" else {}
    install(session, replace(item, engine_settings=decode(engine, settings)))


def configured_switch(
    session: "Session", item: Curve, engine: str, settings: dict[str, Any]
) -> None:
    from .parametric_policy import sampling_signature

    changed = replace(item, engine_settings=decode(engine, settings))
    if sampling_signature(item) != sampling_signature(changed):
        require_topology_edit(session.document, item.id)
    install(session, changed)


def configured_engine(item: Curve, settings: dict[str, Any]) -> Any:
    if item.engine == "ROUTED" and "obstacles" in settings:
        settings.setdefault("obstacle_mode", "MANUAL")
    return replace(item.engine_settings, **settings)


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
