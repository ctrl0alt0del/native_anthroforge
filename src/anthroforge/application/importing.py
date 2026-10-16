"""Import is atomic: failed/cancelled jobs never leave half-created SCPs."""

from dataclasses import replace
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, cast
from uuid import uuid4

from anthroforge.core.entities import SCP
from anthroforge.core.jobs import Job
from anthroforge.native.mesh import NativeCancellation

from .assets import Asset, imported
from .history import Entry
from .operations import origin_if_empty, parent_for, require_name

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
    session.replace_document()
    origin = session.document.revision
    replay = partial(enqueue, session, source, units, y_up, entity, origin)
    session.replay_callback = replay
    return {"entity_id": entity.id, "job_id": replay()}


def prepare_import(session: "Session", path: str, parent: str, name: str) -> tuple[Path, SCP]:
    source = Path(path).resolve(strict=True)
    parent = parent_for(session, parent)
    return source, imported_entity(session, require_name(name or source.stem), parent)


def imported_entity(session: "Session", name: str, parent: str) -> SCP:
    entity = SCP(name, parent=parent, asset=str(uuid4()))
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
    job.cancel = NativeCancellation(session.engine)
    job.retry = partial(enqueue, session, source, units, y_up, entity, origin)
    return session.scheduler.submit(job)


def import_asset(
    session: "Session", source: Path, units: float, y_up: bool, document: object, event: object
) -> Asset:
    return imported(session.engine, source, units, y_up, cast(NativeCancellation, event))


def publish(session: "Session", entity: SCP, origin: int, asset: Asset) -> None:
    validate_parent(session, entity.parent)
    session.assets[entity.asset] = asset
    found = False
    for entry in session.history.entries[: session.history.cursor + 1]:
        found |= origin in entry.versions
        if found:
            merge_entry(session, entry, entity)
    session.document = session.history.entries[session.history.cursor].document
    if entity.parent:
        from .evaluation import request

        request(session, {entity.id}, {entity.id})


def validate_parent(session: "Session", parent: str) -> None:
    if parent:
        session.document.entity(parent)
    elif session.document.entities:
        raise ValueError("Document already has a root; import under an existing SCP.")


def merge_entry(session: "Session", entry: Entry, entity: SCP) -> None:
    if any(item.id == entity.id for item in entry.document.entities):
        return
    if entity.parent and not any(item.id == entity.parent for item in entry.document.entities):
        return
    session.serial += 1
    entry.document = replace(
        entry.document, revision=session.serial, entities=(*entry.document.entities, entity)
    )
    entry.versions.add(session.serial)
