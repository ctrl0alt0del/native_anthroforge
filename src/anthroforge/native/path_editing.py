"""Owned current-shape edits retain deformation residuals in native path correspondence."""

import ctypes as c
from typing import Any

import numpy as np

from anthroforge.core.construction import Curve

from . import construction, paths
from .mesh import D, GeometryEngine, U, pointer
from .point_attachments import INT


def configure(engine: GeometryEngine) -> None:
    engine.bind("af_path_rebase", [U, U, U, D, INT, c.c_int, D, U], U)
    engine.bind("af_path_control_deform", [U, U, U, U], U)


def deform(current: paths.Path, curve: Curve, records: Any, cancel: int) -> paths.Path:
    engine = current.engine
    opening = paths.evaluate(engine, curve, cancel)
    draft = paths.evaluate(engine, curve, cancel, records)
    handle = engine.library.af_path_control_deform(
        current.handle, opening.handle, draft.handle, cancel
    )
    return paths.Path(engine, handle)


def rebase(
    current: paths.Path, opening: Curve, draft: Curve, cancel: int = 0
) -> tuple[paths.Path, Any]:
    engine = current.engine
    old = paths.evaluate(engine, opening, cancel)
    records = construction.resolved_curve(engine, draft)
    new = paths.evaluate(engine, draft, cancel, records)
    identities = {p.id: i for i, p in enumerate(opening.points)}
    indices = np.asarray([identities.get(p.id, -1) for p in draft.points], dtype=np.int32)
    return rebase_native((current, old, new), records, indices, cancel)


def rebase_native(
    inputs: tuple[paths.Path, ...], records: Any, indices: Any, cancel: int
) -> tuple[paths.Path, Any]:
    output = np.empty_like(records)
    args = (pointer(records), indices.ctypes.data_as(INT), len(records), pointer(output), cancel)
    engine = inputs[0].engine
    handle = engine.library.af_path_rebase(*(path.handle for path in inputs), *args)
    return paths.Path(engine, handle), output
