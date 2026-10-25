"""Separate a curve-driven body into sibling SCPs with shared endpoint Hooks."""

from dataclasses import replace
from typing import Any
from uuid import uuid4

from anthroforge.core.construction import ResolvedPrimitive, identity
from anthroforge.core.results import EvaluationResult
from anthroforge.native import construction, curve_editing
from anthroforge.native.scene import entity_frame

from . import control_operations, curve_sources, deformer_operations, primitive_operations
from .construction_tasks import request
from .object_frames import Frames
from .presentation import include_created


def split(session: Any, entity: str, points: list[str]) -> dict[str, list[str]]:
    item = session.editable(entity)
    definition = primitive_operations.definition(session, entity)
    selected = validate(session, item, definition, points)
    source = definition.curves[0]
    segments = split_curves(session, source, selected)
    entities = install_segments(session, item, definition, segments)
    hooks = connect_segments(session, item, source, selected, entities)
    include_created(session, {e.id for e in entities} | set(hooks))
    for part in entities:
        request(session, part.id)
    return dict(entities=[e.id for e in entities], controls=hooks)


def split_curves(session: Any, source: Any, selected: list[int]) -> list[Any]:
    bounds = [0, *selected, len(source.points) - 1]
    return [
        curve_editing.segment(session.engine, source, a, b)
        for a, b in zip(bounds, bounds[1:], strict=False)
    ]


def validate(
    session: Any, item: Any, definition: ResolvedPrimitive, points: list[str]
) -> list[int]:
    if definition.kind != "BODY" or len(definition.curves) != 1 or len(definition.pieces) != 1:
        raise ValueError("Split requires a body with one guide and one body piece.")
    curve = definition.curves[0]
    if not item.parent or curve.closed or curve.engine not in ("BEZIER", "POLYLINE"):
        raise ValueError("Split requires a parent SCP and an open Bezier or Polyline guide.")
    if any(b.target.stage == "CURVE" for b in item.deformers):
        raise ValueError("Resolve existing curve deformers before splitting.")
    if curve_sources.consumers(session.document, {curve.id}) != {item.id}:
        raise ValueError("Make the shared guide independent before splitting.")
    if not whole_guide(item, definition):
        raise ValueError("Split requires whole-guide fitting without a sampling range.")
    return split_indices(curve, points)


def whole_guide(item: Any, definition: ResolvedPrimitive) -> bool:
    curve, use = definition.curves[0], item.primitive.curves[0]
    return (
        definition.pieces[0].fit
        and definition.start == 0
        and definition.span == 1
        and curve.start in (None, 0)
        and curve.span in (None, 1)
        and not use.reverse
    )


def split_indices(curve: Any, points: list[str]) -> list[int]:
    lookup = {p.id: i for i, p in enumerate(curve.points)}
    if not points or len(set(points)) != len(points) or set(points) - lookup.keys():
        raise ValueError("Select distinct interior guide points to split.")
    indices = sorted(lookup[key] for key in points)
    if indices[0] == 0 or indices[-1] == len(curve.points) - 1:
        raise ValueError("Split points must be interior guide points.")
    return indices


def install_segments(session: Any, item: Any, definition: Any, segments: list[Any]) -> list[Any]:
    first = replace(definition, curves=(segments[0],))
    curve_sources.install(session, item, first)
    result = [session.document.entity(item.id)]
    for index, segment in enumerate(segments[1:], 2):
        clone, construction = clone_segment(item, definition, segment, index)
        primitive_operations.install_new(session, clone, construction)
        result.append(session.document.entity(clone.id))
    return result


def clone_segment(item: Any, definition: Any, segment: Any, index: int) -> tuple[Any, Any]:
    curve = replace(
        segment,
        id=identity(),
        result=EvaluationResult(),
        points=tuple(replace(p, id=identity()) for p in segment.points),
    )
    piece = replace(definition.pieces[0], id=identity(), curve=curve.id)
    construction = replace(definition, curves=(curve,), pieces=(piece,))
    clone = new_clone(item, index)
    bindings = tuple(
        clone_binding(b, clone.id, definition.pieces[0].id, piece.id) for b in item.deformers
    )
    return replace(clone, deformers=bindings), construction


def new_clone(item: Any, index: int) -> Any:
    return replace(
        item,
        id=str(uuid4()),
        name=f"{item.name} {index}",
        asset="",
        primitive=None,
        result=EvaluationResult(status="pending"),
        pose_receipt=None,
    )


def clone_binding(binding: Any, owner: str, previous: str, piece: str) -> Any:
    component = piece if binding.target.component == previous else binding.target.component
    target = replace(binding.target, owner=owner, component=component)
    return replace(binding, id=identity(), target=target)


def connect_segments(
    session: Any, item: Any, source: Any, indices: list[int], entities: list[Any]
) -> list[str]:
    hooks = []
    world = construction.matrix(session.engine, entity_frame(session.engine, item), source.matrix)
    parent = Frames(session.engine, session.document).world(item.parent)
    relative = construction.matrix(session.engine, parent, world, relative=True)
    for i, index in enumerate(indices):
        location = session.engine.world_point(relative, source.points[index].position)
        hook = joint_hook(session, item, i, location)
        bind_endpoint(session, entities[i].id, hook, -1)
        bind_endpoint(session, entities[i + 1].id, hook, 0)
        hooks.append(hook)
    return hooks


def joint_hook(session: Any, item: Any, index: int, location: Any) -> str:
    return control_operations.create(
        session,
        "HOOK",
        item.parent,
        item.name + " joint " + str(index + 1),
        [*location, 0, 0, 0, 1, 1, 1],
    )


def bind_endpoint(session: Any, entity: str, hook: str, index: int) -> None:
    curve = primitive_operations.definition(session, entity).curves[0]
    index = len(curve.points) - 1 if index < 0 else index
    target = dict(owner=entity, stage="CURVE", component=curve.id)
    deformer_operations.add(session, hook, target, list(range(3 * index, 3 * index + 3)))
