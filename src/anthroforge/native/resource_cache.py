"""Engine-owned bounded LRU storage of immutable native resources."""

from collections import OrderedDict
from threading import Lock
from typing import Any


class ResourceCache[T]:
    def __init__(self, budget: int, capacity: int, name: str) -> None:
        self.budget, self.capacity, self.bytes, self.name = budget, capacity, 0, name
        self.items: OrderedDict[tuple[Any, ...], tuple[T, int]] = OrderedDict()
        self.lock = Lock()
        self.observer: Any = None

    def get(self, key: tuple[Any, ...]) -> T | None:
        with self.lock:
            item = self.items.get(key)
            self.observe("hit" if item is not None else "miss", key)
            if item is not None:
                self.items.move_to_end(key)
                return item[0]
        return None

    def store(self, key: tuple[Any, ...], mesh: T, size: int) -> T:
        with self.lock:
            if key in self.items:
                self.observe("reuse", key)
                return self.items[key][0]
            self.admit(key, mesh, size)
        return mesh

    def admit(self, key: tuple[Any, ...], mesh: T, size: int) -> None:
        if size > self.budget:
            self.observe("bypass", key, size, "entry_exceeds_budget")
            return
        self.items[key] = (mesh, size)
        self.bytes += size
        self.observe("insert", key, size)
        self.trim()

    def trim(self) -> None:
        while self.bytes > self.budget or len(self.items) > self.capacity:
            reason = "byte_budget" if self.bytes > self.budget else "entry_capacity"
            key, (_, size) = self.items.popitem(last=False)
            self.bytes -= size
            self.observe("evict", key, size, reason)

    def clear(self) -> None:
        with self.lock:
            size = self.bytes
            self.items.clear()
            self.bytes = 0
            self.observe("clear", (), size, "lifecycle")

    def observe(self, action: str, key: tuple[Any, ...], size: int = 0, reason: str = "") -> None:
        if self.observer is not None:
            self.observer(
                action,
                cache=self.name,
                key=hex(hash(key)),
                bytes=size,
                reason=reason,
                retained_bytes=self.bytes,
                entries=len(self.items),
                budget=self.budget,
            )

    def retained(self) -> tuple[T, ...]:
        with self.lock:
            return tuple(mesh for mesh, _ in self.items.values())
