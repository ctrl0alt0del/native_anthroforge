"""Authored deformation support intent, independent of accepted fields and obstacles."""

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
