"""Native bulk geometry identity for inspection, never an attachment correspondence."""

import ctypes as c
from typing import Any

from .mesh import GeometryEngine, U


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_comparison_fingerprint", [U, c.c_int, c.POINTER(U), U])


def fingerprint(resource: Any, path: bool = False, cancel: int = 0) -> str:
    values = (U * 2)()
    resource.engine.check(
        resource.engine.library.af_comparison_fingerprint(resource.handle, path, values, cancel)
    )
    return "fnv-pair-v1:" + "".join(f"{value:016x}" for value in values)
