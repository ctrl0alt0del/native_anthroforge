"""Import is atomic: failed/cancelled jobs never leave half-created SCPs."""

from dataclasses import replace
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, cast
from uuid import uuid4

from anthroforge.core.construction import Primitive
from anthroforge.core.document import Document
from anthroforge.core.entities import SCP
from anthroforge.core.jobs import Job
from anthroforge.core.results import EvaluationResult
from anthroforge.native.mesh import NativeCancellation

from . import authored_jobs
from .assets import Asset, imported
from .operations import origin_if_empty, parent_for, require_name
from .presentation import include_created
from .task_workloads import source_file

if TYPE_CHECKING:
    from .session import Session


def import_mesh(
    session: "Session",
    path: str,
    units: float,
    parent: str = "",
    y_up: bool = False,
    name: str = "",
) -> dict[str, str]:
    source, entity = prepare_import(session, path, parent, name)
    job = authored_jobs.begin(session, partial(enqueue, session, source, units, y_up, entity))
    return {"entity_id": entity.id, "job_id": job}


def prepare_import(session: "Session", path: str, parent: str, name: str) -> tuple[Path, SCP]:
    source = Path(path).resolve(strict=True)
    parent = parent_for(session, parent)
    return source, imported_entity(session, require_name(name or source.stem), parent)


def imported_entity(session: "Session", name: str, parent: str) -> SCP:
    entity = SCP(name, parent=parent, asset=str(uuid4()))
    entity = replace(
        entity,
        primitive=Primitive("IMPORTED", source=entity.asset),
        result=EvaluationResult(asset=entity.asset),
    )
    if parent:
        entity = replace(entity, attachment=origin_if_empty(session, parent, entity.attachment))
    return entity


def enqueue(
    session: "Session", source: Path, units: float, y_up: bool, entity: SCP, origin: int
) -> str:
    if any(item.id == entity.id for item in session.document.entities):
        return ""
    job = Job(
        "Import " + source.name,
        frozenset((entity.id, "@hierarchy")),
        lambda document: document,
        partial(import_asset, session, source, units, y_up),
        lambda result: publish(session, entity, origin, result),
    )
    configure_job(session, job, source, units, y_up, entity, origin)
    return session.scheduler.submit(job)


def configure_job(
    session: "Session", job: Job, source: Path, units: float, y_up: bool, entity: SCP, origin: int
) -> None:
    job.cancel = NativeCancellation(session.engine)
    job.retry = partial(enqueue, session, source, units, y_up, entity, origin)
    job.kind = "mesh_import"
    job.workload = partial(source_file, source)


def import_asset(
    session: "Session", source: Path, units: float, y_up: bool, document: object, event: object
) -> Asset:
    return imported(session.engine, source, units, y_up, cast(NativeCancellation, event))


def publish(session: "Session", entity: SCP, origin: int, asset: Asset) -> None:
    validate_parent(session, entity.parent)
    session.assets[entity.asset] = asset
    authored_jobs.publish(session, origin, partial(merge_entity, entity))
    include_created(session, {entity.id})
    if entity.parent:
        from .evaluation import request

        request(session, {entity.id}, {entity.id})


def validate_parent(session: "Session", parent: str) -> None:
    if parent:
        session.document.entity(parent)
    elif session.document.entities:
        raise ValueError("Document already has a root; import under an existing SCP.")


def merge_entity(entity: SCP, document: Document) -> Document:
    if entity.id in document.index.entities:
        return document
    if entity.parent and entity.parent not in document.index.entities:
        return document
    return replace(document, entities=(*document.entities, entity))
