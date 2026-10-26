"""Immutable numeric payloads for skin references, collagen fields and fitted results."""

import hashlib
import json
import re
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

import numpy as np


@dataclass(frozen=True, eq=False)
class SkinAsset:
    arrays: Any
    metadata: bytes
    digest: str

    @property
    def bytes(self) -> int:
        return len(self.metadata) + sum(int(a.nbytes) for a in self.arrays.values())


def immutable(value: Any) -> Any:
    array = np.ascontiguousarray(value)
    if array.dtype.kind not in "biuf" or not np.isfinite(array).all():
        raise ValueError("Skin resources require finite numeric arrays.")
    return np.frombuffer(array.tobytes(), dtype=array.dtype).reshape(array.shape)


def create(arrays: dict[str, Any], metadata: dict[str, Any]) -> SkinAsset:
    if any(not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", key) for key in arrays):
        raise ValueError("Invalid skin buffer name.")
    owned = {key: immutable(value) for key, value in sorted(arrays.items())}
    encoded = json.dumps(metadata, sort_keys=True, allow_nan=False, separators=(",", ":")).encode()
    digest = hashlib.sha256(encoded)
    for name, array in owned.items():
        digest.update(json.dumps([name, array.dtype.str, array.shape]).encode())
        digest.update(array.tobytes())
    return SkinAsset(MappingProxyType(owned), encoded, digest.hexdigest())


def references(skin: Any) -> tuple[set[str], set[str]]:
    meshes = {skin.envelope.asset, skin.topology.asset, skin.final.asset}
    meshes.update(fit.reference for fit in skin.fits)
    buffers = {skin.reference, *(fit.data for fit in skin.fits)}
    buffers.update(stage.data for stage in (skin.envelope, skin.topology, skin.final))
    buffers.update(item.painted for item in skin.contributors)
    return meshes - {""}, buffers - {""}
