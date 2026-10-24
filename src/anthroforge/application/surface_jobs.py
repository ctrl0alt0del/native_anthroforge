"""Creation and explicit correspondence rebuild publish in their initiating undo step."""

from functools import partial
from typing import Any
from uuid import uuid4

from anthroforge.core.dependency_graph import curve_inputs
from anthroforge.core.jobs import Job
from anthroforge.core.mirror_dependencies import inputs as mirror_inputs
from anthroforge.core.results import Port
from anthroforge.core.surfaces import Surface
from anthroforge.native.mesh import NativeCancellation

from . import (
    authored_jobs,
    construction_tasks,
    path_tasks,
    surface_evaluation,
    surface_history,
    surface_results,
)
from . import dependencies as dep
from .assets import Asset
from .construction_policy import revisions
from .evaluation_results import accepted_result
from .object_revisions import authored


def inputs(document: Any, item: Surface, existing: bool) -> set[Port]:
    seeds = set().union(*(curve_inputs(use, document.objects) for use in item.curves))
    seeds |= mirror_inputs(item)
    if existing:
        seeds.add(Port(item.id, "geometry"))
    return dep.closure(dep.graph(document), seeds)


def enqueue(session: Any, item: Surface, existing: bool, origin: int) -> str:
    path_tasks.require_inputs(session, inputs(session.document, item, existing))
    job = make_job(session, item, existing, origin)
    job.cancel = NativeCancellation(session.engine)
    job.restart_on_input_change = True
    job.retry = partial(enqueue, session, item, existing, origin)
    job.observes = frozenset(inputs(session.document, item, existing))
    job.provides = frozenset((Port(item.id, "geometry"),))
    job.prerequisites = job.observes - job.provides
    job.reads = frozenset(port.owner for port in job.observes)
    job.workload = lambda document: construction_tasks.surface_workload(session, item, document)
    return str(session.scheduler.submit(job))


def make_job(session: Any, item: Surface, existing: bool, origin: int) -> Job:
    return Job(
        ("Realign " if existing else "Create ") + item.name,
        frozenset((item.id,)),
        lambda document: (document, session.resources.snapshot()),
        partial(compute, session, item, existing),
        partial(publish, session, item, existing, origin),
        key="surface-layout:" + item.id,
        kind="surface_layout",
    )


def compute(session: Any, item: Surface, existing: bool, payload: Any, cancel: Any) -> Any:
    document, resources = payload
    if existing and document.object(item.id).generation != item.generation:
        raise ValueError("Surface changed before layout began; request Realign again.")
    placed = surface_evaluation.layout(session.engine, document, resources, item, cancel.handle)
    placed = authored(item, placed) if existing else placed
    mesh = surface_evaluation.evaluate(session.engine, document, resources, placed, cancel.handle)
    return document, placed, mesh


def publish(session: Any, item: Surface, existing: bool, origin: int, payload: Any) -> None:
    document, placed, mesh = payload
    ports = inputs(document, item, existing)
    if revisions(document, ports) != revisions(session.document, ports):
        raise ValueError("Surface inputs changed before layout publication.")
    key = str(uuid4())
    result = accepted_result(document, placed, ports, key)
    ready = surface_results.accepted(placed, result)
    merge = partial(surface_history.merge, ready=ready, original=item, existing=existing)
    authored_jobs.publish(session, origin, merge)
    session.assets[key] = Asset(mesh, "generated", "", 1.0, False)
    construction_tasks.propagate_result(session, ready.id)
