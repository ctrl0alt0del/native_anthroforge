"""Fiber capture owns input snapshots and publishes within the initiating undo operation."""

from dataclasses import fields, replace
from functools import partial
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from anthroforge.core.construction import Curve
from anthroforge.core.entities import Attachment
from anthroforge.core.fibers import Fiber, FiberBinding
from anthroforge.core.jobs import Job
from anthroforge.core.results import EvaluationResult, Port
from anthroforge.core.scheduling import Workload
from anthroforge.native import attachment_fields, construction
from anthroforge.native.mesh import NativeCancellation

from . import (
    attachment_assets,
    authored_jobs,
    curve_copy,
    curve_sources,
    dependencies,
    surface_providers,
)
from .attachment_candidates import eligible
from .construction_policy import revisions
from .consumed_paths import accepted
from .evaluation_results import matches
from .path_assets import PathAsset

if TYPE_CHECKING:
    from .fiber_operations import FiberCreation
    from .session import Session


def capture_targets(document: Any, spec: "FiberCreation") -> tuple[Any, ...]:
    return tuple(
        sorted(
            set(eligible(document, spec.identities[spec.source])) | {b[1] for b in spec.bindings}
        )
    )


def inputs(document: Any, spec: "FiberCreation") -> set[Port]:
    source = dependencies.ports(document, Port(spec.source, "path")) | {Port(spec.source, "pose")}
    return source | surface_providers.ports(document, capture_targets(document, spec))


def enqueue(session: "Session", spec: "FiberCreation", origin: int) -> str:
    job = make_job(session, spec, origin)
    job.cancel = NativeCancellation(session.engine)
    job.restart_on_input_change = True
    job.retry = partial(enqueue, session, spec, origin)
    job.observes = job.prerequisites = frozenset(inputs(session.document, spec))
    job.reads = frozenset(port.owner for port in job.observes)
    job.provides = frozenset((Port(spec.identities[spec.source], "path"),))
    job.workload = partial(workload, spec)
    return session.scheduler.submit(job)


def make_job(session: "Session", spec: "FiberCreation", origin: int) -> Job:
    return Job(
        "Bind " + spec.name,
        frozenset((spec.identities[spec.source],)),
        lambda document: (document, session.resources.snapshot()),
        partial(compute, session, spec),
        partial(publish, session, spec, origin),
        key="fiber:" + spec.identities[spec.source],
        kind="fiber_capture",
    )


def workload(spec: "FiberCreation", document: Any) -> Workload:
    curve = curve_sources.source(document, spec.source)
    return Workload(
        affected=1,
        entities=len(document.entities),
        candidates=len(curve.points) * max(1, curve.resolution),
    )


def path_workload(session: "Session", item: Fiber, document: Any) -> Workload:
    asset = session.resources.attachments.get(item.attachment_asset)
    rows = len(asset.field.owners) if asset else len(item.points) * item.resolution
    targets = item.edit.candidates if item.edit else ()
    triangles = sum(
        surface_providers.triangle_count(document, session.assets, key) for key in targets
    )
    return Workload(affected=1, candidates=rows, entities=len(targets), triangles=triangles)


def capture(session: "Session", spec: "FiberCreation", document: Any, resources: Any) -> Any:
    item = curve_sources.source(document, spec.source)
    original = accepted(document, resources.paths, spec.source)
    targets = capture_targets(document, spec)
    indices = {point.id: index for index, point in enumerate(item.points)}
    pins = [indices[row[0]] for row in spec.bindings]
    parents = [targets.index(row[1]) for row in spec.bindings]
    world = curve_sources.world(session.engine, document, item.id)
    records = construction.resolved_curve(session.engine, original.authored)
    request = attachment_fields.Capture(original.path, records, world, pins, parents)
    return item, original, targets, request


def compute(session: "Session", spec: "FiberCreation", payload: Any, cancel: Any) -> Any:
    document, resources = payload
    item, original, targets, request = capture(session, spec, document, resources)
    surfaces = attachment_assets.surface_inputs(session.engine, document, resources.meshes, targets)
    field = attachment_fields.capture(session.engine, surfaces, request, cancel.handle)
    captures = attachment_assets.captures(session.engine, document, resources.meshes, targets)
    asset = attachment_assets.compact(field, captures)
    copied = independent_curve(item, original.authored, spec)
    fiber = build_fiber(copied, replace(spec, attachment_asset=str(uuid4())), asset)
    return document, fiber, PathAsset(original.path, fiber), asset


def independent_curve(item: Curve, accepted: Curve, spec: "FiberCreation") -> Curve:
    current = replace(item, points=accepted.points)
    copied = curve_copy.clone(current, spec.identities)
    return Curve(**{field.name: getattr(copied, field.name) for field in fields(Curve)})


def build_fiber(curve: Curve, spec: "FiberCreation", asset: Any) -> Fiber:
    indices = {point.id: index for index, point in enumerate(curve.points)}
    bindings = tuple(
        captured_binding(spec.identities[point], target, scope, indices, asset)
        for point, target, scope in spec.bindings
    )
    state = {field.name: getattr(curve, field.name) for field in fields(Curve)}
    state.update(
        name=spec.name,
        bindings=bindings,
        attachment_asset=spec.attachment_asset,
        supports=asset.targets,
    )
    return Fiber(**state)


def captured_binding(point: str, target: Any, scope: str, indices: Any, asset: Any) -> FiberBinding:
    index = asset.field.path.count + 3 * indices[point]
    binding = tuple(asset.field.bindings[index, 0])
    capture = asset.targets[asset.field.owners[index, 0]]
    return FiberBinding(
        point,
        target.target,
        Attachment(child_mode="OBJECT_ORIGIN", binding=binding),
        scope,
        target.role,
        capture.material_asset,
    )


def publish(session: "Session", spec: "FiberCreation", origin: int, payload: Any) -> None:
    source, item, path, attachment = payload
    ports = inputs(source, spec)
    if revisions(source, ports) != revisions(session.document, ports):
        raise ValueError("Fiber capture inputs changed before publication.")
    key = str(uuid4())
    item = replace(
        item, result=EvaluationResult(key, 1, item.construction_revision, revisions(source, ports))
    )
    proof = authored_jobs.Capture(item.result.inputs, partial(enqueue, session, spec, origin))
    authored_jobs.publish(session, origin, partial(merge, item=item), proof)
    session.resources.paths[key] = path
    session.resources.attachments[item.attachment_asset] = attachment


def merge(document: Any, item: Fiber) -> Any:
    if any(s.reference.target not in document.registry.anatomy for s in item.supports):
        return document
    if not matches(document, item.result):
        item = replace(item, result=EvaluationResult(status="pending"))
    return authored_jobs.append_object(document, item)
