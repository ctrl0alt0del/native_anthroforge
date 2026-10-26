"""Owned topology proxy; source geometry and anatomical bindings remain untouched."""

import ctypes as c
from typing import Any

from .mesh import Mesh, U


def configure(engine: Any) -> None:
    engine.bind("af_skin_proxy_decimate", [U, c.c_int, U, U], U)


def decimate(mesh: Mesh, target: int, budget: int = 1024**3, cancel: int = 0) -> Mesh:
    if type(target) is not int or not 1 <= target <= 2**31 - 1:
        raise ValueError("Skin proxy needs a positive integer face target.")
    if type(budget) is not int or not 1 <= budget <= 2**63 - 1:
        raise ValueError("Skin proxy needs a positive memory budget.")
    handle = mesh.engine.library.af_skin_proxy_decimate(mesh.handle, target, budget, cancel)
    mesh.engine.check(not handle)
    return Mesh(mesh.engine, handle)
