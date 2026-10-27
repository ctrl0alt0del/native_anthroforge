"""Owned batch boundary for the maintained addon fitter and sampled prediction."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import D, U, doubles, pointer
from .skin_fields import INT


class Input(c.Structure):
    _fields_ = [
        ("vertices", D),
        ("count", c.c_int),
        ("quads", INT),
        ("quad_count", c.c_int),
        ("targets", D),
        ("frames", c.c_int),
        ("bones", c.c_int),
        ("strategy", c.c_int),
        ("smoothing", c.c_double),
    ]


def configure(engine: Any) -> None:
    engine.bind("af_skin_fit", [c.POINTER(Input), D, D, D, U])
    engine.bind("af_skin_fit_predict", [D, c.c_int, D, c.c_int, D, D, c.c_int, D, c.c_int, D, D, U])
    engine.bind("af_skin_fit_quality", [D, c.c_int, D, D, INT, c.c_int, D, U])


def inputs(vertices: Any, quads: Any, targets: Any) -> tuple[Any, Any, Any]:
    x, q, y = doubles(vertices), np.ascontiguousarray(quads, dtype=np.int32), doubles(targets)
    if x.ndim != 2 or x.shape[1] != 3 or q.ndim != 2 or q.shape[1] != 4:
        raise ValueError("Bone fitting requires XYZ positions and quad faces.")
    if y.ndim != 3 or y.shape[1:] != x.shape:
        raise ValueError("Every fitting pose must preserve vertex identities and order.")
    return x, q, y


def configuration(settings: Any) -> tuple[int, int, float]:
    strategy = settings.get("strategy", "SCALE_AWARE")
    if strategy not in ("SCALE_AWARE", "SINGLE_ACTIVE"):
        raise ValueError("Unknown skin fitting strategy.")
    bones = 2 if strategy == "SINGLE_ACTIVE" else settings.get("bones", 4)
    if type(bones) is not int or not 1 <= bones <= 64:
        raise ValueError("Invalid bone fitting settings.")
    return bones, int(strategy == "SINGLE_ACTIVE"), settings.get("smoothing", 0.0)


def fit(engine: Any, geometry: Any, settings: Any, cancel: int = 0) -> Any:
    x, q, y = inputs(*(geometry[name] for name in ("vertices", "quads", "targets")))
    options = configuration(settings)
    bones = options[0]
    w, m, report = np.zeros((len(x), bones)), np.zeros((len(y), bones, 4, 4)), np.zeros(5)
    data = Input(pointer(x), len(x), q.ctypes.data_as(INT), len(q), pointer(y), len(y), *options)
    count = engine.library.af_skin_fit(
        c.byref(data), pointer(w), pointer(m), pointer(report), cancel
    )
    engine.check(not count)
    return np.ascontiguousarray(w[:, :count]), np.ascontiguousarray(m[:, :count]), report


def prediction_inputs(arrays: Any) -> tuple[Any, ...]:
    names = "vertices", "weights", "keys", "matrices", "values"
    x, w, keys, m, values = (doubles(arrays[n]) for n in names)
    if x.ndim != 2 or x.shape[1] != 3 or w.ndim != 2 or w.shape[0] != len(x):
        raise ValueError("Invalid fitted reference or weights.")
    if keys.ndim != 1 or values.ndim != 1 or m.shape != (len(keys), w.shape[1], 4, 4):
        raise ValueError("Fitted transforms must match the saved control samples.")
    return x, w, keys, m, values


def predict(engine: Any, arrays: Any, cancel: int = 0) -> tuple[Any, Any]:
    x, w, keys, m, values = prediction_inputs(arrays)
    transforms = np.empty((len(values), w.shape[1], 4, 4))
    positions = np.empty((len(values), len(x), 3))
    args = pointer(x), len(x), pointer(w), w.shape[1], pointer(keys), pointer(m), len(keys)
    engine.check(
        engine.library.af_skin_fit_predict(
            *args, pointer(values), len(values), pointer(transforms), pointer(positions), cancel
        )
    )
    return transforms, positions


def quality(engine: Any, arrays: Any, predicted: Any, cancel: int = 0) -> Any:
    x, y, p = doubles(arrays["vertices"]), doubles(arrays["targets"]), doubles(predicted)
    training = np.ascontiguousarray(arrays["training"], dtype=np.int32)
    if x.ndim != 2 or x.shape[1] != 3 or y.ndim != 3 or y.shape[1:] != x.shape:
        raise ValueError("Invalid fitting quality geometry.")
    if p.shape != y.shape or training.shape != (len(y),):
        raise ValueError("Fitting quality requires matching sample identities.")
    output = np.empty((len(y), 4))
    args = pointer(x), len(x), pointer(y), pointer(p), training.ctypes.data_as(INT), len(y)
    engine.check(engine.library.af_skin_fit_quality(*args, pointer(output), cancel))
    return output
