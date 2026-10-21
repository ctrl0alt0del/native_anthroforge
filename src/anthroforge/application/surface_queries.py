"""Query preparation uses the base belonging to accepted output, including Manual results."""

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

from anthroforge.native import surface_queries as native
from anthroforge.native.surface_queries import Mode as Mode

from . import surface_providers


@dataclass(frozen=True)
class Inputs:
    queries: tuple[native.Query, ...]
    frames: tuple[tuple[float, ...], ...]

    def __iter__(self) -> Iterator[Any]:
        yield [q.mesh.handle for q in self.queries]
        yield self.frames


def base(document: Any, meshes: Any, provider: Any) -> Any:
    if provider.reference.role != "TISSUE_FINAL":
        return None
    material = document.object(provider.reference.target).final_material
    if material is None or material.final != provider.asset_id:
        raise ValueError("Confirmed tissue placement needs accepted final material provenance.")
    if material.base_state.kind != "SURFACE" or not material.base:
        return None
    if material.base not in meshes:
        raise ValueError("Confirmed tissue placement is missing its retained material base.")
    return meshes[material.base].mesh


def prepare(
    document: Any, meshes: Any, provider: Any, mode: native.Mode, cancel: int
) -> native.Query:
    backing = base(document, meshes, provider) if mode == native.Mode.CONFIRMED else None
    return native.prepare(provider.resource.mesh, backing, mode, cancel)


def inputs(
    engine: Any,
    document: Any,
    meshes: Any,
    targets: Any,
    cancel: int,
    mode: native.Mode = native.Mode.CONFIRMED,
) -> Inputs:
    providers = [surface_providers.get(engine, document, meshes, ref) for ref in targets]
    queries = tuple(prepare(document, meshes, p, mode, cancel) for p in providers)
    return Inputs(queries, tuple(p.frame for p in providers))
