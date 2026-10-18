"""Explicit point sharing; the designated member supplies accepted position and binding."""

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from .results import Port


@dataclass(frozen=True, slots=True)
class PointRef:
    curve: str
    point: str

    def __post_init__(self) -> None:
        if not self.curve or not self.point:
            raise ValueError("A junction member requires a curve and authored point identity.")


@dataclass(frozen=True, slots=True)
class Junction:
    source: PointRef
    id: str = field(default_factory=lambda: str(uuid4()))


def port(item: Junction) -> Port:
    return Port(item.source.curve, "junction:" + item.id)


def members(objects: tuple[Any, ...]) -> dict[str, tuple[PointRef, ...]]:
    from .construction import Curve

    found: dict[str, list[PointRef]] = {}
    for item in objects:
        if isinstance(item, Curve):
            for point in item.points:
                if point.junction:
                    found.setdefault(point.junction, []).append(PointRef(item.id, point.id))
    return {key: tuple(values) for key, values in found.items()}


def validate(records: tuple[Junction, ...], objects: tuple[Any, ...]) -> None:
    links, lookup = members(objects), {j.id: j for j in records}
    if len(lookup) != len(records) or any(not key for key in lookup):
        raise ValueError("Junction identities must be nonempty and unique.")
    if links.keys() != lookup.keys():
        raise ValueError("Every junction and point membership must resolve explicitly.")
    for key, points in links.items():
        if len(points) < 2 or lookup[key].source not in points:
            raise ValueError("A junction needs its source and at least one other member.")
        if len({p.curve for p in points}) != len(points):
            raise ValueError("A curve cannot visit the same junction twice.")


def inputs(item: Any, records: tuple[Junction, ...]) -> set[Port]:
    lookup = {j.id: j for j in records}
    shared = {
        port(lookup[p.junction])
        for p in item.points
        if p.junction in lookup and lookup[p.junction].source != PointRef(item.id, p.id)
    }
    return shared | ({Port(item.id, "pose")} if shared else set())


def edges(records: tuple[Junction, ...]) -> dict[Port, set[Port]]:
    return {port(j): {Port(j.source.curve, "path"), Port(j.source.curve, "pose")} for j in records}


def decode(value: dict[str, Any]) -> Junction:
    return Junction(PointRef(**value["source"]), value["id"])
