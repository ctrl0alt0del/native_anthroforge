"""SCP calculations reserve complete output sets and publish coherent results."""

from dataclasses import replace
from threading import Event
from typing import TYPE_CHECKING

from anthroforge.core.document import Document
from anthroforge.core.entities import SCP, descendants
from anthroforge.core.jobs import Job
from anthroforge.native.attachments import capture, ordered, propagate
from anthroforge.native.mesh import GeometryEngine, Mesh, NativeCancellation

if TYPE_CHECKING:
    from .session import Session


def request(session: "Session", targets: set[str], recapture: set[str] | None = None) -> str:
    captures = set(recapture or ())
    captures |= {
        e.id for e in session.document.entities if e.id in targets and e.status == "edited"
    }
    targets, captures = absorb_overlaps(session, targets, captures)
    job = create_job(session, targets, captures)
    job.cancel = NativeCancellation(session.engine)
    job.priority = session.priority(targets)
    job.captures = frozenset(captures)
    job.retry = lambda: request(session, targets, captures)
    return session.scheduler.submit(job)


def create_job(session: "Session", targets: set[str], captures: set[str]) -> Job:
    return Job(
        "Update SCP attachments",
        frozenset(targets),
        lambda document: (document, {k: v.mesh for k, v in session.assets.items()}),
        lambda payload, cancel: compute(session.engine, payload, targets, captures, cancel),
        lambda result: publish(session, result, targets),
        key="attachments:" + ",".join(sorted(targets)),
    )


def absorb_overlaps(
    session: "Session", targets: set[str], captures: set[str]
) -> tuple[set[str], set[str]]:
    for job in session.scheduler.jobs:
        if job.active and job.key.startswith("attachments:") and targets.intersection(job.outputs):
            targets |= set(job.outputs)
            captures |= set(job.captures)
            session.scheduler.cancel_job(job.id, obsolete=True)
    available = {item.id for item in session.document.entities}
    return targets & available, captures & available


def compute(
    engine: GeometryEngine,
    payload: tuple[Document, dict[str, Mesh]],
    targets: set[str],
    recaptures: set[str],
    cancel: Event,
) -> tuple[Document, list[SCP]]:
    document, meshes = payload
    entities = ordered(document.entities)
    entities = capture_all(engine, entities, meshes, recaptures, cancel)
    if document.attachments_enabled:
        entities = propagate(engine, entities, meshes, targets, cancel)
    return document, entities


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


def publish(session: "Session", result: tuple[Document, list[SCP]], targets: set[str]) -> None:
    source, entities = result
    validate_inputs(session, source, targets)
    changed = {item.id: merge_result(session, item) for item in entities if item.id in targets}
    session.replace_entities(changed, authored=False)
    failed = [item for item in changed.values() if item.status == "failed"]
    if failed:
        raise ValueError("; ".join(f"{item.name}: {item.error}" for item in failed))


def merge_result(session: "Session", item: SCP) -> SCP:
    current = session.document.entity(item.id)
    return replace(item, generation=item.generation + 1, name=current.name, color=current.color)


def validate_inputs(session: "Session", source: Document, targets: set[str]) -> None:
    current = {item.id: item for item in session.document.entities}
    relevant = input_ids(source, targets)
    if any(
        item.id not in current or current[item.id].generation != item.generation
        for item in source.entities
        if item.id in relevant
    ):
        raise ValueError("Attachment inputs changed before publication.")


def affected(document: Document, entity_id: str) -> set[str]:
    return descendants(document.entities, entity_id)
