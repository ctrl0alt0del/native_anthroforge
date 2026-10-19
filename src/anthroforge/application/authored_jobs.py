"""Async authored publication belongs to its initiating undo step, across later edits."""

from collections.abc import Callable
from dataclasses import replace
from functools import partial
from typing import TYPE_CHECKING, Any

from anthroforge.core.document import Document

from .history import Entry

if TYPE_CHECKING:
    from .session import Session


def begin(session: "Session", enqueue: Callable[[int], str]) -> str:
    session.replace_document()
    replay = partial(enqueue, session.document.revision)
    session.replay_callback = replay
    return replay()


def affected(session: "Session", origin: int) -> list[Entry]:
    found, entries = False, []
    for entry in session.history.entries[: session.history.cursor + 1]:
        found |= origin in entry.versions
        if found:
            entries.append(entry)
    if not found:
        raise ValueError("The initiating authored operation no longer exists in active history.")
    return entries


def publish(session: "Session", origin: int, merge: Callable[[Document], Document]) -> None:
    entries = affected(session, origin)
    planned = [(entry, merge(entry.document)) for entry in entries]
    for entry, document in planned:
        if document is not entry.document:
            session.serial += 1
            entry.document = replace(document, revision=session.serial)
            entry.versions.add(session.serial)
    session.document = replace(entries[-1].document, workspaces=session.document.workspaces)


def append_object(document: Document, item: Any) -> Document:
    if item.id in document.registry.records:
        return document
    if item.parent and item.parent not in document.registry.records:
        return document
    owners = tuple(owner for owner in item.owners if owner in document.index.entities)
    return replace(document, objects=(*document.objects, replace(item, owners=owners)))
