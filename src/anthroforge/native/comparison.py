"""Native bulk geometry identity for inspection, never an attachment correspondence."""

import ctypes as c
from typing import Any

from .mesh import INT64, D, GeometryEngine, U, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_comparison_fingerprint", [U, c.c_int, c.POINTER(U), U])
    engine.bind("af_comparison_distances", [U, D, U, D, c.c_int, D, INT64, U])


def fingerprint(resource: Any, path: bool = False, cancel: int = 0) -> str:
    values = (U * 2)()
    resource.engine.check(
        resource.engine.library.af_comparison_fingerprint(resource.handle, path, values, cancel)
    )
    return "fnv-pair-v1:" + "".join(f"{value:016x}" for value in values)


def distances(first: Any, a: Any, second: Any, b: Any, verified: bool, cancel: int = 0) -> Any:
    values, counts = (c.c_double * 8)(), (c.c_int64 * 2)()
    frames = tuple(doubles(frame) for frame in (a, b))
    if any(frame.size != 16 for frame in frames):
        raise ValueError("Geometry comparison requires world frames.")
    args = first.handle, pointer(frames[0]), second.handle, pointer(frames[1]), verified
    first.engine.check(first.engine.library.af_comparison_distances(*args, values, counts, cancel))
    return distance_summary(values, counts, verified)


def distance_summary(values: Any, counts: Any, verified: bool) -> dict[str, Any]:
    return dict(
        geometric=statistics(values[:4], counts[0]),
        material=statistics(values[4:], counts[1]) if verified else None,
        units="m",
        method="Bidirectional vertex-to-surface samples; not a Hausdorff bound",
    )


def statistics(values: Any, count: int) -> dict[str, Any]:
    return dict(zip(("minimum", "maximum", "mean", "rms"), values, strict=True), samples=count)
