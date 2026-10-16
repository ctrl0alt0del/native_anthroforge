"""Construction job admission and complete, revision-checked result publication."""

from dataclasses import replace
from functools import partial
from typing import TYPE_CHECKING, Any, cast
from uuid import uuid4

from anthroforge.core.document import Document
from anthroforge.core.jobs import Job
from anthroforge.core.results import EvaluationResult
from anthroforge.core.scheduling import Workload
from anthroforge.native.mesh import NativeCancellation

from . import dependencies as dep
from .assets import Asset
from .construction_evaluator import Evaluation
from .construction_policy import mode, revisions
from .construction_scheduling import stages

if TYPE_CHECKING:
    from .session import Session


def request(session: "Session", entity: str, interactive: bool = False) -> str:
    job = make_job(session, entity)
    job.cancel = NativeCancellation(session.engine)
    job.interactive, job.priority = interactive, session.priority({entity})
    job.publish_during_edit = job.restart_on_redo = True
    job.retry = partial(request, session, entity)
    job.workload = partial(workload, session, entity)
    job.cleanup = partial(completed, session, entity, job)
    dep.contract(job, session.document, {dep.Port(entity, "geometry")})
    return session.scheduler.submit(job)


def make_job(session: "Session", entity: str) -> Job:
    job = Job(
        "Evaluate " + session.document.entity(entity).name,
        frozenset((entity,)),
        lambda document: (document, {k: a.mesh for k, a in session.assets.items()}),
        partial(compute, session, entity),
        partial(publish, session, entity),
        key="construction:" + entity,
        kind="construction",
        reads=frozenset(dep.reads(session.document, entity)),
    )
    return job


def workload(session: "Session", entity: str, document: Document) -> Workload:
    item = document.entity(entity)
    primitive = item.primitive
    points = sum(len(c.points) for c in primitive.curves) if primitive else 0
    vertices = primitive.samples * max(len(primitive.curves), 1) if primitive else 0
    return Workload(
        entities=len(document.entities),
        affected=1,
        candidates=points,
        triangles=vertices * (primitive.strips if primitive else 1) * 2,
        stages=stages(session, document, entity),
    )


def compute(session: "Session", entity: str, payload: Any, cancel: Any) -> Any:
    document, meshes = payload
    if dep.Port(entity, "geometry") in dep.blocked(dep.graph(document)):
        raise ValueError(
            "Cyclic or missing construction dependency; last accepted geometry retained."
        )
    evaluator = Evaluation(session.engine, document, meshes, cast(NativeCancellation, cancel))
    return document, evaluator.geometry(document.entity(entity))


def publish(session: "Session", entity: str, result: Any) -> None:
    source, mesh = result
    inputs = dep.ports(source, dep.Port(entity, "geometry"))
    if revisions(source, inputs) != revisions(session.document, inputs):
        raise ValueError("Construction inputs changed before publication.")
    item = session.document.entity(entity)
    key = str(uuid4())
    session.assets[key] = Asset(mesh, "generated", "", 1.0, False)
    accepted = accepted_result(source, item, inputs, key)
    changed = install_result(item, key, accepted)
    session.replace_entities({entity: changed}, authored=False)
    propagate_result(session, entity)


def install_result(item: Any, key: str, accepted: EvaluationResult) -> Any:
    return replace(
        item,
        asset=key,
        result=accepted,
        result_generation=item.result_generation + 1,
        status="ready",
        error="",
    )


def accepted_result(
    source: Document, item: Any, inputs: set[dep.Port], key: str
) -> EvaluationResult:
    pending = tuple(
        e.id
        for e in source.entities
        if dep.Port(e.id, "geometry") in inputs and e.id != item.id and e.result.status == "pending"
    )
    return EvaluationResult(
        key,
        item.result.revision + 1,
        item.construction_revision,
        revisions(source, inputs),
        pending,
    )


def completed(session: "Session", entity: str, job: Job, state: str) -> None:
    if state == "failed" and any(e.id == entity for e in session.document.entities):
        item = session.document.entity(entity)
        result = replace(item.result, status="failed", error=job.error)
        session.replace_entities(
            {entity: replace(item, result=result, error=job.error, status="failed")}, authored=False
        )


def propagate_result(session: "Session", entity: str) -> None:
    from anthroforge.core.entities import descendants

    from . import evaluation
    from .control_tasks import edited as controls_edited

    controls_edited(session, {dep.Port(entity, "geometry")})
    targets = descendants(session.document.entities, entity) - {entity}
    live = {key for key in targets if mode(session.document, key) != "MANUAL"}
    if live and session.document.attachments_enabled:
        evaluation.request(session, live)
    affected = dep.affected(session.document, {dep.Port(entity, "geometry")}) - {entity}
    schedule(session, affected)


def schedule(
    session: "Session", targets: set[str], released: bool = False, explicit: bool = False
) -> list[str]:
    scheduled = []
    for entity in session.document.entities:
        if entity.id in targets and entity.primitive:
            setting = mode(session.document, entity.id)
            if explicit or setting == "LIVE" or (released and setting == "ON_RELEASE"):
                scheduled.append(request(session, entity.id, interactive=not released))
    return scheduled


def edited(session: "Session", targets: set[str]) -> None:
    if not targets:
        return
    targets = dep.affected(session.document, {dep.Port(key, "geometry") for key in targets})
    changed = {
        e.id: replace(e, result=replace(e.result, status="pending"))
        for e in session.document.entities
        if e.id in targets and e.primitive
    }
    session.replace_entities(changed, authored=False)
    schedule(session, targets)


def evaluate(session: "Session", entities: list[str] | None = None) -> list[str]:
    targets = set(entities) if entities is not None else {e.id for e in session.document.entities}
    for entity in tuple(targets):
        targets.update(
            dep.reads(session.document, entity) & {e.id for e in session.document.entities}
        )
    return schedule(session, targets, explicit=True)
