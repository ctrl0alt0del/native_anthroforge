"""Owned curve edits reuse current-shape, junction and authored-revision policies."""

from dataclasses import dataclass, replace
from typing import Any

import numpy as np

from anthroforge.core.construction import Curve
from anthroforge.native import components, construction, curve_editing, scene

from . import curve_edit_state, curve_sources, junction_edits, object_revisions, surface_queries


@dataclass(frozen=True)
class Context:
    engine: Any
    document: Any
    resources: Any


def destination(context: Context, request: Any, cancel: int) -> list[float]:
    inputs = surface_queries.inputs(
        context.engine, context.document, context.resources.meshes, request["targets"], cancel
    )
    handles, frames = inputs
    hits = scene.pick(
        context.engine,
        np.asarray(handles, dtype=np.uint64),
        np.asarray(frames),
        request["origin"],
        request["direction"],
    )
    if not len(hits):
        raise ValueError("No exterior surface under the confirmed placement ray.")
    return hit_position(context.engine, inputs, hits[0], request["offset"])


def hit_position(engine: Any, inputs: Any, hit: Any, offset: float) -> list[float]:
    handles, frames = inputs
    result = scene.surface_snap(
        engine,
        handles[int(hit[0])],
        frames[int(hit[0])],
        int(hit[3]),
        hit[5:8],
        offset,
    )
    return list(result["point"])


def shifted(context: Context, item: Curve, refs: Any, delta: Any) -> Curve:
    world = curve_sources.world(context.engine, context.document, item.id)
    translation = context.engine.transform([*delta, 0, 0, 0, 1, 1, 1])
    moved = construction.matrix(context.engine, translation, world, relative=False)
    local = construction.matrix(context.engine, world, moved, relative=True)
    points = [junction_edits.point(item, ref["point"]) for ref in refs]
    values = components.transformed(
        context.engine, [getattr(p, r["part"]) for p, r in zip(points, refs, strict=True)], local
    )
    grouped: dict[str, dict[str, Any]] = {}
    for ref, value in zip(refs, values.tolist(), strict=True):
        grouped.setdefault(ref["point"], {})[ref["part"]] = tuple(value)
    return apply_points(context.engine, item, grouped)


def apply_points(engine: Any, item: Curve, options: Any) -> Curve:
    points = tuple(
        curve_editing.point(engine, item, index, options[p.id]) if p.id in options else p
        for index, p in enumerate(item.points)
    )
    return replace(item, points=points)


def evaluate(context: Context, request: Any, cancel: int) -> dict[str, Any]:
    if "samples" in request:
        return sample_changes(context, request, cancel)
    location = destination(context, request, cancel)
    delta = [v - p for v, p in zip(location, request["preview"], strict=True)]
    changes = {}
    for key in {ref["curve"] for ref in request["components"]}:
        item = curve_edit_state.current(context, context.document.object(key))
        refs = [ref for ref in request["components"] if ref["curve"] == key]
        changed = shifted(context, item, refs, delta)
        changes[key] = curve_edit_state.prepare(context, item, changed)
    return junction_edits.expand(context, changes)


def sample_changes(context: Context, request: Any, cancel: int) -> dict[str, Any]:
    key = request["components"][0]["curve"]
    item = curve_edit_state.current(context, context.document.object(key))
    local = projected_positions(context, request, item, cancel)
    changes = {p.id: dict(position=tuple(v)) for p, v in zip(item.points, local, strict=True)}
    changed = curve_edit_state.prepare(context, item, apply_points(context.engine, item, changes))
    return junction_edits.expand(context, {item.id: changed})


def projected_positions(context: Context, request: Any, item: Curve, cancel: int) -> Any:
    from .placement_inputs import confirmed

    world = curve_sources.world(context.engine, context.document, item.id)
    positions = components.transformed(context.engine, [p.position for p in item.points], world)
    samples = [[*p, knot.radius] for p, knot in zip(positions, item.points, strict=True)]
    intent = dict(targets=request["targets"], queries=request["samples"])
    output = confirmed(context.engine, context.document, context.resources, samples, intent, cancel)
    inverse = construction.matrix(context.engine, world, np.eye(4).ravel(), relative=True)
    return components.transformed(context.engine, output[:, :3], inverse)


def merge(document: Any, changes: Any) -> Any:
    objects = tuple(
        merge_item(item, changes[item.id]) if item.id in changes else item
        for item in document.objects
    )
    return replace(document, objects=objects)


def merge_item(before: Any, changed: Any) -> Any:
    options = {
        key: getattr(changed, key)
        for key in ("points", "edit", "bindings")
        if hasattr(changed, key)
    }
    return object_revisions.authored(before, replace(before, **options))
