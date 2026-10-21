"""Owned, batched nearest-surface deformation with native spatial queries."""

import ctypes as c
from typing import Any

from anthroforge.core.shrinkwrap import MODES

from .construction import matrix
from .influence import weights
from .mesh import D, GeometryEngine, U, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_shrinkwrap", [D, c.c_int, U, D, c.c_double, c.c_int, c.c_double, D, U])


def deform(
    engine: GeometryEngine, points: Any, binding: Any, owner: Any, target: Any, cancel: int
) -> Any:
    data = doubles(points).copy()
    relative = doubles(matrix(engine, target.frame, owner, relative=True))
    influence = weights(engine, binding, len(data), cancel)
    target_args = (target.resource.mesh.handle, pointer(relative), *parameters(binding))
    arguments = (pointer(data), len(data), *target_args, influence, cancel)
    engine.check(engine.library.af_shrinkwrap(*arguments))
    return data


def parameters(binding: Any) -> tuple[float, int, float]:
    settings = binding.shrinkwrap
    return settings.offset, MODES.index(settings.mode), binding.strength
