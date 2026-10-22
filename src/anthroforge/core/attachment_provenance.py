"""Exact attachment inputs, independent of resource handles and floating-point tolerances."""

from dataclasses import replace

from .entities import SCP, AttachmentReceipt
from .results import geometry_asset

EVALUATOR_VERSION = 1  # Advance when attachment evaluation semantics change.


def receipt(child: SCP, parent: SCP) -> AttachmentReceipt:
    surface = child.attachment.parent_mode == "SURFACE_NEAREST"
    return AttachmentReceipt(
        parent.id,
        parent.matrix,
        parent.geometry_offset if surface else (0.0, 0.0, 0.0),
        geometry_asset(parent) if surface else "",
        child.matrix,
        child.geometry_offset,
        child.attachment,
        EVALUATOR_VERSION,
    )


def required(entities: list[SCP], requested: set[str]) -> set[str]:
    lookup, changed = {item.id: item for item in entities}, set()
    for item in entities:
        if item.id not in requested or not item.parent:
            continue
        parent = lookup[item.parent]
        if (
            item.parent in changed
            or item.status != "ready"
            or parent.status != "ready"
            or item.pose_receipt != receipt(item, parent)
        ):
            changed.add(item.id)
    return changed


def accepted(entities: list[SCP], evaluated: set[str]) -> list[SCP]:
    lookup = {item.id: item for item in entities}
    return [
        replace(item, pose_receipt=receipt(item, lookup[item.parent]))
        if item.id in evaluated and item.parent and item.status == "ready"
        else item
        for item in entities
    ]
