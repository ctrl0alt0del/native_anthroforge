"""Replacement assessments prepare reviewed bindings on owned worker snapshots."""

from dataclasses import replace
from typing import Any, cast
from uuid import uuid4

from anthroforge.core.entities import SCP
from anthroforge.core.fibers import Fiber, FiberEdit
from anthroforge.core.points import Anchor
from anthroforge.core.tissues import TissueVCP
from anthroforge.native import attachments, construction

from . import (
    anchor_capture,
    attachment_candidates,
    fiber_edit_evaluation,
    object_revisions,
    point_evaluation,
    tissue_region_goals,
)
from .object_frames import Frames


def recapture(
    engine: Any, original: Any, document: Any, resources: Any, target: str, rows: Any, cancel: int
) -> tuple[dict[str, Any], dict[str, Any]]:
    entities, objects = {}, {}
    for row in rows:
        if row.action not in ("REBIND", "OWNER_BINDING"):
            continue
        item = document.object(row.target)
        changed = rebound(engine, original, document, resources, item, target, cancel)
        if isinstance(changed, SCP):
            entities[changed.id] = changed
        else:
            objects[changed.id] = object_revisions.authored(item, changed)
    return entities, objects


def rebound(
    engine: Any,
    original: Any,
    document: Any,
    resources: Any,
    item: Any,
    target: str,
    cancel: int,
    capture: Any = None,
) -> Any:
    if isinstance(item, Fiber):
        return fiber(engine, original, document, resources, item, cancel, target, capture)
    return non_curve(engine, document, resources, item, target, cancel)


def non_curve(
    engine: Any, document: Any, resources: Any, item: Any, target: str, cancel: int
) -> Any:
    if isinstance(item, SCP):
        meshes = {key: value.mesh for key, value in resources.meshes.items()}
        return attachments.capture(engine, item, document.entity(item.parent), meshes, cancel)
    if isinstance(item, Anchor):
        return anchor(engine, document, resources, item, cancel)
    if isinstance(item, TissueVCP):
        return tissue(engine, document, resources, item, target, cancel)
    raise ValueError("Unsupported incoming replacement relationship.")


def anchor(engine: Any, document: Any, resources: Any, item: Any, cancel: int) -> Any:
    args = (
        engine,
        document,
        resources.meshes,
        item.binding.reference,
        item.resolved_position,
        cancel,
    )
    binding, frame = anchor_capture.bind_point(*args)
    return point_evaluation.with_frame(replace(item, binding=binding), frame)


def fiber(
    engine: Any,
    original: Any,
    document: Any,
    resources: Any,
    item: Fiber,
    cancel: int,
    target: str = "",
    capture: Any = None,
) -> Fiber:
    current, geometry = fiber_shape(engine, original, document, resources, item, target)
    inputs = engine, current, resources, document, geometry, cancel, capture
    return capture_fiber(item, resources, inputs)


def fiber_shape(
    engine: Any, original: Any, document: Any, resources: Any, item: Fiber, target: str
) -> Any:
    accepted = resources.paths.get(item.result.asset)
    if accepted is None:
        raise ValueError("Wait for this Fiber's accepted shape before replacing its support.")
    current = capture_definition(item, accepted, document, target)
    world = Frames(engine, original).world(item.id)
    geometry = edit_geometry(accepted, world)
    return current, geometry


def capture_fiber(item: Fiber, resources: Any, inputs: Any) -> Fiber:
    _, updated, field = fiber_edit_evaluation.recapture(*inputs)
    resources.attachments[updated.attachment_asset] = field
    return restored_scopes(item, updated)


def capture_definition(item: Fiber, accepted: Any, document: Any, target: str = "") -> Fiber:
    candidates = (
        *attachment_candidates.eligible(document, item.id),
        *(b.reference for b in item.bindings),
    )
    pins = tuple(b.point for b in item.bindings if not target or b.target == target)
    edit = FiberEdit(item.result.asset, tuple(dict.fromkeys(candidates)), rebind=pins, shape=False)
    bindings = tuple(replace(b, capture_scope="CURRENT_PARENT") for b in item.bindings)
    return replace(item, points=accepted.authored.points, edit=edit, bindings=bindings)


def tissue(engine: Any, document: Any, resources: Any, item: Any, target: str, cancel: int) -> Any:
    rows = []
    for row in item.constraints:
        if row.reference is not None and row.reference.target == target:
            batch, material, signature = tissue_region_goals.capture(
                engine, document, resources, item, row.reference, cancel
            )
            key = str(uuid4())
            resources.bindings[key] = batch
            row = replace(row, material_asset=material, binding_asset=key, topology=signature)
        rows.append(row)
    return replace(item, constraints=tuple(rows))


def edit_geometry(accepted: Any, world: Any) -> Any:
    return fiber_edit_evaluation.EditGeometry(
        accepted.path, construction.curve_records(accepted.authored), world
    )


def restored_scopes(before: Fiber, after: Any) -> Fiber:
    scopes = {b.point: b.capture_scope for b in before.bindings}
    bindings = tuple(replace(b, capture_scope=scopes[b.point]) for b in after.bindings)
    return cast(Fiber, replace(after, bindings=bindings, result=before.result))
