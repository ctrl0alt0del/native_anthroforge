"""Bounded, client-independent change descriptions between immutable documents."""

from collections import deque
from collections.abc import Mapping
from dataclasses import dataclass, field, fields
from typing import Any

from anthroforge.core.document import Document

DOCUMENT_FIELDS = (
    "name",
    "workspaces",
    "attachments_enabled",
    "update_mode",
    "junctions",
    "shortcuts",
    "driving_shortcuts",
    "formula_results",
    "mirror_rules",
    "shared_mirror_targets",
)


@dataclass
class DocumentChanges:
    reset: bool = False
    entities: dict[str, set[str]] = field(default_factory=dict)
    controls: dict[str, set[str]] = field(default_factory=dict)
    document: set[str] = field(default_factory=set)
    objects: dict[str, set[str]] = field(default_factory=dict)

    def include(self, other: "DocumentChanges") -> None:
        self.reset |= other.reset
        self.document.update(other.document)
        for name in ("entities", "controls", "objects"):
            target = getattr(self, name)
            for key, values in getattr(other, name).items():
                target.setdefault(key, set()).update(values)


def changed_fields(before: Any, after: Any) -> set[str]:
    if before is after:
        return set()
    if before is None or after is None:
        return {"@membership"}
    if type(before) is not type(after):
        return {"@membership"}
    return {f.name for f in fields(after) if getattr(before, f.name) != getattr(after, f.name)}


def record_changes(before: Mapping[str, Any], after: Mapping[str, Any]) -> dict[str, set[str]]:
    if before is after:
        return {}
    result = {
        key: changed_fields(before.get(key), after.get(key)) for key in before.keys() | after.keys()
    }
    return {key: value for key, value in result.items() if value}


class ChangeJournal:
    def __init__(self) -> None:
        self.serial = 0
        self.records: deque[tuple[int, DocumentChanges]] = deque(maxlen=64)

    def record(self, before: Document, after: Document) -> None:
        if before is after:
            return
        self.serial += 1
        delta = DocumentChanges(
            before.id != after.id,
            record_changes(before.index.entities, after.index.entities),
            record_changes(before.index.controls, after.index.controls),
            {name for name in DOCUMENT_FIELDS if getattr(before, name) != getattr(after, name)},
            record_changes(before.registry.authored, after.registry.authored),
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
    if before.index.structure is after.index.structure and before.objects is after.objects:
        return
    for name in ("entities", "controls", "objects"):
        old, new = getattr(before, name), getattr(after, name)
        if old is not new and tuple(v.id for v in old) != tuple(v.id for v in new):
            delta.document.add(name + ".order")
