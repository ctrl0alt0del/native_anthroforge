"""Owned material participants prepared in worker work, never in a pointer-move handler."""

from hashlib import blake2b
from typing import Any

import numpy as np

from anthroforge.core.tissues import TissueVCP
from anthroforge.native import components, stacking_abi
from anthroforge.native.mesh import INT64, pointer
from anthroforge.native.scene import entity_frame
from anthroforge.native.tissue_stacking import MaterialLease


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


def lease(resources: Any, state: Any, side: str, cancel: int, final: bool = False) -> MaterialLease:
    keys = (state.base, state.rest, state.final if final else state.own)
    meshes = [resources.meshes[key].mesh for key in keys]
    return MaterialLease(
        meshes[0], meshes[1], meshes[2], state, frame=state.frame, side=side, cancel=cancel
    )


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
        for family, item in enumerate(participants(document), 1):
            self.add(item, family)

    def add(self, item: TissueVCP, family: int) -> None:
        state = item.intrinsic_material
        assert state is not None
        try:
            if item.intrinsic_result.status in ("failed", "invalid", "cancelled"):
                raise ValueError(item.intrinsic_result.error or "Intrinsic evaluation failed.")
            for side in sides(state):
                self.add_side(item.id, state, side, family)
        except ValueError as error:
            self.failures[item.id] = str(error)
            self.discard(item.id)

    def add_side(self, owner: str, state: Any, side: str, family: int) -> None:
        value = lease(self.resources, state, side, self.cancel)
        key = identity(owner, side)
        if key in self.identities:
            raise ValueError("Stacking side identity collision.")
        self.leases[owner, side] = value
        domain = value.domain(key, family=family)
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
    vertices = components.transformed(engine, mesh.array(0), entity_frame(engine, item))
    faces = np.ascontiguousarray(mesh.array(3), dtype=np.int64)
    row = stacking_abi.Obstacle(
        pointer(vertices), faces.ctypes.data_as(INT64), len(vertices), len(faces)
    )
    return row, (vertices, faces)
