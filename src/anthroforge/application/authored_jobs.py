"""Async authored publication belongs to its initiating undo step, across later edits."""

from collections.abc import Callable
from dataclasses import dataclass, replace
from functools import partial
from typing import TYPE_CHECKING, Any

from anthroforge.core.document import Document
from anthroforge.core.results import EvaluationResult, ReadRevision

from .evaluation_results import matches
from .history import Entry

if TYPE_CHECKING:
    from .session import Session


@dataclass(frozen=True)
class Capture:
    reads: tuple[ReadRevision, ...]
    restart: Callable[[], Any]

    def matches(self, document: Document) -> bool:
        return matches(document, EvaluationResult(inputs=self.reads))


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


def publish(
    session: "Session",
    origin: int,
    merge: Callable[[Document], Document],
    capture: Capture | None = None,
) -> None:
    entries = affected(session, origin)
    planned = [(entry, planned_merge(entry.document, merge, capture)) for entry in entries]
    for entry, (document, ready) in planned:
        capture_state(entry, origin, capture, ready)
        if document is not entry.document:
            session.serial += 1
            entry.document = replace(document, revision=session.serial)
            entry.versions.add(session.serial)
    session.document = replace(entries[-1].document, workspaces=session.document.workspaces)


def planned_merge(document: Document, merge: Any, capture: Capture | None) -> tuple[Document, bool]:
    ready = capture is None or capture.matches(document)
    return (merge(document) if ready else document), ready


def capture_state(entry: Entry, origin: int, capture: Capture | None, ready: bool) -> None:
    if capture is None:
        return
    if origin in entry.versions:
        entry.replay = None
    if ready:
        entry.pending_authored.pop(origin, None)
    else:
        entry.pending_authored[origin] = capture.restart


def append_object(document: Document, item: Any) -> Document:
    if item.id in document.registry.records:
        return document
    if item.parent and item.parent not in document.registry.records:
        return document
    owners = tuple(owner for owner in item.owners if owner in document.registry.anatomy)
    return replace(document, objects=(*document.objects, replace(item, owners=owners)))
