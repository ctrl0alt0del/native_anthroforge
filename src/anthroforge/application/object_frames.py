"""Resolve ordinary transform relationships across object types with one cycle guard."""

from typing import Any

from anthroforge.core.entities import IDENTITY, SCP
from anthroforge.native.construction import matrix


class Frames:
    def __init__(self, engine: Any, document: Any) -> None:
        self.engine, self.document = engine, document
        self.frames: dict[str, tuple[float, ...]] = {"": IDENTITY}
        self.visiting: set[str] = set()

    def world(self, key: str) -> tuple[float, ...]:
        if key in self.frames:
            return self.frames[key]
        if key in self.visiting:
            raise ValueError("Cyclic ordinary transform dependency.")
        self.visiting.add(key)
        try:
            frame = self.resolve(self.document.object(key))
            self.frames[key] = frame
            return frame
        finally:
            self.visiting.remove(key)

    def resolve(self, item: Any) -> tuple[float, ...]:
        if isinstance(item, SCP):
            return item.matrix
        parent = getattr(item, "parent", "") or getattr(item, "follow", "")
        return matrix(self.engine, self.world(parent), item.matrix)
