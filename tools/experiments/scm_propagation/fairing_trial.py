"""Owned cached reconstruction experiment; no optimizer loop or production hook."""

import ctypes as c
from pathlib import Path

import numpy as np
from regional_trial import Trial

from anthroforge.native.mesh import D, pointer


def library():
    lib = c.CDLL(str(Path("build/scm-ribs-distortion/native/af_scm_fairing.dll").resolve()))
    lib.fair_prepare.argtypes = [c.c_void_p, c.c_double]
    lib.fair_prepare.restype = c.c_void_p
    lib.fair_evaluate.argtypes = [c.c_void_p, D, D, D]
    lib.fair_evaluate.restype = c.c_int
    lib.fair_release.argtypes = [c.c_void_p]
    lib.trial_error.restype = c.c_char_p
    return lib


class Fairing:
    def __init__(self, data, fraction, width=0.2):
        self.trial = Trial(data, width=width)
        self.data = data
        self.lib = library()
        self.handle = self.lib.fair_prepare(self.trial.handle, fraction)
        if not self.handle:
            raise RuntimeError(self.lib.trial_error().decode())

    def evaluate(self, current, goals):
        result = np.empty_like(self.data.points)
        status = self.lib.fair_evaluate(
            self.handle, pointer(current), pointer(goals), pointer(result)
        )
        if status:
            raise RuntimeError(self.lib.trial_error().decode())
        return result

    def __del__(self):
        if getattr(self, "handle", None):
            self.lib.fair_release(self.handle)
