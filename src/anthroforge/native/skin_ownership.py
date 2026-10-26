"""Instance-aware source attribution and density transfers, batched in native code."""

import ctypes as c
from dataclasses import dataclass
from typing import Any

import numpy as np

from .mesh import INT64, D, U, pointer
from .skin_fields import INT
from .skin_flow import integers


class Input(c.Structure):
    _fields_ = [
        ("vertices", D),
        ("vertex_offsets", INT),
        ("triangles", INT64),
        ("triangle_sources", INT),
        ("segments", INT64),
        ("segment_sources", INT),
        ("bone_ids", INT),
        ("candidate_offsets", INT),
        ("candidates", INT),
        ("source_count", c.c_int),
        ("vertex_count", c.c_int),
        ("triangle_count", c.c_int),
        ("segment_count", c.c_int),
        ("candidate_count", c.c_int),
    ]


@dataclass(frozen=True)
class Ownership:
    owners: Any
    sources: Any
    fallback_count: int


def configure(engine: Any) -> None:
    engine.bind("af_skin_ownership", [U, c.POINTER(Input), c.c_double, INT, INT, INT, U])
    engine.bind("af_skin_owner_regions", [INT, c.c_int, INT, c.c_int, c.c_int, INT, U])
    engine.bind("af_skin_sample_density", [U, U, INT, D, INT, D, U])


def pack(geometry: Any, offsets: Any, bones: Any, candidates: Any) -> tuple[Any, ...]:
    geometry = validate_geometry(geometry)
    arrays = tuple(np.ascontiguousarray(v, dtype=np.int32) for v in (offsets, bones))
    boundaries = [0]
    flattened = []
    for row in candidates:
        flattened.extend(row)
        boundaries.append(len(flattened))
    ranges, values = (np.ascontiguousarray(v, dtype=np.int32) for v in (boundaries, flattened))
    starts, owners = arrays
    if starts.shape != (len(owners) + 1,) or ranges.shape != starts.shape:
        raise ValueError("Ownership needs a vertex range and candidate range per source.")
    return geometry, starts, owners, ranges, values


def matrix(value: Any, dtype: Any, columns: int) -> Any:
    result = np.ascontiguousarray(value, dtype=dtype)
    if result.ndim != 2 or result.shape[1:] != (columns,):
        raise ValueError("Ownership geometry has invalid buffer dimensions.")
    return result


def labels(value: Any, size: int) -> Any:
    result = np.ascontiguousarray(value, dtype=np.int32)
    if result.shape != (size,):
        raise ValueError("Ownership element labels do not match geometry.")
    return result


def validate_geometry(geo: Any) -> Any:
    from .skin_capture import Capture

    vertices = matrix(geo.vertices, np.float64, 3)
    faces, edges = matrix(geo.triangles, np.int64, 3), matrix(geo.segments, np.int64, 2)
    owners, lines = labels(geo.owners, len(faces)), labels(geo.segment_owners, len(edges))
    return Capture(vertices, faces, owners, geo.skeletal, geo.policies, edges, lines)


def geometry_arguments(geo: Any) -> tuple[Any, ...]:
    return (
        pointer(geo.vertices),
        geo.triangles.ctypes.data_as(INT64),
        integers(geo.owners),
        geo.segments.ctypes.data_as(INT64),
        integers(geo.segment_owners),
    )


def request(data: Any) -> Input:
    geo, starts, bones, ranges, candidates = data
    xyz, *elements = geometry_arguments(geo)
    metadata = integers(bones), integers(ranges), integers(candidates)
    buffers = (xyz, integers(starts), *elements, *metadata)
    sizes = (len(bones), len(geo.vertices), len(geo.triangles), len(geo.segments), len(candidates))
    return Input(*buffers, *sizes)


def evaluate(
    mesh: Any,
    geometry: Any,
    offsets: Any,
    bones: Any,
    candidates: Any,
    ratio: float = 0.0005,
    cancel: int = 0,
) -> Ownership:
    return run(mesh, pack(geometry, offsets, bones, candidates), ratio, cancel)


def run(mesh: Any, data: Any, ratio: float, cancel: int) -> Ownership:
    packed = request(data)
    owners = np.empty(mesh.counts[0], dtype=np.int32)
    sources, fallback = np.empty_like(owners), c.c_int()
    outputs = integers(owners), integers(sources), c.byref(fallback)
    mesh.engine.check(
        mesh.engine.library.af_skin_ownership(mesh.handle, c.byref(packed), ratio, *outputs, cancel)
    )
    return Ownership(owners, sources, fallback.value)


def regions(engine: Any, owners: Any, mapping: Any, remainder: int, cancel: int = 0) -> Any:
    owners, mapping = (np.ascontiguousarray(v, dtype=np.int32) for v in (owners, mapping))
    if owners.ndim != 1 or mapping.ndim != 1:
        raise ValueError("Ownership region buffers must be vectors.")
    result = np.empty_like(owners)
    inputs = integers(owners), len(owners), integers(mapping), len(mapping), remainder
    engine.check(engine.library.af_skin_owner_regions(*inputs, integers(result), cancel))
    return result


def sample(source: Any, target: Any, owners: Any, lengths: Any, cancel: int = 0) -> tuple[Any, Any]:
    ids = np.ascontiguousarray(owners, dtype=np.int32)
    sizes = np.ascontiguousarray(lengths, dtype=np.float64)
    if ids.shape != (source.counts[0],) or sizes.shape != ids.shape:
        raise ValueError("Density sampling requires one owner and length per source vertex.")
    result, values = np.empty(target.counts[0], dtype=np.int32), np.empty(target.counts[0])
    inputs = source.handle, target.handle, integers(ids), pointer(sizes)
    source.engine.check(
        source.engine.library.af_skin_sample_density(
            *inputs, integers(result), pointer(values), cancel
        )
    )
    return result, values
