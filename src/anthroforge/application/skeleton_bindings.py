"""Reviewed capture policy over unchanged production attachment services."""

from dataclasses import replace
from functools import partial
from typing import Any

from anthroforge.core.entities import SCP
from anthroforge.core.results import geometry_asset
from anthroforge.core.skeleton_update import BoneChange, Finding
from anthroforge.native import attachments, topology

from . import (
    assembly_evidence,
    object_revisions,
    replacement_bindings,
    replacement_reviews,
    scp_surface_parents,
    surface_providers,
)
from .entity_revisions import GEOMETRY_FIELDS, differs


def changes(context: Any, p: Any) -> tuple[BoneChange, ...]:
    result = []
    for original in p.selection.records.values():
        if not isinstance(original, SCP):
            continue
        target = p.ids[original.id]
        after = context.document.entity(target)
        before = context.baseline.index.entities.get(target)
        result.append(change(context, original.id, before, after))
    return tuple(result)


def change(context: Any, source: str, before: Any, after: Any) -> BoneChange:
    compatible = matching(context, before, after) if before else False
    placement = before is None or differs(before, after, ("matrix", "geometry_offset"))
    construction = before is None or differs(before, after, GEOMETRY_FIELDS)
    return BoneChange(
        source,
        after.id,
        placement,
        construction,
        "verified" if compatible else "unverified",
        before is None,
    )


def matching(context: Any, before: Any, after: Any) -> bool:
    first, second = geometry_asset(before), geometry_asset(after)
    if not first or not second:
        return not first and not second
    return topology.same_topology(
        context.assets[first].mesh, context.assets[second].mesh, context.cancel.handle
    )


def capture_bones(context: Any, changes: Any, options: Any) -> list[dict[str, Any]]:
    evidence = []
    for row in changes:
        item = context.document.entity(row.target)
        if not item.parent:
            continue
        if locked(item, row) and options.get("clear_locks", {}).get(item.id) is not True:
            context.findings.append(lock_finding(item))
            continue
        capture_bone(context, item, row, evidence)
    return evidence


def lock_finding(item: Any) -> Finding:
    return Finding(
        "lock:" + item.id,
        item.id,
        "Review incompatible child-anchor locks; explicitly clear them.",
        blocking=True,
    )


def locked(item: Any, change: BoneChange) -> bool:
    return change.correspondence != "verified" and (
        item.attachment.face_lock >= 0 or item.attachment.vertex_lock >= 0
    )


def capture_bone(context: Any, item: Any, row: Any, evidence: Any) -> None:
    before = context.baseline.index.entities.get(item.id)
    if locked(item, row):
        item = replace(item, attachment=replace(item.attachment, face_lock=-1, vertex_lock=-1))
    updated = captured_bone(context, item)
    context.install(replace(updated, capture_parent_matrix=(), pose_receipt=None))
    if before is None or updated.attachment != before.attachment:
        record_bone_capture(context, before, updated, evidence)


def captured_bone(context: Any, item: Any) -> Any:
    meshes = {key: asset.mesh for key, asset in context.assets.items()}
    frame = scp_surface_parents.reflections(context.document, {item.id}).get(item.id)
    return attachments.capture(
        context.engine,
        item,
        context.document.entity(item.parent),
        meshes,
        context.cancel.handle,
        frame,
    )


def record_bone_capture(context: Any, before: Any, item: Any, evidence: Any) -> None:
    context.findings.append(
        Finding(
            "bone_capture:" + item.id,
            item.id,
            "Preserve replacement pose with a recaptured bone attachment.",
            acknowledge=True,
            kind="attachment",
        )
    )
    previous = locations(context, context.baseline, before) if before else []
    evidence.append(
        dict(owner=item.id, before=previous, after=locations(context, context.document, item))
    )


def locations(context: Any, document: Any, item: Any) -> Any:
    provider = partial(surface_providers.snapshot, context.engine, document, context.assets)
    return assembly_evidence.locations(
        context.engine,
        item,
        provider,
        context.assets,
        context.cancel.handle,
        document,
        context.resources.bindings,
    )


def old_frames(context: Any) -> Any:
    originals = context.baseline.index.entities
    entities = tuple(
        replace(
            item,
            matrix=originals[item.id].matrix,
            geometry_offset=originals[item.id].geometry_offset,
        )
        if item.id in context.fixed_poses and item.id in originals
        else item
        for item in context.document.entities
    )
    return replace(context.document, entities=entities)


def rebind_dependents(context: Any, changes: Any, options: Any) -> list[dict[str, Any]]:
    evidence = []
    for row in changes:
        if row.added or row.correspondence == "verified":
            continue
        for item in replacement_reviews.incoming(context.baseline, row.target):
            if item.id in context.fixed_poses:
                continue
            rebind(context, item.id, row.target, options, evidence)
    return evidence


def rebind(context: Any, owner: str, target: str, options: Any, evidence: Any) -> None:
    key = "rebind:" + owner + ":" + target
    enabled = options.get("rebind", {}).get(key, False)
    context.findings.append(rebind_finding(key, owner, bool(enabled)))
    if not enabled:
        return
    item = context.document.object(owner)
    before = locations(context, context.baseline, context.baseline.object(owner))
    changed = rebound_item(context, item, target)
    context.install(changed if isinstance(item, SCP) else object_revisions.authored(item, changed))
    after = locations(context, context.document, changed)
    evidence.append(dict(owner=owner, target=target, before=before, after=after))


def rebind_finding(key: str, owner: str, enabled: bool) -> Finding:
    return Finding(
        key,
        owner,
        "Recapture attachment on replacement surface.",
        blocking=not enabled,
        acknowledge=enabled,
        kind="attachment",
    )


def rebound_item(context: Any, item: Any, target: str) -> Any:
    return replacement_bindings.rebound(
        context.engine,
        context.baseline,
        old_frames(context),
        context.resources,
        item,
        target,
        context.cancel.handle,
    )
