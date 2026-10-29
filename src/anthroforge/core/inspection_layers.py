"""Read-only scene layers retain resource owners, never authored scene identities."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Layer:
    identity: str
    resource: Any
    frame: tuple[float, ...]
    kind: str = "MESH"
    color: str = "#b87d72"
    lineage: Any = None
    side: str = "after"
    stage: str = "geometry"
    status: str = "current"
    reason: str = ""
    subject: str = ""
    category: str = "geometry"
