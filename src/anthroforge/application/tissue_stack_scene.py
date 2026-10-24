"""Owned material participants prepared in worker work, never in a pointer-move handler."""

from hashlib import blake2b
from typing import Any

from anthroforge.core.anatomical_surfaces import usable
from anthroforge.core.mirroring import source as source_identity
from anthroforge.core.tissues import TissueVCP
from anthroforge.native import stacking_abi
from anthroforge.native.resource_cache import ResourceCache
from anthroforge.native.scene import entity_frame
from anthroforge.native.tissue_stacking import MaterialLease

from . import mirror_stacking


def participants(document: Any) -> tuple[TissueVCP, ...]:
    return tuple(
        item
        for item in document.objects
        if isinstance(item, TissueVCP)
        and item.stacking
        and item.intrinsic_material is not None
        and item.intrinsic_material.base_state.kind == "SURFACE"
    )


def identity(key: str, side: str) -> int:
    return (
        int.from_bytes(blake2b((key + ":" + side).encode(), digest_size=8).digest(), "little") or 1
    )


def sides(state: Any) -> tuple[str, ...]:
    return ("a", "b") if state.both_sides else ("a",)


def families(document: Any) -> list[tuple[TissueVCP, int]]:
    labels: dict[tuple[bool, str], int] = {}
    return [
        (item, labels.setdefault((bool(item.group), item.group or item.id), len(labels) + 1))
        for item in participants(document)
    ]


def lease(resources: Any, state: Any, side: str, cancel: int, final: bool = False) -> MaterialLease:
    keys = (state.base, state.rest, state.final if final else state.own)
    meshes = [resources.meshes[key].mesh for key in keys]
    cache: ResourceCache[MaterialLease] = meshes[0].engine.tissue_materials
    key = state, side, final
    cached = cache.get(key)
    if cached is not None:
        return cached
    value = MaterialLease(
        meshes[0], meshes[1], meshes[2], state, frame=state.frame, side=side, cancel=cancel
    )
    metadata_bytes = sum(len(f.values) for f in state.fields) * 8 + 4096
    return cache.store(key, value, value.retained_bytes + metadata_bytes)


class StackScene:
    def __init__(self, document: Any, resources: Any, target: str, cancel: int) -> None:
        self.document, self.resources, self.target, self.cancel = (
            document,
            resources,
            target,
            cancel,
        )
        self.leases: dict[tuple[str, str], MaterialLease] = {}
        self.domains: dict[int, Any] = {}
        self.identities: dict[int, tuple[str, str]] = {}
        self.failures: dict[str, str] = {}
        for item, family in families(document):
            self.add(item, family)
        mirror_stacking.add(self, families(document))

    def add(self, item: TissueVCP, family: int) -> None:
        state = item.intrinsic_material
        assert state is not None
        try:
            if not usable(item.intrinsic_result):
                raise ValueError(item.intrinsic_result.error or "Intrinsic evaluation failed.")
            for side in sides(state):
                self.add_side(item.id, state, side, family)
        except ValueError as error:
            self.failures[item.id] = str(error)
            self.discard(item.id)

    def add_side(self, owner: str, state: Any, side: str, family: int) -> None:
        value = lease(self.resources, state, side, self.cancel, owner.startswith("mirror/"))
        key = identity(owner, side)
        if key in self.identities:
            raise ValueError("Stacking side identity collision.")
        self.leases[owner, side] = value
        allowance = self.document.object(source_identity(owner)).stack_settings.displacement
        domain = value.domain(key, family=family, allowance=allowance)
        if domain.triangles:
            self.identities[key], self.domains[key] = (owner, side), domain

    def discard(self, target: str) -> None:
        for key, label in tuple(self.identities.items()):
            if label[0] == target:
                del self.identities[key], self.domains[key]
        for label in tuple(self.leases):
            if label[0] == target:
                del self.leases[label]


def obstacles(engine: Any, document: Any, resources: Any) -> tuple[list[Any], list[Any]]:
    from anthroforge.core.results import geometry_asset

    rows, buffers = [], []
    for item in document.entities:
        asset = resources.meshes.get(geometry_asset(item))
        if asset is None or not asset.mesh.counts[3]:
            continue
        row, owned = obstacle(engine, item, asset.mesh)
        rows.append(row)
        buffers.extend(owned)
    return rows, buffers


def obstacle(engine: Any, item: Any, mesh: Any) -> tuple[Any, Any]:
    row = stacking_abi.Obstacle(mesh=mesh.handle)
    row.frame[:] = entity_frame(engine, item)
    return row, (mesh,)
