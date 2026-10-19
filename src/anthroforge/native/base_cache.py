"""Engine-owned bounded cache of immutable native construction bases."""

from typing import TYPE_CHECKING, Any

from .resource_cache import ResourceCache

if TYPE_CHECKING:
    from .mesh import Mesh


class BaseCache(ResourceCache["Mesh"]):
    def __init__(self, budget: int = 32 * 1024 * 1024, capacity: int = 64) -> None:
        super().__init__(budget, capacity, "body_base")

    def put(self, key: tuple[Any, ...], mesh: "Mesh") -> "Mesh":
        if mesh.counts[-1]:
            raise ValueError("Only immutable construction drafts belong in the base cache.")
        size = int(mesh.engine.library.af_mesh_storage_bytes(mesh.handle)) + 1024
        return self.store(key, mesh, size)
