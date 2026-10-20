"""Automatic pin choices use native queries on dispatch-time accepted SCP surfaces."""

from dataclasses import replace
from typing import Any

from anthroforge.native import components

from . import attachment_defaults


def resolve(
    engine: Any, spec: Any, document: Any, resources: Any, request: Any, cancel: int
) -> Any:
    automatic = [index for index, row in enumerate(spec.bindings) if row[1] is None]
    if not automatic:
        return spec
    pins = [request.pins[index] for index in automatic]
    positions = components.transformed(engine, request.records[pins, :3], request.world)
    targets = attachment_defaults.nearest(engine, document, resources, positions, cancel)
    return resolved_bindings(spec, automatic, targets)


def resolved_bindings(spec: Any, automatic: Any, targets: Any) -> Any:
    bindings = list(spec.bindings)
    for index, target in zip(automatic, targets, strict=True):
        point, _, scope = bindings[index]
        bindings[index] = (point, target, scope)
    return replace(spec, bindings=tuple(bindings))
