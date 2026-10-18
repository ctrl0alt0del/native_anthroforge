"""Branch topology is declared by source curves and explicit junction identities."""

from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class SurfaceBranch:
    boundary: str
    curves: tuple[str, ...]
    junctions: tuple[str, ...]
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if not self.boundary or not self.id or len(self.curves) < 2:
            raise ValueError(
                "A branch requires an outer main curve and at least two source curves."
            )
        if len(self.junctions) != len(self.curves) or len(set(self.junctions)) != len(
            self.junctions
        ):
            raise ValueError("Each branch curve requires a distinct explicit junction.")


def validate(item: Any) -> None:
    if item.kind != "BRANCHED":
        if item.main or item.branches:
            raise ValueError("Only branched surfaces have main/branch source groups.")
        return
    if len(item.main) < 2 or not item.branches or item.close_across:
        raise ValueError("Branched surfaces require an open main loft and explicit branches.")
    keys = (*item.main, *(key for b in item.branches for key in b.curves))
    if len(keys) != len(set(keys)) or set(keys) != {u.curve for u in item.curves}:
        raise ValueError("Main and branch groups must partition the surface sources.")
    if len({b.id for b in item.branches}) != len(item.branches):
        raise ValueError("Branch identities must be unique.")
    if any(b.boundary not in (item.main[0], item.main[-1]) for b in item.branches):
        raise ValueError("Branches connect only to outer main curves.")


def root_points(boundary: Any, curves: list[Any], junctions: tuple[str, ...]) -> list[int]:
    indices = {p.junction: i for i, p in enumerate(boundary.points) if p.junction}
    roots = []
    for curve, key in zip(curves, junctions, strict=True):
        index = indices.get(key, -1)
        if not 0 < index < len(boundary.points) - 1:
            raise ValueError("Branch roots require explicit junctions on interior main points.")
        if key not in (curve.points[0].junction, curve.points[-1].junction):
            raise ValueError("A branch endpoint must share its main root's junction identity.")
        roots.append(index)
    return roots


def validate_sources(item: Any, records: Any) -> None:
    occupied: dict[str, list[tuple[int, int]]] = {}
    uses = {u.curve: u for u in item.curves}
    for branch in item.branches:
        roots = root_points(
            records[branch.boundary], [records[k] for k in branch.curves], branch.junctions
        )
        ordered = list(reversed(roots)) if uses[branch.boundary].reverse else roots
        if ordered != sorted(set(ordered)):
            raise ValueError("Branch roots must follow the consumed main curve order.")
        first, last = min(roots), max(roots)
        if any(first <= b and last >= a for a, b in occupied.get(branch.boundary, ())):
            raise ValueError("Branch intervals cannot overlap or share endpoints.")
        occupied.setdefault(branch.boundary, []).append((first, last))
