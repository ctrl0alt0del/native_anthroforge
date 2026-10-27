"""Owned LE/FAST preparation; numerical normalization and solving stay native."""

import ctypes as c
from tempfile import TemporaryDirectory
from typing import Any, cast

import numpy as np

from .mesh import D, U, doubles, pointer
from .skin_fields import INT


class Reference(c.Structure):
    _fields_ = [
        ("proxy", D),
        ("proxy_count", c.c_int),
        ("tets", INT),
        ("tet_count", c.c_int),
        ("points", D),
        ("point_count", c.c_int),
        ("samples", D),
        ("sample_count", c.c_int),
        ("weights", D),
        ("method", c.c_int),
        ("handles", c.c_int),
        ("strength", c.c_double),
        ("cache_path", c.c_char_p),
    ]


def configure(engine: Any) -> None:
    engine.bind("af_skin_deformation_prepare", [c.POINTER(Reference), U], U)
    engine.bind("af_skin_deformation_solve", [U, D, c.c_int, D, D, D, U])
    engine.bind("af_skin_deformation_embedding", [U, INT, D])
    engine.bind("af_skin_deformation_bytes", [U], U)
    engine.bind("af_skin_deformation_release", [U], None)
    engine.bind("af_skin_deformation_samples", [D, c.c_int, INT, c.c_int, c.c_int, INT, D, U])


def inputs(arrays: Any) -> tuple[Any, ...]:
    names = "proxy_vertices", "vertices", "samples", "sample_weights"
    proxy, points, samples, weights = (doubles(arrays[name]) for name in names)
    tets = np.ascontiguousarray(arrays["proxy_tets"], dtype=np.int32)
    if any(a.ndim != 2 or a.shape[1] != 3 or not len(a) for a in (proxy, points, samples)):
        raise ValueError("Skin deformation requires nonempty XYZ arrays.")
    if tets.ndim != 2 or tets.shape[1] != 4 or not len(tets):
        raise ValueError("Skin deformation requires tetrahedra.")
    if weights.shape != (len(samples),):
        raise ValueError("Skin deformation requires one weight per sample.")
    return proxy, tets, points, samples, weights


def definition(arrays: Any, settings: Any, cache_path: str) -> Reference:
    proxy, tets, points, samples, weights = arrays
    geometry = pointer(proxy), len(proxy), tets.ctypes.data_as(INT), len(tets)
    bindings = pointer(points), len(points), pointer(samples), len(samples), pointer(weights)
    return Reference(
        *geometry,
        *bindings,
        {"LE": 0, "FAST": 2}[settings.method],
        settings.fast_handles,
        settings.constraint_strength,
        (cache_path + "/cache").encode(),
    )


class Preparation:
    def __init__(self, engine: Any, arrays: Any, settings: Any, cancel: int = 0):
        self.engine, self.handle = engine, 0
        self.folder = TemporaryDirectory(prefix="anthroforge-skin-solver-")
        data = inputs(arrays)
        self.points, self.samples = len(data[2]), len(data[3])
        value = definition(data, settings, self.folder.name)
        self.handle = int(engine.library.af_skin_deformation_prepare(c.byref(value), cancel))
        engine.check(not self.handle)

    @property
    def bytes(self) -> int:
        return int(self.engine.library.af_skin_deformation_bytes(self.handle))

    def close(self) -> None:
        if getattr(self, "handle", 0):
            self.engine.library.af_skin_deformation_release(self.handle)
            self.handle = 0
        if hasattr(self, "folder"):
            self.folder.cleanup()

    def __del__(self) -> None:
        self.close()

    def __enter__(self) -> "Preparation":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def solve(self, targets: Any, cancel: int = 0) -> tuple[Any, Any, Any]:
        targets = doubles(targets)
        if targets.shape != (self.samples, 3):
            raise ValueError("Skin deformation targets must match retained samples.")
        points, predicted, report = np.empty((self.points, 3)), np.empty_like(targets), np.zeros(6)
        inputs = self.handle, pointer(targets), self.samples
        outputs = pointer(points), pointer(predicted), pointer(report)
        self.engine.check(self.engine.library.af_skin_deformation_solve(*inputs, *outputs, cancel))
        return points, report, predicted

    def embedding(self) -> tuple[Any, Any]:
        ids, weights = np.empty((self.points, 4), np.int32), np.empty((self.points, 4))
        self.engine.check(
            self.engine.library.af_skin_deformation_embedding(
                self.handle,
                ids.ctypes.data_as(INT),
                pointer(weights),
            )
        )
        return ids, weights


def sample_surface(engine: Any, points: Any, faces: Any, cancel: int = 0) -> tuple[Any, float]:
    points, faces = doubles(points), np.ascontiguousarray(faces, dtype=np.int32)
    if points.ndim != 2 or points.shape[1] != 3 or faces.ndim != 2 or faces.shape[1] < 3:
        raise ValueError("Anatomical sampling requires XYZ vertices and polygon rows.")
    selected, mass = np.empty(80, np.int32), np.zeros(1)
    geometry = pointer(points), len(points), faces.ctypes.data_as(INT), len(faces), faces.shape[1]
    count = engine.library.af_skin_deformation_samples(
        *geometry, selected.ctypes.data_as(INT), pointer(mass), cancel
    )
    engine.check(count < 0)
    return selected[:count], float(mass[0])


def cached(engine: Any, identity: str, arrays: Any, settings: Any, cancel: int = 0) -> Preparation:
    key = identity, settings
    found = engine.skin_preparations.get(key)
    if found is not None:
        return cast(Preparation, found)
    value = Preparation(engine, arrays, settings, cancel)
    return remember(engine, identity, settings, value)


def remember(engine: Any, identity: str, settings: Any, value: Preparation) -> Preparation:
    return cast(
        Preparation, engine.skin_preparations.store((identity, settings), value, value.bytes)
    )
