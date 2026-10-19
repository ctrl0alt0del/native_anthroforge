"""Retained Anchor bindings use coordinated, revision-checked output jobs."""

from dataclasses import replace
from functools import partial
from typing import TYPE_CHECKING, Any

from anthroforge.core.jobs import Job
from anthroforge.core.points import Anchor
from anthroforge.core.results import Port
from anthroforge.core.scheduling import Workload
from anthroforge.native.mesh import NativeCancellation

from . import dependencies as dep
from . import point_evaluation
from .construction_policy import mode, revisions
from .evaluation_results import accepted_result

if TYPE_CHECKING:
    from .session import Session


def request(session: "Session", target: str, interactive: bool = False) -> str:
    job = make_job(session, target)
    job.cancel = NativeCancellation(session.engine)
    job.interactive, job.priority = interactive, session.priority({target})
    job.publish_during_edit = job.restart_on_redo = True
    job.retry = partial(request, session, target)
    job.cleanup = partial(completed, session, target, job)
    job.workload = lambda document: Workload(affected=1, candidates=1, entities=1)
    dep.contract(job, session.document, {Port(target, "binding")})
    return session.scheduler.submit(job)


def make_job(session: Any, target: str) -> Job:
    reads = frozenset(p.owner for p in dep.ports(session.document, Port(target, "binding")))
    return Job(
        "Resolve " + session.document.object(target).name,
        frozenset((target,)),
        lambda document: (document, session.resources.snapshot()),
        partial(compute, session, target),
        partial(publish, session, target),
        key="anchor_binding:" + target,
        kind="anchor_binding",
        reads=reads,
    )


def compute(session: Any, target: str, payload: Any, cancel: Any) -> Any:
    document, resources = payload
    if Port(target, "binding") in dep.blocked(dep.graph(document)):
        raise ValueError("Cyclic or missing Anchor dependency; last accepted position retained.")
    item = document.object(target)
    return document, point_evaluation.resolve(
        session.engine, document, resources.meshes, item, cancel.handle
    )


def publish(session: Any, target: str, payload: Any) -> None:
    from .output_tasks import propagate

    document, resolved = payload
    ports = dep.ports(document, Port(target, "binding"))
    if revisions(document, ports) != revisions(session.document, ports):
        raise ValueError("Anchor inputs changed before publication.")
    current = session.document.object(target)
    result = accepted_result(document, current, ports, "")
    item = adopt(current, resolved, result)
    install_result(session, item)
    propagate(session, {Port(target, "binding")})


def adopt(current: Anchor, resolved: Anchor, result: Any) -> Anchor:
    return replace(
        current,
        resolved_position=resolved.resolved_position,
        resolved_frame=resolved.resolved_frame,
        result=result,
    )


def install_result(session: Any, item: Anchor) -> None:
    session.replace_document(
        objects=tuple(item if o.id == item.id else o for o in session.document.objects)
    )


def completed(session: Any, target: str, job: Job, state: str) -> None:
    if state == "failed" and target in session.document.registry.construction:
        item = session.document.object(target)
        install_result(
            session, replace(item, result=replace(item.result, status="failed", error=job.error))
        )


def schedule(
    session: Any, targets: set[str], released: bool = False, explicit: bool = False
) -> list[str]:
    jobs = []
    for item in session.document.objects:
        if not isinstance(item, Anchor) or item.id not in targets:
            continue
        setting = mode(session.document, item.id)
        if explicit or setting == "LIVE" or (released and setting == "ON_RELEASE"):
            jobs.append(request(session, item.id, interactive=not released))
    return jobs


def edited(session: Any, seeds: set[Port]) -> None:
    ports = dep.closure(dep.reverse(dep.graph(session.document)), seeds)
    targets = {p.owner for p in ports if p.output == "binding"}
    if not targets:
        return
    objects = tuple(
        replace(o, result=replace(o.result, status="pending")) if o.id in targets else o
        for o in session.document.objects
    )
    session.replace_document(objects=objects)
    schedule(session, targets)


def pending(session: Any, released: bool = False) -> None:
    targets = {o.id for o in session.document.objects if o.result.status == "pending"}
    schedule(session, targets, released=released)
