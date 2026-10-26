"""Common remesher output; usable-result warnings remain distinct from failures."""

from dataclasses import dataclass
from typing import Any

from anthroforge.native.mesh import Mesh


@dataclass(frozen=True)
class Result:
    mesh: Mesh
    warnings: tuple[str, ...]
    statistics: dict[str, Any]
