"""Separate selectable anatomical anchors from automatic deformation supports."""

from dataclasses import replace
from typing import Any

from anthroforge.core.fiber_support_policy import FiberSupportPolicy
from anthroforge.native import attachment_fields, components, point_attachments

from . import attachment_assets

DEFAULT_POLICY = FiberSupportPolicy()


def deformation_targets(candidates: Any, parents: Any) -> tuple[Any, ...]:
    explicit = set(parents)
    if any(ref.role != "SCP_GEOMETRY" for ref in explicit):
        return tuple(sorted(explicit))
    return tuple(sorted(explicit | {ref for ref in candidates if ref.role == "SCP_GEOMETRY"}))


def selected_targets(candidates: Any, parents: Any, policy: FiberSupportPolicy) -> tuple[Any, ...]:
    automatic = set(deformation_targets(candidates, parents)) if policy.automatic else set(parents)
    return tuple(sorted((automatic | set(policy.included)) - set(policy.excluded) | set(parents)))


def resolve_parents(
    engine: Any, document: Any, resources: Any, targets: Any, request: Any, cancel: int
) -> tuple[Any, ...]:
    parents = list(request.parents)
    automatic = [i for i, parent in enumerate(parents) if parent < 0]
    if automatic:
        owners = automatic_owners(engine, document, resources, targets, request, automatic, cancel)
        for i, owner in zip(automatic, owners, strict=True):
            parents[i] = int(owner)
    return tuple(targets[parent] for parent in parents)


def automatic_owners(
    engine: Any,
    document: Any,
    resources: Any,
    targets: Any,
    request: Any,
    indices: Any,
    cancel: int,
) -> Any:
    pins = [request.pins[i] for i in indices]
    positions = components.transformed(engine, request.records[pins, :3], request.world)
    surfaces = attachment_assets.surface_inputs(engine, document, resources.meshes, targets, cancel)
    handles, frames = surfaces
    owners, _ = point_attachments.capture(engine, handles, frames, positions, cancel=cancel)
    return owners


def capture(
    engine: Any,
    document: Any,
    resources: Any,
    candidates: Any,
    request: Any,
    cancel: int,
    policy: FiberSupportPolicy = DEFAULT_POLICY,
) -> tuple[Any, Any]:
    parents = resolve_parents(engine, document, resources, candidates, request, cancel)
    targets = selected_targets(candidates, parents, policy)
    request = replace(request, parents=[targets.index(parent) for parent in parents])
    return capture_field(engine, document, resources, targets, request, cancel)


def capture_field(
    engine: Any, document: Any, resources: Any, targets: Any, request: Any, cancel: int
) -> tuple[Any, Any]:
    surfaces = attachment_assets.surface_inputs(engine, document, resources.meshes, targets, cancel)
    field = attachment_fields.capture(engine, surfaces, request, cancel)
    captures = attachment_assets.captures(engine, document, resources.meshes, targets)
    return field, captures
