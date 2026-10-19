"""Tissue phases use the shared coordinator, exclusive writers and complete read validation."""

from functools import partial
from typing import Any

from anthroforge.core.jobs import Job
from anthroforge.core.results import Port
from anthroforge.core.scheduling import Workload
from anthroforge.core.tissue_revisions import PHASES
from anthroforge.core.tissues import TissueVCP
from anthroforge.native.mesh import NativeCancellation

from . import dependencies as dep
from . import tissue_evaluation, tissue_results
from .construction_policy import mode, revisions


def request(session: Any, target: str, phase: str, interactive: bool = False) -> str:
    job = make_job(session, target, phase)
    job.cancel = NativeCancellation(session.engine)
    job.interactive, job.priority = interactive, session.priority({target})
    job.publish_during_edit = job.restart_on_redo = True
    job.retry = partial(request, session, target, phase)
    job.cleanup = partial(completed, session, target, phase, job)
    job.workload = partial(workload, session, target, phase)
    dep.contract(job, session.document, {Port(target, phase)})
    return str(session.scheduler.submit(job))


def make_job(session: Any, target: str, phase: str) -> Job:
    reads = frozenset(p.owner for p in dep.ports(session.document, Port(target, phase)))
    return Job(
        "Tissue " + phase + ": " + session.document.object(target).name,
        frozenset((target,)),
        lambda doc: (doc, session.resources.snapshot()),
        partial(compute, session, target, phase),
        partial(publish, session, target, phase),
        key="tissue:" + phase + ":" + target,
        kind="tissue_" + phase,
        reads=reads,
    )


def workload(session: Any, target: str, phase: str, document: Any) -> Workload:
    item = document.object(target)
    keys = (item.base_result.asset, item.rest_result.asset, item.intrinsic_result.asset)
    vertices = max(
        (session.assets[k].mesh.counts[0] for k in keys if k in session.assets), default=0
    )
    return Workload(
        affected=1, candidates=vertices, triangles=2 * vertices, entities=len(item.parts)
    )


def compute(session: Any, target: str, phase: str, payload: Any, cancel: Any) -> Any:
    document, resources = payload
    if Port(target, phase) in dep.blocked(dep.graph(document)):
        raise ValueError("Cyclic or missing tissue dependency; accepted geometry retained.")
    return document, tissue_evaluation.evaluate(
        session.engine, document, resources, target, phase, cancel.handle
    )


def publish(session: Any, target: str, phase: str, payload: Any) -> None:
    from .output_tasks import propagate

    document, mesh = payload
    ports = dep.ports(document, Port(target, phase))
    if revisions(document, ports) != revisions(session.document, ports):
        raise ValueError("Tissue inputs changed before publication.")
    tissue_results.publish(session, document, target, phase, mesh, ports)
    propagate(session, {Port(target, phase)})


def completed(session: Any, target: str, phase: str, job: Job, state: str) -> None:
    if state == "failed":
        tissue_results.fail(session, target, phase, job.error)


def schedule(
    session: Any, targets: set[str], released: bool = False, explicit: bool = False
) -> list[str]:
    jobs = []
    for item in session.document.registry.anatomy.values():
        if not isinstance(item, TissueVCP) or item.id not in targets:
            continue
        setting = mode(session.document, item.id)
        if explicit or setting == "LIVE" or (released and setting == "ON_RELEASE"):
            jobs.extend(schedule_phases(session, item, explicit, not released))
    return jobs


def schedule_phases(session: Any, item: TissueVCP, explicit: bool, interactive: bool) -> list[str]:
    active = set().union(*(j.provides for j in session.scheduler.active_jobs))
    needed = [
        phase
        for phase in PHASES
        if Port(item.id, phase) not in active
        and (
            explicit
            or getattr(item, phase + "_result").status == "pending"
            or not getattr(item, phase + "_result").asset
        )
    ]
    return [request(session, item.id, phase, interactive) for phase in needed]


def edited(session: Any, seeds: set[Port]) -> None:
    ports = dep.closure(dep.reverse(dep.graph(session.document)), seeds)
    targets = {p.owner for p in ports if p.output in PHASES}
    for key in targets:
        item = session.document.object(key)
        if isinstance(item, TissueVCP):
            tissue_results.install(
                session, tissue_results.pending(item, {p.output for p in ports if p.owner == key})
            )
    schedule(session, targets)


def pending(session: Any, released: bool = False) -> None:
    targets = {
        o.id
        for o in session.document.objects
        if isinstance(o, TissueVCP) and o.result.status == "pending"
    }
    schedule(session, targets, released=released)
