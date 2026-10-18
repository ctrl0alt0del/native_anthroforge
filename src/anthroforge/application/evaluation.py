"""SCP calculations reserve complete output sets and publish coherent results."""

from dataclasses import replace
from functools import partial
from threading import Event
from typing import TYPE_CHECKING

from anthroforge.core.document import Document
from anthroforge.core.entities import SCP, descendants
from anthroforge.core.jobs import Job
from anthroforge.core.results import Port
from anthroforge.native.attachments import capture, ordered, propagate
from anthroforge.native.mesh import GeometryEngine, Mesh, NativeCancellation

from . import dependencies, task_workloads

if TYPE_CHECKING:
    from .session import Session


def request(
    session: "Session",
    targets: set[str],
    recapture: set[str] | None = None,
    interactive: bool = False,
    queued_since: float | None = None,
) -> str:
    captures = captures_for(session.document, targets, recapture)
    targets, captures, pending = absorb_overlaps(session, targets, captures)
    job = create_job(session, targets, captures)
    job.interactive = interactive
    job.queued_since = min((p for p in (queued_since, pending) if p is not None), default=None)
    return session.scheduler.submit(job)


def captures_for(document: Document, targets: set[str], requested: set[str] | None) -> set[str]:
    return set(requested or ()) | {
        e.id for e in document.entities if e.id in targets and e.status == "edited"
    }


def configure_job(session: "Session", job: Job, targets: set[str], captures: set[str]) -> None:
    job.cancel = NativeCancellation(session.engine)
    job.priority = session.priority(targets)
    job.captures = frozenset(captures)
    job.retry = lambda: request(session, targets, captures)
    job.kind = "attachments"
    job.workload = partial(task_workloads.attachments, session, targets, captures)
    job.publish_during_edit = job.restart_on_redo = True
    job.reads = frozenset(input_ids(session.document, targets))
    dependencies.contract(job, session.document, {Port(key, "pose") for key in targets})
    job.observes |= frozenset(capture_reads(session.document, captures))


def create_job(session: "Session", targets: set[str], captures: set[str]) -> Job:
    job = Job(
        "Update SCP attachments",
        frozenset(targets),
        lambda document: (document, {k: v.mesh for k, v in session.assets.items()}),
        lambda payload, cancel: compute(session.engine, payload, targets, captures, cancel),
        lambda result: publish(session, result, targets, captures),
        key="attachments:" + ",".join(sorted(targets)),
    )
    configure_job(session, job, targets, captures)
    return job


def absorb_overlaps(
    session: "Session", targets: set[str], captures: set[str]
) -> tuple[set[str], set[str], float | None]:
    pending = []
    for job in session.scheduler.active_jobs:
        if job.active and job.key.startswith("attachments:") and targets.intersection(job.outputs):
            targets |= set(job.outputs)
            captures |= set(job.captures)
            if job.queued_since is not None:
                pending.append(job.queued_since)
            session.scheduler.cancel_job(job.id, obsolete=True, reason="dependency_changed")
    available = {item.id for item in session.document.entities}
    return targets & available, captures & available, min(pending, default=None)


def compute(
    engine: GeometryEngine,
    payload: tuple[Document, dict[str, Mesh]],
    targets: set[str],
    recaptures: set[str],
    cancel: Event,
) -> tuple[Document, list[SCP]]:
    document, meshes = payload
    blocked = cyclic_targets(document, targets)
    entities = ordered(document.entities)
    entities = capture_all(engine, entities, meshes, recaptures - blocked, cancel)
    if document.attachments_enabled:
        entities = propagate(engine, entities, meshes, targets - blocked, cancel)
    return document, cycle_failures(entities, blocked)


def cyclic_targets(document: Document, targets: set[str]) -> set[str]:
    blocked = dependencies.blocked(dependencies.graph(document))
    return {key for key in targets if Port(key, "pose") in blocked}


def cycle_failures(entities: list[SCP], blocked: set[str]) -> list[SCP]:
    return [
        replace(e, status="failed", error="Cyclic pose dependency; last accepted pose retained.")
        if e.id in blocked
        else e
        for e in entities
    ]


def capture_all(
    engine: GeometryEngine,
    entities: list[SCP],
    meshes: dict[str, Mesh],
    recaptures: set[str],
    cancel: Event,
) -> list[SCP]:
    lookup = {item.id: item for item in entities}
    for index, item in enumerate(entities):
        if cancel.is_set():
            return entities
        if item.id in recaptures and item.parent:
            entities[index] = capture_safely(engine, item, lookup[item.parent], meshes)
    return entities


def capture_safely(engine: GeometryEngine, item: SCP, parent: SCP, meshes: dict[str, Mesh]) -> SCP:
    try:
        if item.capture_parent_matrix:
            parent = replace(
                parent,
                matrix=item.capture_parent_matrix,
                geometry_offset=item.capture_parent_offset,
            )
        captured = capture(engine, item, parent, meshes)
        return replace(captured, status="ready", error="", capture_parent_matrix=())
    except ValueError as error:
        return replace(item, status="failed", error=str(error))


def input_ids(document: Document, targets: set[str]) -> set[str]:
    result = set(targets)
    for entity_id in tuple(targets):
        parent = document.entity(entity_id).parent
        while parent:
            result.add(parent)
            parent = document.entity(parent).parent
    return result


def publish(
    session: "Session", result: tuple[Document, list[SCP]], targets: set[str], captures: set[str]
) -> None:
    source, entities = result
    validate_inputs(session, source, targets, captures)
    changed = {item.id: merge_result(session, item) for item in entities if item.id in targets}
    session.replace_entities(changed, authored=False)
    publish_pose_dependents(session, source, changed)
    failed = [item for item in changed.values() if item.status == "failed"]
    if failed:
        raise ValueError("; ".join(f"{item.name}: {item.error}" for item in failed))


def publish_pose_dependents(session: "Session", source: Document, changed: dict[str, SCP]) -> None:
    from .dependencies import Port
    from .dependent_tasks import changed as changed_outputs

    seeds = {
        Port(key, "pose")
        for key, item in changed.items()
        if item.matrix != source.entity(key).matrix
    }
    changed_outputs(session, seeds)


def merge_result(session: "Session", item: SCP) -> SCP:
    current = session.document.entity(item.id)
    return replace(
        current,
        result_generation=current.result_generation + 1,
        matrix=item.matrix,
        geometry_offset=item.geometry_offset,
        attachment=item.attachment,
        status=item.status,
        error=item.error,
        capture_parent_matrix=item.capture_parent_matrix,
        capture_parent_offset=item.capture_parent_offset,
    )


def validate_inputs(
    session: "Session", source: Document, targets: set[str], captures: set[str]
) -> None:
    from .construction_policy import revisions

    ports = dependencies.closure(dependencies.graph(source), {Port(key, "pose") for key in targets})
    ports |= capture_reads(source, captures)
    if revisions(source, ports) != revisions(session.document, ports):
        raise ValueError("Attachment inputs changed before publication.")


def capture_reads(document: Document, captures: set[str]) -> set[Port]:
    # Child anchors are captured once in local coordinates; propagation does not read
    # the child's changing mesh. Capture observes its accepted mesh without making a
    # permanent geometry-to-pose dependency (which would falsely cycle pose-following cages).
    return {
        Port(e.id, "geometry")
        for e in document.entities
        if e.id in captures and e.parent and e.attachment.child_mode != "OBJECT_ORIGIN"
    }


def affected(document: Document, entity_id: str) -> set[str]:
    return descendants(document.entities, entity_id)
