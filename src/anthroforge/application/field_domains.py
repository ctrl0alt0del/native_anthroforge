"""Shared material-field identity, stable across position-only mesh changes."""

from hashlib import sha256
from struct import pack
from typing import Any

from anthroforge.native import material


def mesh_domain(mesh: Any) -> tuple[int, str]:
    digest = sha256(pack("<q", mesh.counts[0]))
    for kind in (1, 2):
        digest.update(memoryview(mesh.array(kind)))
    digest.update(memoryview(material.axes(mesh)))
    return mesh.counts[0], digest.hexdigest()
