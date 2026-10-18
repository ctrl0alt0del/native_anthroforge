"""Curve path jobs use the same coordinator, revision contracts and result lifetime as meshes."""

from dataclasses import replace
from functools import partial
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from anthroforge.core.construction import Curve
from anthroforge.core.document import Document
from anthroforge.core.jobs import Job
from anthroforge.core.results import EvaluationResult, Port
from anthroforge.core.scheduling import Workload
from anthroforge.native.mesh import NativeCancellation

from . import curve_evaluation
from . import dependencies as dep
from .construction_policy import mode, revisions
from .curve_sources import source
from .evaluation_results import accepted_result

if TYPE_CHECKING:
    from .session import Session


def request(session: "Session", curve: str, interactive: bool = False) -> str:
    job = make_job(session, curve)
    job.cancel = NativeCancellation(session.engine)
    job.interactive, job.priority = interactive, session.priority({curve})
    job.publish_during_edit = job.restart_on_redo = True
    job.retry = partial(request, session, curve)
    job.cleanup = partial(completed, session, curve, job)
    job.workload = partial(workload, curve)
    dep.contract(job, session.document, {Port(curve, "path")})
    return session.scheduler.submit(job)


def make_job(session: "Session", curve: str) -> Job:
    reads = frozenset(p.owner for p in dep.ports(session.document, Port(curve, "path")))
    return Job(
        "Evaluate " + source(session.document, curve).name,
        frozenset((curve,)),
        lambda document: (document, session.resources.snapshot()),
        partial(compute, session, curve),
        partial(publish, session, curve),
        key="path:" + curve,
        kind="curve_path",
        reads=reads,
    )


def workload(curve: str, document: Document) -> Workload:
    item = source(document, curve)
    return Workload(
        affected=1,
        candidates=len(item.points),
        triangles=len(item.points) * (item.resolution if item.engine == "BEZIER" else 1),
    )


def compute(session: "Session", curve: str, payload: Any, cancel: Any) -> Any:
    document, resources = payload
    if Port(curve, "path") in dep.blocked(dep.graph(document)):
        raise ValueError("Cyclic or missing curve dependency; last accepted path retained.")
    return document, curve_evaluation.evaluate(
        session.engine, document, resources, curve, cancel.handle
    )


def publish(session: "Session", curve: str, payload: Any) -> None:
    document, asset = payload
    inputs = dep.ports(document, Port(curve, "path"))
    if revisions(document, inputs) != revisions(session.document, inputs):
        raise ValueError("Curve inputs changed before publication.")
    item = source(session.document, curve)
    key = str(uuid4())
    session.resources.paths[key] = asset
    result = accepted_result(document, item, inputs, key)
    install_result(session, curve, result)
    propagate(session, curve)


def install_result(session: "Session", curve: str, result: EvaluationResult) -> None:
    objects = tuple(
        replace(o, result=result) if o.id == curve else o for o in session.document.objects
    )
    session.replace_document(objects=objects)


def completed(session: "Session", curve: str, job: Job, state: str) -> None:
    if state == "failed" and curve in session.document.registry.construction:
        result = replace(source(session.document, curve).result, status="failed", error=job.error)
        install_result(session, curve, result)


def propagate(session: "Session", curve: str) -> None:
    from .construction_tasks import edited

    targets = dep.affected(session.document, {Port(curve, "path")})
    waiting = set().union(
        *(
            job.outputs
            for job in session.scheduler.active_jobs
            if job.kind == "construction" and job.future is None
        )
    )
    edited(session, targets - waiting)


def schedule(
    session: "Session", targets: set[str], released: bool = False, explicit: bool = False
) -> list[str]:
    scheduled = []
    for item in session.document.objects:
        if isinstance(item, Curve) and item.id in targets:
            setting = mode(session.document, item.id)
            if explicit or setting == "LIVE" or (released and setting == "ON_RELEASE"):
                scheduled.append(request(session, item.id, interactive=not released))
    return scheduled


def edited(session: "Session", seeds: set[Port]) -> None:
    outputs = dep.closure(dep.reverse(dep.graph(session.document)), seeds)
    curves = {p.owner for p in outputs if p.output == "path"}
    objects = tuple(
        replace(o, result=replace(o.result, status="pending")) if o.id in curves else o
        for o in session.document.objects
    )
    if curves:
        session.replace_document(objects=objects)
        schedule(session, curves)


def prerequisites(session: "Session", target: str, explicit: bool = False) -> None:
    ports = dep.ports(session.document, Port(target, "geometry"))
    active = set().union(*(job.provides for job in session.scheduler.active_jobs))
    curves = {p.owner for p in ports if p.output == "path" and p not in active}
    needed = {
        key
        for key in curves
        if not source(session.document, key).result.asset
        or (explicit and source(session.document, key).result.status == "pending")
    }
    for key in needed:
        if explicit or mode(session.document, key) == "LIVE":
            request(session, key)  # Register prerequisites before any inline consumer publication.


def pending(session: "Session", released: bool = False) -> None:
    targets = {
        o.id
        for o in session.document.objects
        if o.result.status == "pending"
        and (not released or mode(session.document, o.id) == "ON_RELEASE")
    }
    schedule(session, targets, released=released)
