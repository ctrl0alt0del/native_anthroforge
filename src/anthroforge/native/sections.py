"""Plane contours and clip-aware ray picking preserve original material triangles."""

import ctypes as c
from typing import Any

import numpy as np

from .mesh import INT64, D, U, doubles, pointer


def configure(engine: Any) -> None:
    engine.bind("af_section_contours", [U, D, D, c.c_int, D, INT64, U])
    engine.bind("af_scene_pick_clipped", [c.c_int, c.POINTER(U), D, D, D, D, D])


def contours(mesh: Any, frame: Any, plane: Any, cancel: int = 0) -> dict[str, Any]:
    world, equation = doubles(frame), doubles(plane)
    if world.shape != (16,) or equation.shape != (4,):
        raise ValueError("A section requires a world transform and four plane coefficients.")
    lines, counts = np.empty((16384, 3)), np.zeros(3, dtype=np.int64)
    inputs = mesh.handle, pointer(world), pointer(equation), len(lines), pointer(lines)
    mesh.engine.check(
        mesh.engine.library.af_section_contours(*inputs, counts.ctypes.data_as(INT64), cancel)
    )
    return contour_report(lines, counts)


def contour_report(lines: Any, counts: Any) -> dict[str, Any]:
    return dict(
        lines=lines[: counts[0]].tolist(),
        coplanar_faces=int(counts[1]),
        truncated=bool(counts[2]),
        space="world",
        units="metres",
    )


def pick(engine: Any, handles: Any, matrices: Any, planes: Any, origin: Any, direction: Any) -> Any:
    ids, frames, clip = (
        np.ascontiguousarray(handles, dtype=np.uint64),
        doubles(matrices),
        doubles(planes),
    )
    start, ray, hits = doubles(origin), doubles(direction), np.empty((len(ids), 11))
    validate_pick(len(ids), frames, clip, start, ray)
    args = len(ids), ids.ctypes.data_as(c.POINTER(U)), pointer(frames), pointer(clip)
    count = engine.library.af_scene_pick_clipped(*args, pointer(start), pointer(ray), pointer(hits))
    engine.check(count < 0)
    return sorted(hits[:count].tolist(), key=lambda row: row[1])


def validate_pick(count: int, frames: Any, clip: Any, start: Any, ray: Any) -> None:
    if frames.size != 16 * count or clip.size != 4 * count or start.size != 3 or ray.size != 3:
        raise ValueError("Invalid clipped scene query dimensions.")
