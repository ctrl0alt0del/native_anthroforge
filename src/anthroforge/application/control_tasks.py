"""Control-frame writers participate in the same coordinator as geometry writers."""

from dataclasses import replace
from functools import partial
from typing import TYPE_CHECKING, Any

from anthroforge.core.construction import Control
from anthroforge.core.document import Document
from anthroforge.core.jobs import Job
from anthroforge.core.results import ControlResult
from anthroforge.core.scheduling import Workload
from anthroforge.native.mesh import NativeCancellation

from . import dependencies as dep
from .construction_evaluator import Evaluation
from .construction_policy import revisions

if TYPE_CHECKING:
    from .session import Session


def inputs(document: Document, control: str) -> set[str]:
    ports = dep.closure(dep.graph(document), {dep.Port(control, "control")})
    return {p.owner for p in ports}


def make_job(session: "Session", control: str) -> Job:
    item, reads = session.document.control(control), inputs(session.document, control)
    return Job(
        "Resolve " + item.name,
        frozenset({control}),
        partial(prepare, session),
        partial(compute, session, control),
        partial(publish, session, control),
        kind="control_attachments",
        key="control:" + control,
        reads=frozenset(reads),
    )


def request(session: "Session", control: str) -> str:
    job = make_job(session, control)
    job.cancel = NativeCancellation(session.engine)
    job.interactive, job.priority = True, session.priority({control})
    job.publish_during_edit = job.restart_on_redo = True
    job.retry, job.cleanup = (
        partial(request, session, control),
        partial(finished, session, control, job),
    )
    job.workload = partial(workload, session, control)
    dep.contract(job, session.document, {dep.Port(control, "control")})
    return session.scheduler.submit(job)


def prepare(session: "Session", document: Document) -> Any:
    return document, {key: asset.mesh for key, asset in session.assets.items()}


def workload(session: "Session", control: str, document: Document) -> Workload:
    ids = inputs(document, control)
    meshes = [session.assets[e.asset].mesh for e in document.entities if e.id in ids and e.asset]
    return Workload(
        entities=len(document.entities),
        affected=1,
        candidates=len(ids),
        triangles=sum(m.counts[3] for m in meshes),
    )


def compute(session: "Session", control: str, payload: Any, cancel: Any) -> Any:
    document, meshes = payload
    if dep.Port(control, "control") in dep.blocked(dep.graph(document)):
        raise ValueError("Cyclic or missing control dependency; last accepted frame retained.")
    evaluator = Evaluation(session.engine, document, meshes, cancel)
    matrix = evaluator.control_frame(document.control(control))
    return document, matrix, evaluator.bindings.get(control, ())


def publish(session: "Session", control: str, payload: Any) -> None:
    document, matrix, binding = payload
    read_set = dep.ports(document, dep.Port(control, "control"))
    if revisions(document, read_set) != revisions(session.document, read_set):
        raise ValueError("Control inputs changed before publication.")
    item = session.document.control(control)
    result = ControlResult(
        matrix, revisions(document, read_set), item.result.revision + 1, binding=binding
    )
    install_result(session, control, result)


def install_result(session: "Session", control: str, result: ControlResult) -> None:
    controls = tuple(
        replace(c, result=result) if c.id == control else c for c in session.document.controls
    )
    session.replace_document(controls=controls)


def finished(session: "Session", control: str, job: Job, state: str) -> None:
    if state != "failed" or not any(c.id == control for c in session.document.controls):
        return
    item = session.document.control(control)
    install_result(session, control, replace(item.result, status="failed", error=job.error))


def affected(document: Document, seeds: set[dep.Port]) -> set[str]:
    ports = dep.closure(dep.reverse(dep.graph(document)), seeds)
    return {p.owner for p in ports if p.output == "control"}


def edited(session: "Session", seeds: set[dep.Port]) -> None:
    targets = affected(session.document, seeds)
    if not targets:
        return
    session.scheduler.invalidate(targets)
    controls = tuple(pending(c) if c.id in targets else c for c in session.document.controls)
    session.replace_document(controls=controls)
    for control in targets:
        request(session, control)


def pending(control: Control) -> Control:
    return replace(control, result=replace(control.result, status="pending", error=""))


def resume(session: Any) -> None:
    for control in session.document.controls:
        if control.result.status == "pending":
            request(session, control.id)
