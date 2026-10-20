"""Reserve and publish an entire attached graph as one cancellable authored operation."""

from dataclasses import fields, replace
from functools import partial
from typing import Any

from anthroforge.core.jobs import Job, ObsoleteInputs
from anthroforge.core.object_outputs import output
from anthroforge.core.results import Port
from anthroforge.core.scheduling import Workload
from anthroforge.native.mesh import NativeCancellation

from . import (
    anchor_capture,
    attached_creation,
    attached_creation_compute,
    authored_jobs,
    dependencies,
    fiber_tasks,
    path_tasks,
)
from .construction_policy import revisions


def enqueue(session: Any, original: Any, origin: int) -> str:
    spec = attached_creation.plan(session, original.source, original.name, original.identities)
    spec = replace(spec, tissue=original.tissue)
    ports = inputs(session.document, spec)
    path_tasks.require_inputs(session, ports)
    job = make_job(session, spec, origin)
    job.cancel = NativeCancellation(session.engine)
    job.restart_on_input_change = True
    job.retry = partial(enqueue, session, spec, origin)
    job.observes = job.prerequisites = frozenset(ports)
    job.reads = frozenset(port.owner for port in ports)
    job.provides = frozenset(provided(session.document, spec))
    job.workload = partial(workload, spec)
    return str(session.scheduler.submit(job))


def inputs(document: Any, spec: Any) -> set[Port]:
    seeds = {Port(key, output(document.object(key))) for key in spec.selected}
    seeds |= {Port(key, "pose") for key in spec.selected}
    for capture in spec.fibers:
        seeds |= fiber_tasks.inputs(document, capture)
    if spec.anchor:
        seeds |= anchor_capture.inputs(document, spec.anchor)
    return dependencies.closure(dependencies.graph(document), seeds)


def provided(document: Any, spec: Any) -> set[Port]:
    ports = {Port(spec.identities[key], output(document.object(key))) for key in spec.selected}
    if spec.anchor:
        ports.add(Port(spec.anchor.identity, "binding"))
    return ports


def make_job(session: Any, spec: Any, origin: int) -> Job:
    return Job(
        "Create " + (spec.tissue[1] if spec.tissue else spec.name),
        spec.outputs,
        lambda document: (document, session.resources.snapshot()),
        partial(attached_creation_compute.compute, session, spec),
        partial(publish, session, spec, origin),
        key="attached-construction:" + spec.primary,
        kind="attached_construction",
    )


def workload(spec: Any, document: Any) -> Workload:
    points = sum(len(getattr(document.object(key), "points", ())) for key in spec.selected)
    return Workload(
        affected=len(spec.selected),
        candidates=points * 32,
        entities=len(document.entities),
        triangles=sum(getattr(document.object(key), "samples", 0) * 32 for key in spec.selected),
    )


def publish(session: Any, spec: Any, origin: int, payload: Any) -> None:
    document, objects, links, resources = payload
    ports = inputs(document, spec)
    if revisions(document, ports) != revisions(session.document, ports):
        raise ObsoleteInputs("Attached construction inputs changed before publication.")
    proof = authored_jobs.Capture(
        revisions(document, ports), partial(enqueue, session, spec, origin)
    )
    authored_jobs.publish(session, origin, partial(merge, objects=objects, links=links), proof)
    for field in fields(resources):
        getattr(session.resources, field.name).update(getattr(resources, field.name))
    if spec.tissue:
        from .tissue_tasks import schedule

        schedule(session, {spec.primary}, explicit=True)


def merge(document: Any, objects: Any, links: Any) -> Any:
    existing = document.registry.records
    if any(item.id in existing for item in objects):
        return document
    available = existing.keys() | {item.id for item in objects}
    if any(item.parent and item.parent not in available for item in objects):
        return document
    rows = tuple(
        replace(item, owners=tuple(key for key in item.owners if key in document.registry.anatomy))
        for item in objects
    )
    return replace(
        document, objects=(*document.objects, *rows), junctions=(*document.junctions, *links)
    )
