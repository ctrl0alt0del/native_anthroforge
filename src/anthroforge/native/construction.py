"""Batched construction/deformation adapters. Geometry computation remains native."""

import ctypes as c
from typing import Any

import numpy as np

from anthroforge.core.construction import Control, Curve, Deformer, Primitive, Thickness, cyclic
from anthroforge.core.entities import IDENTITY

from .falloff import table as falloff_table
from .mesh import D, GeometryEngine, Mesh, U, doubles, pointer

INT = c.c_int
F = c.c_double
IP = c.POINTER(INT)
HANDLES = ("AUTO", "ALIGNED", "FREE", "VECTOR")
INTERPOLATION = ("LINEAR", "CARDINAL", "CATMULL_ROM", "BSPLINE")
FALLOFF = (
    "NONE",
    "CURVE",
    "SMOOTH",
    "SPHERE",
    "ROOT",
    "SHARP",
    "LINEAR",
    "CONSTANT",
    "INVERSE_SQUARE",
)


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_curve_handles", [D, INT, INT])
    engine.bind("af_curve_sample", [D, INT, INT, INT, INT, F, F, D, D, U])
    engine.bind("af_loft", [D, INT, INT, INT, INT, INT, U], U)
    engine.bind("af_loft_geometry", [D, INT, INT, INT, INT, INT, U], U)
    engine.bind("af_mesh_deformed", [U, D, c.c_int64, U], U)
    engine.bind("af_mesh_join", [c.POINTER(U), INT, U], U)
    engine.bind("af_matrix_relative", [D, D, D])
    engine.bind("af_matrix_product", [D, D, D])
    engine.bind("af_hook", [D, INT, D, D, D, F, F, INT, D, D, INT, U])
    engine.bind("af_lattice_grid", [IP, D])
    engine.bind("af_lattice_resolution", [IP])
    engine.bind("af_lattice", [D, INT, D, IP, IP, D, F, D, D, U])
    engine.bind("af_lattice_outside", [D, IP])
    engine.bind("af_solidify", [U, D, D, U], U)


def matrix(engine: GeometryEngine, a: Any, b: Any, relative: bool = False) -> tuple[float, ...]:
    left, right, output = doubles(a), doubles(b), np.empty(16)
    operation = engine.library.af_matrix_relative if relative else engine.library.af_matrix_product
    engine.check(operation(pointer(left), pointer(right), pointer(output)))
    return tuple(output.tolist())


def curve_records(curve: Curve) -> Any:
    return doubles(
        [
            (
                *p.position,
                *p.left,
                *p.right,
                p.radius,
                p.tilt,
                HANDLES.index(p.left_mode),
                HANDLES.index(p.right_mode),
            )
            for p in curve.points
        ]
    )


def resolved_curve(engine: GeometryEngine, curve: Curve, records: Any = None) -> Any:
    records = curve_records(curve) if records is None else doubles(records)
    records[:, 11:13] %= 4
    engine.check(engine.library.af_curve_handles(pointer(records), len(curve.points), curve.closed))
    return records


def sample_curve(
    engine: GeometryEngine,
    curve: Curve,
    definition: Primitive,
    cancel: int = 0,
    records: Any = None,
) -> Any:
    data = curve_records(curve) if records is None else doubles(records)
    output, transform = np.empty((definition.samples, 11)), doubles(curve.matrix)
    start = definition.start if curve.start is None else curve.start
    span = definition.span if curve.span is None else curve.span
    prefix = (pointer(data), len(curve.points), curve.closed, curve.resolution, definition.samples)
    args = (*prefix, start, span, pointer(transform), pointer(output), cancel)
    engine.check(engine.library.af_curve_sample(*args))
    return output


def owned_mesh(engine: GeometryEngine, handle: int) -> Mesh:
    engine.check(not handle)
    return Mesh(engine, handle)


def loft(
    engine: GeometryEngine,
    definition: Primitive,
    samples: list[Any],
    cancel: int,
    *,
    complete: bool = True,
) -> Mesh:
    data = doubles(samples)
    args = loft_arguments(definition, data, cancel)
    operation = engine.library.af_loft if complete else engine.library.af_loft_geometry
    return owned_mesh(engine, operation(*args))


def loft_arguments(definition: Primitive, data: Any, cancel: int) -> tuple[Any, ...]:
    closed = all(cyclic(c, definition) for c in definition.curves)
    if any(c.closed for c in definition.curves) and not all(c.closed for c in definition.curves):
        raise ValueError("Loft curves must agree on open or closed topology.")
    return (
        pointer(data),
        len(data),
        definition.samples,
        definition.strips,
        closed,
        definition.caps,
        cancel,
    )


def deformed(source: Mesh, points: Any, cancel: int = 0) -> Mesh:
    data = doubles(points)
    if data.shape != source.array(0).shape:
        raise ValueError("Deformation must preserve vertex count.")
    return owned_mesh(
        source.engine,
        source.engine.library.af_mesh_deformed(
            source.handle,
            pointer(data),
            len(data),
            cancel,
        ),
    )


