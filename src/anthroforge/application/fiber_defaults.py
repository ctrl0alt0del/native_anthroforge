"""Automatic pin choices use native queries on dispatch-time accepted SCP surfaces."""

from dataclasses import replace
from typing import Any

from anthroforge.native import components, point_attachments

from . import attachment_assets, attachment_candidates


def candidates(document: Any) -> tuple[Any, ...]:
    targets = tuple(
        ref for ref in attachment_candidates.eligible(document, "") if ref.role == "SCP_GEOMETRY"
    )
    if not targets:
        raise ValueError("No ready SCP surfaces. Import an SCP or choose explicit binding targets.")
    return targets


def resolve(
    engine: Any, spec: Any, document: Any, resources: Any, request: Any, cancel: int
) -> Any:
    automatic = [index for index, row in enumerate(spec.bindings) if row[1] is None]
    if not automatic:
        return spec
    targets = candidates(document)
    pins = [request.pins[index] for index in automatic]
    positions = components.transformed(engine, request.records[pins, :3], request.world)
    handles, frames = attachment_assets.surface_inputs(engine, document, resources.meshes, targets)
    owners, _ = point_attachments.capture(engine, handles, frames, positions, cancel=cancel)
    return resolved_bindings(spec, automatic, targets, owners)


def resolved_bindings(spec: Any, automatic: Any, targets: Any, owners: Any) -> Any:
    bindings = list(spec.bindings)
    for index, owner in zip(automatic, owners, strict=True):
        point, _, scope = bindings[index]
        bindings[index] = (point, targets[owner], scope)
    return replace(spec, bindings=tuple(bindings))
