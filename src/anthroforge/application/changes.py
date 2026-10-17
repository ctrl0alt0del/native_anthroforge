"""Bounded, client-independent change descriptions between immutable documents."""

from collections import deque
from dataclasses import dataclass, field, fields
from typing import Any

from anthroforge.core.document import Document


@dataclass
class DocumentChanges:
    reset: bool = False
    entities: dict[str, set[str]] = field(default_factory=dict)
    controls: dict[str, set[str]] = field(default_factory=dict)
    document: set[str] = field(default_factory=set)

    def include(self, other: "DocumentChanges") -> None:
        self.reset |= other.reset
        self.document.update(other.document)
        for name in ("entities", "controls"):
            target = getattr(self, name)
            for key, values in getattr(other, name).items():
                target.setdefault(key, set()).update(values)


def changed_fields(before: Any, after: Any) -> set[str]:
    if before is after:
        return set()
    if before is None or after is None:
        return {"@membership"}
    return {f.name for f in fields(after) if getattr(before, f.name) != getattr(after, f.name)}


def record_changes(before: tuple[Any, ...], after: tuple[Any, ...]) -> dict[str, set[str]]:
    if before is after:
        return {}
    old, new = {v.id: v for v in before}, {v.id: v for v in after}
    result = {key: changed_fields(old.get(key), new.get(key)) for key in old.keys() | new.keys()}
    return {key: value for key, value in result.items() if value}


class ChangeJournal:
    def __init__(self) -> None:
        self.serial = 0
        self.records: deque[tuple[int, DocumentChanges]] = deque(maxlen=64)

    def record(self, before: Document, after: Document) -> None:
        if before is after:
            return
        self.serial += 1
        names = ("name", "workspaces", "attachments_enabled", "update_mode")
        delta = DocumentChanges(
            before.id != after.id,
            record_changes(before.entities, after.entities),
            record_changes(before.controls, after.controls),
            {name for name in names if getattr(before, name) != getattr(after, name)},
        )
        record_order(delta, before, after)
        self.records.append((self.serial, delta))

    def since(self, cursor: int) -> DocumentChanges:
        result = DocumentChanges(reset=cursor < 0)
        if self.records and cursor < self.records[0][0] - 1:
            result.reset = True
        for serial, delta in self.records:
            if serial > cursor:
                result.include(delta)
        return result


def record_order(delta: DocumentChanges, before: Document, after: Document) -> None:
    for name in ("entities", "controls"):
        old, new = getattr(before, name), getattr(after, name)
        if old is not new and tuple(v.id for v in old) != tuple(v.id for v in new):
            delta.document.add(name + ".order")
