"""Batched dense-node attachments; editable controls accompany the authoritative path."""

import ctypes as c
from dataclasses import dataclass, replace
from typing import Any

import numpy as np

from . import paths, point_attachments
from .mesh import D, GeometryEngine, U, doubles, pointer
from .point_attachments import HANDLES, INT


def configure(engine: GeometryEngine) -> None:
    prefix = [c.c_int, HANDLES, D]
    engine.bind(
        "af_curve_attachment_capture",
        [*prefix, U, D, c.c_int, D, INT, INT, c.c_int, D, INT, D, D, U],
    )
    engine.bind("af_blended_attachment_resolve", [*prefix, c.c_int, INT, D, D, D, U])
    engine.bind("af_attached_path", [U, D, D, U], U)
    engine.bind("af_attached_controls", [D, c.c_int, D, D, D])
    engine.bind("af_attachment_compact", [c.c_int, INT, c.c_int, INT, INT])


@dataclass(frozen=True, eq=False)
class Field:
    owners: Any
    weights: Any
    bindings: Any
    records: Any
    path: paths.Path

    def __post_init__(self) -> None:
        validate_arrays(self)
        count = self.path.count + len(self.records) * 3
        if self.owners.shape != (count, 2) or self.weights.shape != (count, 2):
            raise ValueError("Attachment field must cover path samples and editable controls.")
        if self.bindings.shape != (count, 2, 28) or self.records.shape[1:] != (13,):
            raise ValueError("Invalid attachment field record layout.")
        for data in (self.owners, self.weights, self.bindings, self.records):
            data.flags.writeable = False

    @property
    def bytes(self) -> int:
        return sum(
            array.nbytes for array in (self.owners, self.weights, self.bindings, self.records)
        )


@dataclass(frozen=True)
class Capture:
    path: paths.Path
    records: Any
    world: Any
    pins: Any
    parents: Any
    retained: Any = None


def validate_arrays(field: Field) -> None:
    for name, dtype in (
        ("owners", np.int32),
        ("weights", np.float64),
        ("bindings", np.float64),
        ("records", np.float64),
    ):
        array = getattr(field, name)
        if array.dtype != dtype or not array.flags.c_contiguous or not np.isfinite(array).all():
            raise ValueError("Attachment buffers require finite, contiguous typed data.")


def compact(field: Field, surfaces: int) -> tuple[Field, Any]:
    output, used = np.empty_like(field.owners), np.empty(surfaces, dtype=np.int32)
    args = (
        field.owners.size,
        field.owners.ctypes.data_as(INT),
        surfaces,
        output.ctypes.data_as(INT),
        used.ctypes.data_as(INT),
    )
    count = field.path.engine.library.af_attachment_compact(*args)
    field.path.engine.check(count < 0)
    return replace(field, owners=output), used[:count]


def capture(engine: GeometryEngine, surfaces: Any, spec: Capture, cancel: int = 0) -> Field:
    records, world = doubles(spec.records), doubles(spec.world)
    pins, parents = capture_pins(spec)
    count = spec.path.count + len(records) * 3
    owners = np.empty((count, 2), dtype=np.int32)
    weights, bindings = np.empty((count, 2)), np.empty((count, 2, 28))
    arguments = capture_arguments(spec, records, world, pins, parents)
    output = (owners.ctypes.data_as(INT), pointer(weights), pointer(bindings))
    engine.check(
        engine.library.af_curve_attachment_capture(*prefix(surfaces), *arguments, *output, cancel)
    )
    return Field(owners, weights, bindings, records.copy(), spec.path)


def capture_arguments(spec: Capture, records: Any, world: Any, pins: Any, parents: Any) -> Any:
    return (
        spec.path.handle,
        pointer(records),
        len(records),
        pointer(world),
        pins.ctypes.data_as(INT),
        parents.ctypes.data_as(INT),
        len(pins),
        retained_bindings(spec, len(pins)),
    )


def retained_bindings(spec: Capture, count: int) -> Any:
    if spec.retained is None:
        return None
    records = doubles(spec.retained)
    if records.shape != (count, 28) or not np.isfinite(records).all():
        raise ValueError("Retained fiber anchors require finite attachment records.")
    return pointer(records)


def capture_pins(spec: Capture) -> tuple[Any, Any]:
    pins = np.ascontiguousarray(spec.pins, dtype=np.int32)
    parents = np.ascontiguousarray(spec.parents, dtype=np.int32)
    if pins.ndim != 1 or pins.shape != parents.shape:
        raise ValueError("Fiber anchors need corresponding authored points and parent surfaces.")
    return pins, parents


def prefix(surfaces: Any) -> tuple[Any, ...]:
    handles, frames = point_attachments.surface_arrays(*surfaces)
    return len(handles), handles.ctypes.data_as(HANDLES), pointer(frames)


def resolved_points(engine: GeometryEngine, surfaces: Any, field: Field, cancel: int) -> Any:
    positions = np.empty((len(field.owners), 3))
    inputs = (field.owners.ctypes.data_as(INT), pointer(field.weights), pointer(field.bindings))
    engine.check(
        engine.library.af_blended_attachment_resolve(
            *prefix(surfaces), len(positions), *inputs, pointer(positions), cancel
        )
    )
    return positions


def resolve(
    engine: GeometryEngine, surfaces: Any, field: Field, world: Any, cancel: int = 0
) -> tuple[paths.Path, Any]:
    positions, frame = resolved_points(engine, surfaces, field, cancel), doubles(world)
    handle = engine.library.af_attached_path(
        field.path.handle, pointer(positions), pointer(frame), cancel
    )
    return paths.Path(engine, handle), resolved_controls(engine, field, positions, frame)


def resolved_controls(engine: GeometryEngine, field: Field, positions: Any, world: Any) -> Any:
    controls, output = doubles(positions[field.path.count :]), np.empty_like(field.records)
    inputs = (
        pointer(field.records),
        len(output),
        pointer(controls),
        pointer(world),
        pointer(output),
    )
    engine.check(engine.library.af_attached_controls(*inputs))
    return output
