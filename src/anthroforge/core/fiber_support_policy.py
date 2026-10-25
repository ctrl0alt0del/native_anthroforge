"""Authored deformation support intent, independent of accepted fields and obstacles."""

from collections.abc import Iterable
from dataclasses import dataclass

from .surface_references import SurfaceReference


@dataclass(frozen=True, slots=True)
class FiberSupportPolicy:
    automatic: bool = True
    included: tuple[SurfaceReference, ...] = ()
    excluded: tuple[SurfaceReference, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.automatic, bool):
            raise ValueError("Automatic deformation supports must be a Boolean.")
        for values in (self.included, self.excluded):
            if len(set(values)) != len(values):
                raise ValueError("Deformation support overrides must be unique.")
        if set(self.included) & set(self.excluded):
            raise ValueError("A deformation support cannot be included and excluded.")


def deformation_targets(
    candidates: Iterable[SurfaceReference], parents: Iterable[SurfaceReference]
) -> tuple[SurfaceReference, ...]:
    explicit = set(parents)
    if any(ref.role != "SCP_GEOMETRY" for ref in explicit):
        return tuple(sorted(explicit))
    return tuple(sorted(explicit | {ref for ref in candidates if ref.role == "SCP_GEOMETRY"}))


def selected_targets(
    candidates: Iterable[SurfaceReference],
    parents: Iterable[SurfaceReference],
    policy: FiberSupportPolicy,
) -> tuple[SurfaceReference, ...]:
    parents = set(parents)
    automatic = set(deformation_targets(candidates, parents)) if policy.automatic else parents
    return tuple(sorted((automatic | set(policy.included)) - set(policy.excluded) | parents))
