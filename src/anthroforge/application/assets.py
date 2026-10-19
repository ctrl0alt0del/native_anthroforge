"""Immutable mesh assets with independent import provenance."""

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


def imported(
    engine: GeometryEngine, path: Path, units: float, y_up: bool, cancel: NativeCancellation
) -> Asset:
    with path.open("rb") as source:
        digest = file_digest(source, "sha256").hexdigest()
    if cancel.is_set():
        raise ValueError("Import cancelled.")
    mesh = engine.import_mesh(path, units, y_up, cancel.handle)
    return Asset(mesh, path.name, digest, units, y_up)
