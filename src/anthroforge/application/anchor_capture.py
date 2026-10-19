"""Async bind capture belongs to its initiating undo action; source points remain unchanged."""

from dataclasses import dataclass, fields, replace
from functools import partial
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from anthroforge.core import anatomical_surfaces
from anthroforge.core.entities import Attachment
from anthroforge.core.jobs import Job
from anthroforge.core.points import Anchor, Point
from anthroforge.core.results import Port
from anthroforge.core.scheduling import Workload
from anthroforge.core.surface_references import SurfaceBinding, SurfaceReference
from anthroforge.native import point_attachments
from anthroforge.native.mesh import NativeCancellation

from . import authored_jobs, dependencies, object_revisions, point_evaluation, surface_providers
from .construction_policy import revisions
from .evaluation_results import accepted_result

if TYPE_CHECKING:
    from .session import Session


@dataclass(frozen=True)
class Capture:
    source: str
    identity: str
    reference: SurfaceReference
    name: str
    position: tuple[float, ...] = ()


def create(session: Any, item: Point, parent: str, role: str, name: str) -> dict[str, str]:
    ref = anatomical_surfaces.reference(parent, session.document.registry.records, role)
    spec = Capture(item.id, str(uuid4()), ref, name)
    job = authored_jobs.begin(session, partial(enqueue, session, spec))
    return dict(object_id=spec.identity, job_id=job)


def rebind(session: Any, item: Anchor, parent: str, role: str, position: Any) -> str:
    ref = anatomical_surfaces.reference(parent, session.document.registry.records, role)
    location = tuple(position) if position is not None else ()
    spec = Capture(item.id, item.id, ref, item.name, location)
    return authored_jobs.begin(session, partial(enqueue, session, spec))


def inputs(document: Any, spec: Capture) -> set[Port]:
    from anthroforge.core.object_outputs import output

    source = document.object(spec.source)
    seeds = {Port(spec.source, output(source)), Port(spec.source, "pose")}
    seeds |= surface_providers.ports(document, (spec.reference,))
    return dependencies.closure(dependencies.graph(document), seeds)


def enqueue(session: "Session", spec: Capture, origin: int) -> str:
    job = make_job(session, spec, origin)
    job.cancel = NativeCancellation(session.engine)
    job.restart_on_input_change = True
    job.retry = partial(enqueue, session, spec, origin)
    job.observes = job.prerequisites = frozenset(inputs(session.document, spec))
    job.reads = frozenset(port.owner for port in job.observes)
    job.provides = frozenset((Port(spec.identity, "binding"),))
    job.workload = lambda document: Workload(affected=1, candidates=1, entities=1)
    return session.scheduler.submit(job)


def make_job(session: Any, spec: Capture, origin: int) -> Job:
    return Job(
        "Bind " + spec.name,
        frozenset((spec.identity,)),
        lambda document: (document, session.resources.snapshot()),
        partial(compute, session, spec),
        partial(publish, session, spec, origin),
        key="anchor_capture:" + spec.identity,
        kind="anchor_capture",
    )


def compute(session: Any, spec: Capture, payload: Any, cancel: Any) -> Any:
    document, resources = payload
    item = document.object(spec.source)
    world = spec.position or point_evaluation.position(session.engine, document, item)
    provider = surface_providers.get(session.engine, document, resources.meshes, spec.reference)
    binding, frame = capture_binding(session.engine, provider, world, cancel.handle)
    return document, point_evaluation.with_frame(copied(item, spec, binding), frame)


def capture_binding(engine: Any, provider: Any, world: Any, cancel: int) -> Any:
    surfaces = ([provider.resource.mesh.handle], [provider.frame])
    targets, records = point_attachments.capture(engine, *surfaces, [world], cancel=cancel)
    attachment = Attachment(child_mode="OBJECT_ORIGIN", binding=tuple(records[0].tolist()))
    binding = SurfaceBinding(provider.reference, attachment, material_asset=provider.asset_id)
    frame = point_attachments.resolve(engine, *surfaces, targets, records, cancel)[0]
    return binding, frame


def copied(item: Point, spec: Capture, binding: SurfaceBinding) -> Anchor:
    state = {f.name: getattr(item, f.name) for f in fields(Point)}
    state.update(id=spec.identity, name=spec.name)
    return Anchor(**state, binding=binding)


def publish(session: Any, spec: Capture, origin: int, payload: Any) -> None:
    document, item = payload
    ports = inputs(document, spec)
    if revisions(document, ports) != revisions(session.document, ports):
        raise ValueError("Anchor capture inputs changed before publication.")
    result = accepted_result(document, item, ports, "")
    authored_jobs.publish(session, origin, partial(merge, item=replace(item, result=result)))
    from .output_tasks import propagate

    propagate(session, {Port(item.id, "binding")})


def merge(document: Any, item: Anchor) -> Any:
    if item.id not in document.registry.records:
        return authored_jobs.append_object(document, item)
    before = document.object(item.id)
    updated = object_revisions.authored(before, item)
    return replace(
        document, objects=tuple(updated if o.id == item.id else o for o in document.objects)
    )
