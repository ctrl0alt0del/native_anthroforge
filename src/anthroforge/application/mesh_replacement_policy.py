"""Reviewed changes needed when an imported source loses indexed correspondence."""

from dataclasses import dataclass, replace
from typing import Any

from anthroforge.core.attachment_references import targets
from anthroforge.core.entities import SCP
from anthroforge.core.fibers import Fiber
from anthroforge.core.points import Anchor
from anthroforge.core.tissues import TissueVCP


@dataclass(frozen=True)
class Change:
    key: str
    target: str
    action: str
    description: str


def incoming(document: Any, target: str) -> tuple[Any, ...]:
    return tuple(
        item
        for item in document.registry.records.values()
        if (isinstance(item, SCP) and item.parent == target) or target in targets(item)
    )


def assess(document: Any, item: Any, matching: bool) -> tuple[Change, ...]:
    if matching:
        return ()
    rows = [
        Change("rebind:" + child.id, child.id, "REBIND", description(child))
        for child in incoming(document, item.id)
    ]
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


def description(item: Any) -> str:
    if isinstance(item, Fiber):
        return "Recapture this Fiber's deformation supports and pins from its accepted shape."
    if isinstance(item, Anchor):
        return "Recapture this Anchor on the same target from its accepted position."
    if isinstance(item, TissueVCP):
        return "Recapture target-relative tissue region goals on the same target."
    return "Recapture this child SCP's attachment while preserving its current pose."


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
