"""Independent fitted display uses the addon's linear TRS channels, not anatomy evaluation."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import D, U, doubles, pointer
from .skin_fit import prediction_inputs


def configure(engine: Any) -> None:
    engine.bind("af_skin_fit_channels", [D, c.c_int, D, c.c_int, D, c.c_int, D, D, U])
    engine.bind(
        "af_skin_fit_playback", [D, c.c_int, D, c.c_int, D, D, D, c.c_int, c.c_double, D, U]
    )


def channels(engine: Any, arrays: Any, cancel: int = 0) -> tuple[Any, Any]:
    x, w, keys, matrices, _ = prediction_inputs(dict(arrays, values=arrays["keys"]))
    bases, values = np.empty((w.shape[1], 4, 4)), np.empty((len(keys), w.shape[1], 10))
    args = pointer(x), len(x), pointer(w), w.shape[1], pointer(matrices), len(keys)
    engine.check(
        engine.library.af_skin_fit_channels(*args, pointer(bases), pointer(values), cancel)
    )
    return bases, values


def inputs(arrays: Any) -> tuple[Any, ...]:
    names = "vertices", "weights", "bases", "keys", "channels"
    x, w, bases, keys, values = (doubles(arrays[n]) for n in names)
    if x.ndim != 2 or x.shape[1] != 3 or w.ndim != 2 or w.shape[0] != len(x):
        raise ValueError("Invalid fitted playback reference or weights.")
    if keys.ndim != 1 or values.shape != (len(keys), w.shape[1], 10):
        raise ValueError("Invalid fitted playback keys or channels.")
    if bases.shape != (w.shape[1], 4, 4):
        raise ValueError("Invalid fitted playback bone frames.")
    return x, w, bases, keys, values


def evaluate(engine: Any, arrays: Any, value: float, cancel: int = 0) -> Any:
    x, w, bases, keys, channels = inputs(arrays)
    output = np.empty_like(x)
    args = pointer(x), len(x), pointer(w), w.shape[1], pointer(bases), pointer(keys)
    engine.check(
        engine.library.af_skin_fit_playback(
            *args, pointer(channels), len(keys), value, pointer(output), cancel
        )
    )
    return output
