"""Plan one independent attached construction graph, shared by Membrane and Tissue creation."""

from dataclasses import dataclass, replace
from functools import partial
from typing import Any
from uuid import uuid4

from anthroforge.core import tissue_presets
from anthroforge.core.construction import Curve
from anthroforge.core.fibers import Fiber
from anthroforge.core.points import Point
from anthroforge.core.surfaces import Surface

from . import anchor_capture, authored_jobs, fiber_operations, object_operations, source_graph_copy
from .operations import require_name


@dataclass(frozen=True)
class Plan:
    source: str
    name: str
    selected: frozenset[str]
    identities: dict[str, str]
    fibers: tuple[fiber_operations.FiberCreation, ...] = ()
    anchor: anchor_capture.Capture | None = None
    tissue: tuple[str, str, str] | tuple[()] = ()

    @property
    def primary(self) -> str:
        return self.tissue[0] if self.tissue else self.identities[self.source]

    @property
    def outputs(self) -> frozenset[str]:
        return frozenset({self.identities[key] for key in self.selected} | {self.primary})


def membrane(session: Any, source: str, name: str = "Membrane") -> dict[str, str]:
    item = object_operations.editable(session, source)
    if not isinstance(item, Surface):
        raise ValueError("Select a Surface to create a Membrane.")
    return start(session, plan(session, source, require_name(name)))


def tissue(session: Any, source: str, name: str, preset: str) -> dict[str, str]:
    item = object_operations.editable(session, source)
    if preset not in {row["id"] for row in tissue_presets.available(item)}:
        raise ValueError("Choose a tissue preset compatible with the selected construction source.")
    spec = plan(session, source, item.name + " attached")
    spec = replace(spec, tissue=(str(uuid4()), require_name(name), preset))
    return start(session, spec)


def start(session: Any, spec: Plan) -> dict[str, str]:
    from .attached_creation_jobs import enqueue

    job = authored_jobs.begin(session, partial(enqueue, session, spec))
    return dict(object_id=spec.primary, job_id=job)


def plan(session: Any, source: str, name: str, identities: Any = None) -> Plan:
    selected = source_graph_copy.required(session.document, source)
    mapping = source_graph_copy.identities(session.document, selected)
    mapping.update({key: value for key, value in (identities or {}).items() if key in mapping})
    spec = Plan(source, name, frozenset(selected), mapping)
    fibers = tuple(curve_plan(session, spec, key) for key in sorted(selected))
    anchor = point_plan(session, spec)
    return replace(
        spec, fibers=tuple(value for value in fibers if value is not None), anchor=anchor
    )


def point_plan(session: Any, spec: Plan) -> anchor_capture.Capture | None:
    from .attachment_defaults import candidates

    if not isinstance(session.document.object(spec.source), Point):
        return None
    candidates(session.document)
    return anchor_capture.Capture(spec.source, spec.identities[spec.source], None, spec.name)


def curve_plan(session: Any, spec: Plan, key: str) -> fiber_operations.FiberCreation | None:
    item = session.document.object(key)
    if not isinstance(item, Curve):
        return None
    values = binding_values(session.document, item, spec)
    if isinstance(item, Fiber) and {row["point"] for row in values} == {
        b.point for b in item.bindings
    }:
        return None
    bindings = fiber_operations.requested_bindings(session, item, values)
    name = spec.name if key == spec.source else item.name + " fiber"
    return fiber_operations.FiberCreation(key, spec.identities, bindings, name, "")


def binding_values(document: Any, item: Curve, spec: Plan) -> list[dict[str, Any]]:
    rows = original_bindings(item)
    # Bound incident endpoints must share a binding owned by their copied junction source.
    pins = {row["point"] for row in rows}
    for junction in document.junctions:
        if (
            junction.id in spec.identities
            and junction.source.curve == item.id
            and bound_junction(document, junction.id, spec)
        ):
            if junction.source.point not in pins:
                rows.append(dict(point=junction.source.point))
    return rows


def bound_junction(document: Any, identity: str, spec: Plan) -> bool:
    curves = (document.object(key) for key in spec.selected)
    return any(bound_member(item, identity) for item in curves if isinstance(item, Curve))


def bound_member(item: Curve, identity: str) -> bool:
    pins = {row["point"] for row in original_bindings(item)}
    return any(point.junction == identity and point.id in pins for point in item.points)


def original_bindings(item: Curve) -> list[dict[str, Any]]:
    if not isinstance(item, Fiber):
        return fiber_operations.default_bindings(item)
    return [
        dict(point=b.point, target=b.target, role=b.role, capture_scope=b.capture_scope)
        for b in item.bindings
    ]
