"""Undo steps own revision membership; frozen historical snapshots never mutate."""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from anthroforge.core.document import Document


@dataclass
class Entry:
    document: Document
    versions: set[int] = field(default_factory=set)
    replay: Callable[[], Any] | None = None
    restarts: list[Callable[[], Any]] = field(default_factory=list)


class History:
    def __init__(self, document: Document) -> None:
        self.entries = [Entry(document, {document.revision})]
        self.cursor = 0
        self.before: Document | None = None
        self.versions: set[int] = set()

    def begin(self, document: Document) -> None:
        if self.before is not None:
            raise ValueError("An editing transaction is already active.")
        self.before, self.versions = document, set()

    def observe(self, document: Document) -> None:
        if self.before is not None:
            self.versions.add(document.revision)
        else:
            self.entries[self.cursor].document = document
            self.entries[self.cursor].versions.add(document.revision)

    def commit(self, document: Document, replay: Callable[[], Any] | None = None) -> None:
        if self.before is None:
            raise ValueError("No editing transaction is active.")
        if document != self.before:
            self.entries = self.entries[: self.cursor + 1]
            self.entries.append(Entry(document, self.versions | {document.revision}, replay))
            self.cursor += 1
        self.before, self.versions = None, set()

    def cancel(self) -> Document:
        if self.before is None:
            raise ValueError("No editing transaction is active.")
        document = self.before
        self.before, self.versions = None, set()
        return document

    def navigate(self, direction: int) -> Document:
        if self.before is not None:
            raise ValueError("Finish the current edit before navigating history.")
        target = self.cursor + direction
        if target < 0 or target >= len(self.entries):
            raise ValueError("No further history in that direction.")
        self.cursor = target
        return self.entries[target].document

    def surviving(self) -> set[int]:
        versions = set().union(*(e.versions for e in self.entries[: self.cursor + 1]))
        return versions | self.versions

    def replay(self) -> None:
        entry = self.entries[self.cursor]
        callback = entry.replay
        if callback is not None:
            callback()
        callbacks, entry.restarts = entry.restarts, []
        for restart in callbacks:
            restart()
