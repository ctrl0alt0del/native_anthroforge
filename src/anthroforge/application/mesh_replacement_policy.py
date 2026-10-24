"""Reviewed changes needed when an imported source loses indexed correspondence."""

from dataclasses import replace
from typing import Any

from anthroforge.core.replacement_reviews import Change

from .replacement_reviews import binding_changes


def assess(document: Any, item: Any, matching: bool) -> tuple[Change, ...]:
    if matching:
        return ()
    rows = binding_changes(document, item.id)
    return tuple((*rows, *owned_changes(item), *deformer_changes(item)))


def owned_changes(item: Any) -> list[Change]:
    rows = []
    if item.parent and item.attachment.child_mode != "OBJECT_ORIGIN":
        rows.append(
            local_change(item, "OWNER_BINDING", "Recapture child anchor; release old locks.")
        )
    if item.thickness and item.thickness.weights:
        rows.append(local_change(item, "THICKNESS_WEIGHTS", "Clear thickness vertex weights."))
    return rows


def local_change(item: Any, action: str, description: str) -> Change:
    return Change(action.lower() + ":" + item.id, item.id, action, description)


def deformer_changes(item: Any) -> list[Change]:
    return [
        Change(
            "deformer:" + b.id,
            item.id,
            "REMOVE_DEFORMER",
            "Remove indexed deformer " + b.id + "; preserve its shared control.",
        )
        for b in item.deformers
        if b.target.stage == "GEOMETRY"
        and (b.indices or b.weights or b.members or b.weighted_members or b.restrict)
    ]


def adjusted(item: Any, changes: tuple[Change, ...]) -> Any:
    removed = {
        row.key.removeprefix("deformer:") for row in changes if row.action == "REMOVE_DEFORMER"
    }
    thickness = item.thickness
    if thickness and any(row.action == "THICKNESS_WEIGHTS" for row in changes):
        thickness = replace(thickness, weights=())
    attachment = item.attachment
    if any(row.action == "OWNER_BINDING" for row in changes):
        attachment = replace(attachment, face_lock=-1, vertex_lock=-1)
    bindings = tuple(b for b in item.deformers if b.id not in removed)
    return replace(item, deformers=bindings, thickness=thickness, attachment=attachment)
