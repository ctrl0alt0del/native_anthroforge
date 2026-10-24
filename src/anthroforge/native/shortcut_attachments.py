"""Native owner-anchor capture/backsolve without Python coordinate calculations."""

import ctypes as c
from typing import Any

import numpy as np

from .attachments import CHILD_MODES, handle
from .mesh import D, GeometryEngine, U, doubles, pointer


def configure(engine: GeometryEngine) -> None:
    common = [U, D, D, D, c.c_int, c.c_int, D, D]
    engine.bind("af_shortcut_owner_anchor", common)
    engine.bind("af_shortcut_owner_backsolve", [*common, D])
    engine.bind("af_shortcut_owner_material_capture", [U, D, D, c.c_int, c.c_int, D, D])
    engine.bind("af_shortcut_owner_material_backsolve", [U, U, D, D, D, D, D, D])


def arguments(child: Any, parent: Any, meshes: Any, anchor: Any) -> tuple[Any, ...]:
    arrays = tuple(doubles(v) for v in (child.matrix, parent.matrix, child.geometry_offset))
    mode, index, fallback = anchor
    return (
        handle(child, meshes),
        *(pointer(v) for v in arrays),
        CHILD_MODES[mode],
        index,
        pointer(doubles(fallback)),
    )


def capture(engine: GeometryEngine, child: Any, parent: Any, meshes: Any) -> tuple[Any, ...]:
    binding = child.attachment.binding
    if not binding:
        raise ValueError("Owner backsolve requires a captured anatomical attachment.")
    anchor = child.attachment.child_mode, int(binding[27]), binding[18:21]
    output = np.empty(3)
    engine.check(
        engine.library.af_shortcut_owner_anchor(
            *arguments(child, parent, meshes, anchor), pointer(output)
        )
    )
    return *anchor, tuple(map(float, output))


def backsolve(
    engine: GeometryEngine, child: Any, parent: Any, meshes: Any, retained: Any
) -> tuple[float, ...]:
    mode, index, fallback, target = retained
    output, goal = np.empty(16), doubles(target)
    args = arguments(child, parent, meshes, (mode, index, fallback))
    engine.check(engine.library.af_shortcut_owner_backsolve(*args, pointer(goal), pointer(output)))
    return tuple(map(float, output))


def material_capture(engine: GeometryEngine, child: Any, meshes: Any) -> tuple[float, ...]:
    record = child.attachment.binding
    output = np.empty(28)
    engine.check(
        engine.library.af_shortcut_owner_material_capture(
            handle(child, meshes),
            pointer(doubles(child.matrix)),
            pointer(doubles(child.geometry_offset)),
            CHILD_MODES[child.attachment.child_mode],
            int(record[27]),
            pointer(doubles(record[18:21])),
            pointer(output),
        )
    )
    return tuple(map(float, output))


def material_backsolve(
    engine: GeometryEngine, child: Any, parent: Any, meshes: Any, anchor: Any
) -> tuple[float, ...]:
    output = np.empty(16)
    arrays = material_arrays(child, parent, anchor)
    handles = meshes[anchor.material_asset].handle, handle(child, meshes)
    engine.check(
        engine.library.af_shortcut_owner_material_backsolve(
            *handles,
            *(pointer(v) for v in arrays),
            pointer(output),
        )
    )
    return tuple(map(float, output))


def material_arrays(child: Any, parent: Any, anchor: Any) -> Any:
    return tuple(
        doubles(v)
        for v in (
            child.matrix,
            parent.matrix,
            child.geometry_offset,
            anchor.material_binding,
            anchor.parent_local,
        )
    )
