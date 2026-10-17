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

    def get(self, key: tuple[Any, ...]) -> "Mesh | None":
        with self.lock:
            item = self.items.get(key)
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
                return self.items[key][0]
            if size <= self.budget:
                self.items[key] = (mesh, size)
                self.bytes += size
                self.trim()
        return mesh

    def trim(self) -> None:
        while self.bytes > self.budget or len(self.items) > self.capacity:
            _, (_, size) = self.items.popitem(last=False)
            self.bytes -= size

    def clear(self) -> None:
        with self.lock:
            self.items.clear()
            self.bytes = 0
