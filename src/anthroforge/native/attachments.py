"""Batch attachment capture and propagation, without host or UI objects."""

import ctypes as c
from collections import deque
from dataclasses import replace
from threading import Event
from typing import Any

import numpy as np

from anthroforge.core.entities import SCP
from anthroforge.core.results import geometry_asset

from .mesh import GeometryEngine, Mesh, doubles, pointer

CHILD_MODES = {"FACE_CENTER": 0, "VERTEX_NEAREST": 1, "OBJECT_ORIGIN": 2}


def capture(engine: GeometryEngine, child: SCP, parent: SCP, meshes: dict[str, Mesh]) -> SCP:
    settings = child.attachment
    arrays = [
        doubles(v)
        for v in (child.matrix, parent.matrix, child.geometry_offset, parent.geometry_offset)
    ]
    output = np.empty(28)
    handles = (handle(child, meshes), handle(parent, meshes))
    status = engine.library.af_capture(
        *handles, *(pointer(a) for a in arrays), *capture_options(child), pointer(output)
    )
    engine.check(status)
    return replace(child, attachment=replace(settings, binding=tuple(output.tolist())))


def anchor_points(engine: GeometryEngine, child: SCP, parent: SCP, mesh: int) -> list[float]:
    values = (child.matrix, parent.matrix, parent.geometry_offset, child.attachment.binding)
    arrays, output = [doubles(value) for value in values], np.empty(6)
    engine.check(
        engine.library.af_anchor_points(mesh, *(pointer(a) for a in arrays), pointer(output))
    )
    return list(output.tolist())


def capture_options(child: SCP) -> tuple[Any, ...]:
    settings = child.attachment
    locked = settings.vertex_lock if settings.child_mode == "VERTEX_NEAREST" else settings.face_lock
    return (
        settings.parent_mode == "SURFACE_NEAREST",
        CHILD_MODES[settings.child_mode],
        locked,
        settings.strategy == "DEFORMATION_FLOW",
    )


def handle(entity: SCP, meshes: dict[str, Mesh]) -> int:
    key = geometry_asset(entity)
    return meshes[key].handle if key else 0


def ordered(entities: tuple[SCP, ...]) -> list[SCP]:
    children: dict[str, list[SCP]] = {}
    for item in entities:
        children.setdefault(item.parent, []).append(item)
    result, pending = [], deque(children.get("", ()))
    while pending:
        item = pending.popleft()
        result.append(item)
        pending.extend(children.get(item.id, ()))
    if len(result) != len(entities):
        raise ValueError("Invalid attachment hierarchy.")
    return result


def packed(entities: list[SCP], meshes: dict[str, Mesh], active: set[str]) -> dict[str, Any]:
    lookup = {item.id: i for i, item in enumerate(entities)}
    return {
        **packed_flags(entities, active),
        "meshes": np.array([handle(e, meshes) for e in entities], dtype=np.uint64),
        "parents": np.array([lookup.get(e.parent, -1) for e in entities], dtype=np.int32),
        "matrices": doubles([e.matrix for e in entities]),
        "offsets": doubles([e.geometry_offset for e in entities]),
        "bindings": doubles([e.attachment.binding or (0.0,) * 28 for e in entities]),
    }


def packed_flags(entities: list[SCP], active: set[str]) -> dict[str, Any]:
    return {
        "modes": flags(entities, lambda e: e.attachment.parent_mode == "SURFACE_NEAREST"),
        "follows": flags(entities, lambda e: e.attachment.follow_rotation),
        "flows": flags(entities, lambda e: e.attachment.strategy == "DEFORMATION_FLOW"),
        "active": flags(
            entities,
            lambda e: e.id in active and bool(e.attachment.binding) and e.status != "failed",
        ),
        "status": flags(entities, lambda e: e.status == "failed"),
    }


def flags(entities: list[SCP], predicate: Any) -> Any:
    return np.array([predicate(e) for e in entities], dtype=np.int32)


def propagate(
    engine: GeometryEngine,
    entities: list[SCP],
    meshes: dict[str, Mesh],
    active: set[str],
    cancel: Event,
) -> list[SCP]:
    if not entities or cancel.is_set():
        return entities
    data = packed(entities, meshes, active)
    apply_batch(engine, data, len(entities), cancel)
    return [
        evaluated(item, data["matrices"][i], data["status"][i]) if item.id in active else item
        for i, item in enumerate(entities)
    ]


def apply_batch(engine: GeometryEngine, data: dict[str, Any], count: int, cancel: Event) -> None:
    integers = ("modes", "follows", "flows", "active", "status")
    status = engine.library.af_propagate(
        count,
        data["meshes"].ctypes.data_as(c.POINTER(c.c_uint64)),
        int_pointer(data["parents"]),
        *(pointer(data[key]) for key in ("matrices", "offsets", "bindings")),
        *(int_pointer(data[key]) for key in integers),
        getattr(cancel, "handle", 0),
    )
    engine.check(status)


def int_pointer(array: Any) -> Any:
    return array.ctypes.data_as(c.POINTER(c.c_int))


def evaluated(entity: SCP, matrix: Any, failed: int) -> SCP:
    message = (
        entity.error or "Attachment or an upstream attachment failed; recapture or change anchor."
        if failed
        else ""
    )
    return replace(
        entity, matrix=tuple(matrix.tolist()), status="failed" if failed else "ready", error=message
    )


def move_origin(engine: GeometryEngine, entity: SCP) -> SCP:
    if not entity.attachment.binding:
        raise ValueError("Capture the attachment before moving its origin.")
    arrays = [
        doubles(v) for v in (entity.matrix, entity.geometry_offset, entity.attachment.binding)
    ]
    matrix, offset = np.empty(16), np.empty(3)
    engine.check(
        engine.library.af_move_origin(
            *(pointer(a) for a in arrays), pointer(matrix), pointer(offset)
        )
    )
    return replace(entity, matrix=tuple(matrix.tolist()), geometry_offset=tuple(offset.tolist()))
