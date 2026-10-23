"""Material clipping consumes accepted base/output handles; interpolation stays native."""

from typing import Any

from .mesh import D, GeometryEngine, Mesh, U, doubles, pointer
from .tissue_shapes import owned


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_tissue_crop", [U, U, D, U], U)
    engine.bind("af_tissue_crop_retained", [U, U, U, D, U], U)


def evaluate(base: Mesh, output: Mesh, settings: Any, cancel: int = 0) -> Mesh:
    if not settings.enabled:
        return output
    plane = doubles((*settings.origin, *settings.normal, float(settings.positive)))
    handle = output.engine.library.af_tissue_crop(
        base.handle, output.handle, pointer(plane), cancel
    )
    return owned(output.engine, handle)


def retained(reference: Mesh, base: Mesh, output: Mesh, settings: Any, cancel: int = 0) -> Mesh:
    plane = doubles((*settings.origin, *settings.normal, float(settings.positive)))
    handle = output.engine.library.af_tissue_crop_retained(
        reference.handle, base.handle, output.handle, pointer(plane), cancel
    )
    return owned(output.engine, handle)
