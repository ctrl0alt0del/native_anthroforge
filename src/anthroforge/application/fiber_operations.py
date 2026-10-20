"""Independent curve-to-fiber authoring, using shared asynchronous transactions."""

from dataclasses import dataclass, replace
from functools import partial
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from anthroforge.core.construction import Curve
from anthroforge.core.fibers import Fiber
from anthroforge.core.surface_references import SurfaceReference

from . import authored_jobs, curve_copy, fiber_tasks, surface_providers
from .object_operations import editable
from .operations import require_name

if TYPE_CHECKING:
    from .session import Session


@dataclass(frozen=True)
class FiberCreation:
    source: str
    identities: dict[str, str]
    bindings: tuple[tuple[str, SurfaceReference | None, str], ...]
    name: str
    attachment_asset: str


def create(
    session: "Session",
    curve: str,
    bindings: list[dict[str, Any]] | None = None,
    name: str = "Fiber",
) -> str:
    item = editable(session, curve)
    if not isinstance(item, Curve):
        raise ValueError("Fiber creation requires a curve source.")
    values = default_bindings(item) if bindings is None else bindings
    anchors = requested_bindings(session, item, values)
    spec = FiberCreation(curve, curve_copy.mapping(item), anchors, require_name(name), str(uuid4()))
    return authored_jobs.begin(session, partial(fiber_tasks.enqueue, session, spec))


def requested_bindings(
    session: "Session", item: Curve, values: list[dict[str, Any]]
) -> tuple[Any, ...]:
    result = tuple(requested_binding(session, row) for row in values)
    keys = [row[0] for row in result]
    if len(keys) != len(set(keys)) or set(keys) - {p.id for p in item.points}:
        raise ValueError("Bindings require distinct authored curve points.")
    endpoints = {item.points[0].id, item.points[-1].id}
    if not result or (not item.closed and not endpoints.issubset(keys)):
        raise ValueError("Bind both open endpoints, or at least one chosen closed-curve point.")
    validate_targets(session, result)
    return result


def default_bindings(item: Curve) -> list[dict[str, Any]]:
    points = (item.points[0],) if item.closed else (item.points[0], item.points[-1])
    return [dict(point=point.id) for point in points]


def requested_binding(
    session: "Session", row: dict[str, Any]
) -> tuple[str, SurfaceReference | None, str]:
    return (
        str(row["point"]),
        requested_surface(session, row) if row.get("target") else None,
        str(row.get("capture_scope", "CURRENT_PARENT")),
    )


def validate_targets(session: "Session", result: tuple[Any, ...]) -> None:
    for _, target, scope in result:
        if target is not None:
            surface_providers.get(session.engine, session.document, session.assets, target)
        else:
            from .attachment_defaults import candidates

            candidates(session.document)
        if scope not in ("CURRENT_PARENT", "ANY_PARENT"):
            raise ValueError("Invalid endpoint capture scope.")


def requested_surface(session: "Session", row: dict[str, Any]) -> SurfaceReference:
    from anthroforge.core.anatomical_surfaces import reference

    return reference(
        str(row["target"]), session.document.registry.records, str(row.get("role", ""))
    )


def binding_scope(session: "Session", curve: str, point: str, scope: str) -> None:
    from .object_operations import install

    item = editable(session, curve)
    if not isinstance(item, Fiber) or point not in {b.point for b in item.bindings}:
        raise ValueError("Select a fiber anatomical binding.")
    bindings = tuple(
        replace(b, capture_scope=scope) if b.point == point else b for b in item.bindings
    )
    install(session, replace(item, bindings=bindings))
