"""Frozen surface measurements with explicit freshness, shared by UI and reports."""

from dataclasses import asdict
from typing import Any

from anthroforge.core.inspection_views import Measurement, SurfacePoint, decode_point
from anthroforge.native import measurement
from anthroforge.native.mesh import GeometryEngine, Mesh

from . import measurement_sources, presentation
from .inspection_context import InspectionContext
from .session import Session

Source = Session | InspectionContext


def witness(
    engine: GeometryEngine, mesh: Mesh, source: dict[str, Any], triangle: int, weights: Any
) -> SurfacePoint:
    position = measurement.point(engine, mesh.handle, source["frame"], triangle, weights)
    return SurfacePoint(**source, triangle=triangle, weights=tuple(weights), position=position)


def point(
    session: Session,
    entity: str,
    triangle: int,
    weights: list[float],
    role: str = "",
    stage: str = "",
) -> dict[str, Any]:
    source = measurement_sources.resolve(session, entity, role, stage)
    value = witness(session.engine, session.assets[source["asset"]].mesh, source, triangle, weights)
    return asdict(value)


def add(
    session: Session, start: dict[str, Any], end: dict[str, Any], name: str = "Distance"
) -> str:
    if session.waiting_save:
        raise ValueError("Wait until saving finishes before changing measurements.")
    value = Measurement(name.strip(), decode_point(start), decode_point(end))
    presentation.update_workspace(session, measurements=(*session.workspace.measurements, value))
    return value.id


def remove(session: Session, measurement: str) -> None:
    values = tuple(v for v in session.workspace.measurements if v.id != measurement)
    if len(values) == len(session.workspace.measurements):
        raise ValueError("Unknown measurement.")
    presentation.update_workspace(session, measurements=values)


def endpoint(session: Source, value: SurfacePoint) -> dict[str, Any]:
    from anthroforge.core.mirroring import parse, source

    item = session.document.registry.records.get(source(value.entity))
    try:
        current = measurement_sources.resolve(session, value.entity, value.role, value.stage)
        stale = current["asset"] != value.asset or current["frame"] != value.frame
    except ValueError:
        stale = True
    name = item.name + (" · mirrored" if parse(value.entity) else "") if item else "Deleted SCP"
    return dict(asdict(value), stale=stale, name=name)


def describe(session: Source, value: Measurement) -> dict[str, Any]:
    start, end = endpoint(session, value.start), endpoint(session, value.end)
    delta = measurement.distance(session.engine, value.start.position, value.end.position)
    return dict(
        id=value.id,
        name=value.name,
        start=start,
        end=end,
        delta=delta[:3],
        distance=delta[3],
        stale=start["stale"] or end["stale"],
    )


def inspect(session: Source) -> list[dict[str, Any]]:
    return [describe(session, value) for value in session.workspace.measurements]
