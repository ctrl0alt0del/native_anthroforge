"""Frozen surface measurements with explicit freshness, shared by UI and reports."""

from dataclasses import asdict
from typing import Any

from anthroforge.core.inspection_views import Measurement, SurfacePoint, decode_point
from anthroforge.core.results import geometry_asset
from anthroforge.native import measurement, scene
from anthroforge.native.mesh import GeometryEngine, Mesh

from . import presentation
from .inspection_context import InspectionContext
from .session import Session

Source = Session | InspectionContext


def witness(
    engine: GeometryEngine, mesh: Mesh, source: dict[str, Any], triangle: int, weights: Any
) -> SurfacePoint:
    position = measurement.point(engine, mesh.handle, source["frame"], triangle, weights)
    return SurfacePoint(**source, triangle=triangle, weights=tuple(weights), position=position)


def point(session: Session, entity: str, triangle: int, weights: list[float]) -> dict[str, Any]:
    item = session.document.entity(entity)
    asset = geometry_asset(item)
    if not asset:
        raise ValueError("This SCP has no accepted surface.")
    source = dict(
        entity=entity,
        asset=asset,
        frame=scene.entity_frame(session.engine, item),
        revision=item.result.revision,
    )
    value = witness(session.engine, session.assets[asset].mesh, source, triangle, weights)
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
    item = session.document.index.entities.get(value.entity)
    stale = item is None or geometry_asset(item) != value.asset
    if item is not None:
        stale |= scene.entity_frame(session.engine, item) != value.frame
    return dict(asdict(value), stale=stale, name=item.name if item else "Deleted SCP")


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