def joined(engine: GeometryEngine, meshes: list[Mesh], cancel: int) -> Mesh:
    handles = (U * len(meshes))(*(m.handle for m in meshes))
    return owned_mesh(engine, engine.library.af_mesh_join(handles, len(meshes), cancel))


def influence(binding: Deformer, count: int) -> Any:
    weights = np.ones(count) if not binding.weights else doubles(binding.weights).copy()
    if len(weights) != count:
        raise ValueError("Influence weights do not match target points.")
    if binding.invert and binding.weights:
        weights = 1 - weights
    if binding.restrict or binding.indices:
        mask = np.zeros(count)
        mask[[i for i in binding.indices if i < count]] = 1
        weights *= mask
    return weights


def hook(
    engine: GeometryEngine, points: Any, binding: Deformer, owner: Any, target: Any, cancel: int
) -> Any:
    data = doubles(points).copy()
    relative = matrix(engine, owner, target, relative=True)
    transform = doubles(matrix(engine, relative, binding.bind))
    uniform = doubles(binding.bind if binding.uniform else IDENTITY)
    args = (pointer(data), len(data), pointer(transform), pointer(uniform))
    engine.check(engine.library.af_hook(*args, *hook_arguments(engine, binding, len(data)), cancel))
    return data


def hook_arguments(engine: GeometryEngine, binding: Deformer, count: int) -> tuple[Any, ...]:
    center, weights = doubles(binding.center), influence(binding, count)
    custom = falloff_table(engine, binding)
    return (
        pointer(center),
        binding.strength,
        binding.radius,
        FALLOFF.index(binding.falloff),
        pointer(weights),
        pointer(custom),
        len(custom) // 2,
    )


def lattice_grid(engine: GeometryEngine, resolution: tuple[int, ...]) -> Any:
    dims = (INT * 3)(*resolution)
    output = np.empty((int(np.prod(resolution)), 3))
    engine.check(engine.library.af_lattice_grid(dims, pointer(output)))
    return output


def lattice_resolution(engine: GeometryEngine, resolution: list[int]) -> tuple[int, ...]:
    if len(resolution) != 3 or any(int(n) != n for n in resolution):
        raise ValueError("Lattice resolution requires three integers.")
    dimensions = (INT * 3)(*map(int, resolution))
    engine.check(engine.library.af_lattice_resolution(dimensions))
    return tuple(dimensions)


def lattice_points(engine: GeometryEngine, cage: Control, points: Any = None) -> Any:
    data = doubles(cage.points if points is None else points).copy()
    if cage.outside:
        engine.check(engine.library.af_lattice_outside(pointer(data), (INT * 3)(*cage.resolution)))
    return data


def lattice(
    engine: GeometryEngine,
    points: Any,
    cage: Control,
    binding: Deformer,
    owner: Any,
    target: Any,
    cancel: int,
    cage_points: Any = None,
) -> Any:
    data, controls = doubles(points).copy(), lattice_points(engine, cage, cage_points)
    transform = doubles(matrix(engine, target, owner, relative=True))
    return apply_lattice(engine, data, controls, cage, binding, transform, cancel)


def apply_lattice(
    engine: GeometryEngine,
    data: Any,
    controls: Any,
    cage: Control,
    binding: Deformer,
    transform: Any,
    cancel: int,
) -> Any:
    options = lattice_arguments(cage, binding, len(data), transform)
    args = (pointer(data), len(data), pointer(controls), *options, cancel)
    engine.check(engine.library.af_lattice(*args))
    return data


def lattice_arguments(
    cage: Control, binding: Deformer, count: int, transform: Any
) -> tuple[Any, ...]:
    weights = influence(binding, count)
    interpolation = (INT * 3)(*(INTERPOLATION.index(i) for i in cage.interpolation))
    return (
        (INT * 3)(*cage.resolution),
        interpolation,
        pointer(transform),
        binding.strength,
        pointer(weights),
        cage_weight_pointer(cage),
    )


def cage_weight_pointer(cage: Control) -> Any:
    if cage.weights and len(cage.weights) != len(cage.points):
        raise ValueError("Lattice weights must match the cage point count.")
    return pointer(doubles(cage.weights)) if cage.weights else None


THICKNESS_FIELDS = (
    "thickness",
    "offset",
    "rim",
    "rim_only",
    "even",
    "high_quality_normals",
    "flip",
    "clamp",
    "angle_clamp",
    "invert",
    "minimum",
)


def thickness_arguments(settings: Thickness) -> Any:
    return doubles([getattr(settings, name) for name in THICKNESS_FIELDS])


def solidify(source: Mesh, settings: Thickness, cancel: int) -> Mesh:
    values = thickness_arguments(settings)
    weights = doubles(settings.weights) if settings.weights else None
    if weights is not None and len(weights) != source.counts[0]:
        raise ValueError("Thickness weights do not match the unthickened mesh.")
    return owned_mesh(
        source.engine,
        source.engine.library.af_solidify(
            source.handle,
            pointer(values),
            pointer(weights) if weights is not None else None,
            cancel,
        ),
    )
