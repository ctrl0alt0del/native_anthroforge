"""Immutable mesh assets with independent import provenance."""

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from hashlib import file_digest
from pathlib import Path

from anthroforge.native.mesh import GeometryEngine, Mesh, NativeCancellation


@dataclass(frozen=True)
class Asset:
    mesh: Mesh
    source: str
    digest: str
    units: float
    y_up: bool

    def __post_init__(self) -> None:
        if not self.mesh.prepared:
            raise ValueError("An asset requires finalized spatial and render geometry.")


class MeshAssetView(Mapping[str, Asset]):
    """Adapt a worker's owned mesh snapshot without wrapping unrelated resources."""

    def __init__(self, meshes: Mapping[str, Mesh]) -> None:
        self.meshes = meshes

    def __getitem__(self, key: str) -> Asset:
        return Asset(self.meshes[key], "generated", "", 1.0, False)

    def __iter__(self) -> Iterator[str]:
        return iter(self.meshes)

    def __len__(self) -> int:
        return len(self.meshes)

    def __contains__(self, key: object) -> bool:
        return key in self.meshes


def imported(
    engine: GeometryEngine, path: Path, units: float, y_up: bool, cancel: NativeCancellation
) -> Asset:
    with path.open("rb") as source:
        digest = file_digest(source, "sha256").hexdigest()
    if cancel.is_set():
        raise ValueError("Import cancelled.")
    mesh = engine.import_mesh(path, units, y_up, cancel.handle)
    return Asset(mesh, path.name, digest, units, y_up)
