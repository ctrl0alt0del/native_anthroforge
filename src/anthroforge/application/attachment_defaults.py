"""Shared nearest-SCP defaults; all geometric searches stay in the native service."""

from typing import Any

from anthroforge.native import point_attachments

from . import attachment_assets, attachment_candidates


def candidates(document: Any) -> tuple[Any, ...]:
    targets = tuple(
        ref for ref in attachment_candidates.eligible(document, "") if ref.role == "SCP_GEOMETRY"
    )
    if not targets:
        raise ValueError("No ready SCP surfaces. Import an SCP or choose explicit binding targets.")
    return targets


def nearest(engine: Any, document: Any, resources: Any, positions: Any, cancel: int) -> Any:
    targets = candidates(document)
    surfaces = attachment_assets.surface_inputs(engine, document, resources.meshes, targets, cancel)
    handles, frames = surfaces
    owners, _ = point_attachments.capture(engine, handles, frames, positions, cancel=cancel)
    return tuple(targets[index] for index in owners)
