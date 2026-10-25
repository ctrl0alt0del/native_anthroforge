"""Owned experimental native kernel; no runtime registration or monkey-patching."""

import ctypes as c
from pathlib import Path

import numpy as np

from anthroforge.native.mesh import D, doubles, pointer

INT = c.c_int
IP = c.POINTER(INT)
H = c.c_void_p


def library():
    lib = c.CDLL(str(Path("build/scm-ribs-distortion/native/af_scm_trial.dll").resolve()))
    lib.trial_prepare.argtypes = [INT, INT, INT, D, D, D, IP, D, INT, IP, IP, INT, INT, c.c_double]
    lib.trial_prepare.restype = H
    lib.trial_evaluate.argtypes = [H, D, D, D, D]
    lib.trial_evaluate.restype = INT
    lib.trial_release.argtypes = [H]
    lib.trial_error.restype = c.c_char_p
    lib.trial_arcs.argtypes = [INT, INT, D, IP, D]
    lib.trial_parameters.argtypes = [INT, D, INT, D, D]
    return lib


def integers(value):
    return np.ascontiguousarray(value, dtype=np.int32)


def arcs(lib, points, n):
    nodes = integers([i if i < n else (i - n) // 3 for i in range(len(points))])
    result = np.empty(len(points))
    lib.trial_arcs(n, len(points), pointer(points), nodes.ctypes.data_as(IP), pointer(result))
    return result


class Trial:
    def __init__(self, data, width=0.2, regions=8, neighbors=64):
        self.lib = library()
        self.data = data
        self.arc = arcs(self.lib, data.points, data.samples)
        self.width = width * self.arc[data.samples - 1]
        self.handle = self.prepare(regions, neighbors)
        if not self.handle:
            raise RuntimeError(self.lib.trial_error().decode())

    def prepare(self, regions, neighbors):
        d = self.data
        counts = integers(d.counts)
        pins = integers(d.pins)
        owners = integers(d.pin_parents)
        geometry = (pointer(d.points), pointer(self.arc), pointer(d.weights))
        parents = (counts.ctypes.data_as(IP), pointer(d.before))
        anchors = (len(pins), pins.ctypes.data_as(IP), owners.ctypes.data_as(IP))
        prefix = (d.samples, len(d.points), len(counts))
        arguments = (*prefix, *geometry, *parents, *anchors, regions, neighbors, self.width)
        return self.lib.trial_prepare(*arguments)

    def evaluate(self, current, goals):
        d = self.data
        result = np.empty_like(d.points)
        status = self.lib.trial_evaluate(
            self.handle, pointer(d.before), pointer(current), pointer(goals), pointer(result)
        )
        if status:
            raise RuntimeError(self.lib.trial_error().decode())
        return result

    def __del__(self):
        if getattr(self, "handle", None):
            self.lib.trial_release(self.handle)


def parameters(lib, values, stations):
    a, b = doubles(values), doubles(stations)
    result = np.empty(len(a))
    lib.trial_parameters(len(a), pointer(a), len(b), pointer(b), pointer(result))
    return result
