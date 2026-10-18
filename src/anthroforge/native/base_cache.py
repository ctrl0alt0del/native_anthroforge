"""Engine-owned bounded cache of immutable native construction bases."""

from collections import OrderedDict
from threading import Lock
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .mesh import Mesh


class BaseCache:
    def __init__(self, budget: int = 32 * 1024 * 1024, capacity: int = 64) -> None:
        self.budget, self.capacity, self.bytes = budget, capacity, 0
        self.items: OrderedDict[tuple[Any, ...], tuple[Mesh, int]] = OrderedDict()
        self.lock = Lock()
        self.observer: Any = None

    def get(self, key: tuple[Any, ...]) -> "Mesh | None":
        with self.lock:
            item = self.items.get(key)
            self.observe("hit" if item is not None else "miss", key)
            if item is not None:
                self.items.move_to_end(key)
                return item[0]
        return None

    def put(self, key: tuple[Any, ...], mesh: "Mesh") -> "Mesh":
        if mesh.counts[-1]:
            raise ValueError("Only immutable construction drafts belong in the base cache.")
        size = int(mesh.engine.library.af_mesh_storage_bytes(mesh.handle)) + 1024
        with self.lock:
            if key in self.items:
                self.observe("reuse", key)
                return self.items[key][0]
            self.admit(key, mesh, size)
        return mesh

    def admit(self, key: tuple[Any, ...], mesh: "Mesh", size: int) -> None:
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
                key=hex(hash(key)),
                bytes=size,
                reason=reason,
                retained_bytes=self.bytes,
                entries=len(self.items),
                budget=self.budget,
            )

    def retained(self) -> tuple["Mesh", ...]:
        with self.lock:
            return tuple(mesh for mesh, _ in self.items.values())
