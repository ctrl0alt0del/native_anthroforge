"""Immutable resolved component buffers; native owners outlive borrowed arrays."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ComponentBuffer:
    local: Any
    world: Any
    frame: tuple[float, ...]
    common: tuple[tuple[str, Any], ...]
    references: tuple[tuple[tuple[str, Any], ...], ...] = ()
    owner: Any = None

    def reference(self, index: int) -> dict[str, Any]:
        result = dict(self.common)
        result.update(dict(self.references[index]) if self.references else {"index": index})
        return result


@dataclass(frozen=True)
class ComponentRead:
    signature: str
    buffers: tuple[ComponentBuffer, ...]
    provenance: tuple[tuple[str, Any], ...]
    reason: str = ""
    weight_binding: Any = None
    writers: tuple[tuple[Any, str], ...] = ()


def component_key(reference: dict[str, Any]) -> str:
    fields = (
        ("owner", "curve", "point", "part")
        if reference.get("point")
        else ("owner", "piece", "part", "index")
    )
    return ":".join(str(reference.get(key, "")) for key in fields)
