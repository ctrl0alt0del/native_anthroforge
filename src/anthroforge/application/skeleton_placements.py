"""Reviewed world-space goals are captured in the replacement surface's old bone frame."""

from dataclasses import replace
from typing import Any
from uuid import uuid4

from anthroforge.core.entities import IDENTITY
from anthroforge.core.fibers import Fiber
from anthroforge.core.points import Anchor
from anthroforge.core.surface_references import SurfaceReference
from anthroforge.core.tissues import TissueVCP
from anthroforge.native import binding_batches, components, construction, point_attachments

from . import (
    anchor_capture,
    point_evaluation,
    replacement_bindings,
    surface_providers,
    surface_queries,
)


def apply(context: Any, old_frames: Any, item: Any, target: str) -> Any:
    options = context.options.get("placements", {}).get(item.id, {})
    if not options:
        return unchanged(context, old_frames, item, target)
    goals = converted(context, old_frames, item, target, options)
    if isinstance(item, Fiber):
        return fiber(context, old_frames, item, target, goals)
    if isinstance(item, Anchor):
        return anchor(context, old_frames, item, goals)
    if isinstance(item, TissueVCP):
        return tissue(context, old_frames, item, target, goals)
    raise ValueError("This attachment does not support a surface-placement correction.")


def unchanged(context: Any, document: Any, item: Any, target: str) -> Any:
    return replacement_bindings.rebound(
        context.engine,
        context.baseline,
        document,
        context.resources,
        item,
        target,
        context.cancel.handle,
    )


def fiber(context: Any, document: Any, item: Any, target: str, goals: Any) -> Any:
    return replacement_bindings.fiber(
        context.engine,
        context.baseline,
        document,
        context.resources,
        item,
        context.cancel.handle,
        target=target,
        placements=goals,
    )


def references(item: Any) -> dict[str, SurfaceReference]:
    if isinstance(item, Fiber):
        return {b.point: b.reference for b in item.bindings}
    if isinstance(item, Anchor):
        return {item.id: item.binding.reference}
    if isinstance(item, TissueVCP):
        return {r.id: r.reference for r in item.constraints if r.reference is not None}
    return {}


def converted(context: Any, old_frames: Any, item: Any, target: str, options: Any) -> Any:
    refs, goals = references(item), {}
    for key, value in options.items():
        reference = refs.get(key) or refs.get(key.rsplit(":", 1)[0])
        if reference is None:
            raise ValueError("Placement correction no longer identifies an attachment.")
        if reference.target != target:
            continue
        require_reference(reference, value)
        goals[key] = old_position(context, old_frames, reference, value["position"])
    return goals


def require_reference(reference: Any, value: Any) -> None:
    if (value.get("target"), value.get("role"), value.get("instance", "")) != (
        reference.target,
        reference.role,
        reference.instance,
    ):
        raise ValueError("Placement corrections cannot change anatomical targets or roles.")


def old_position(context: Any, old_frames: Any, reference: Any, point: Any) -> Any:
    args = context.engine, context.document, context.assets, reference
    current = surface_providers.get(*args).frame
    previous = surface_providers.get(context.engine, old_frames, context.assets, reference).frame
    inverse = construction.matrix(context.engine, current, IDENTITY, relative=True)
    transform = construction.matrix(context.engine, previous, inverse)
    return tuple(components.transformed(context.engine, [point], transform)[0])


def anchor(context: Any, document: Any, item: Any, goals: Any) -> Any:
    binding, frame = anchor_capture.bind_point(
        context.engine,
        document,
        context.assets,
        item.binding.reference,
        goals[item.id],
        context.cancel.handle,
    )
    return point_evaluation.with_frame(replace(item, binding=binding), frame)


def tissue(context: Any, document: Any, item: Any, target: str, goals: Any) -> Any:
    updated = replacement_bindings.tissue(
        context.engine, document, context.resources, item, target, context.cancel.handle
    )
    return replace(
        updated,
        constraints=tuple(correct_region(context, document, r, goals) for r in updated.constraints),
    )


def correct_region(context: Any, document: Any, row: Any, goals: Any) -> Any:
    selected = {
        int(k.removeprefix(row.id + ":")): v for k, v in goals.items() if k.startswith(row.id + ":")
    }
    if not selected:
        return row
    batch = context.resources.bindings[row.binding_asset].records.copy()
    if min(selected) < 0 or max(selected) >= len(batch):
        raise ValueError("Constraint sample no longer exists; review the current region.")
    batch[list(selected)] = capture_points(
        context, document, row.reference, list(selected.values())
    )
    key = str(uuid4())
    context.resources.bindings[key] = binding_batches.BindingBatch(batch)
    return replace(row, binding_asset=key)


def capture_points(context: Any, document: Any, reference: Any, points: Any) -> Any:
    surfaces = surface_queries.inputs(
        context.engine, document, context.assets, [reference], context.cancel.handle
    )
    handles, frames = surfaces
    _, records = point_attachments.capture(
        context.engine, handles, frames, points, cancel=context.cancel.handle
    )
    return records
