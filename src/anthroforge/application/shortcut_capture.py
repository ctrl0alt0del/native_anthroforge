"""Prepare temporary attachment bindings from the owned pre-edit state."""

from dataclasses import replace
from typing import Any

from anthroforge.core.entities import SCP
from anthroforge.core.results import geometry_asset
from anthroforge.core.shortcut_edits import OverrideBinding, OwnerAnchor, ShortcutEdit
from anthroforge.native import attachments, shortcut_attachments


def snapshot(item: SCP) -> SCP:
    return SCP(
        item.name,
        id=item.id,
        parent=item.parent,
        asset=geometry_asset(item),
        matrix=item.matrix,
        geometry_offset=item.geometry_offset,
        attachment=item.attachment,
        primitive=item.primitive,
    )


def source_entities(document: Any, owner: str, policy: Any) -> tuple[SCP, ...]:
    selected = {owner, *(v.target for v in policy.descendants)}
    selected.update(document.entity(key).parent for key in tuple(selected))
    return tuple(snapshot(document.entity(key)) for key in sorted(selected - {""}))


def effective(attachment: Any, override: Any) -> Any:
    changes = {}
    for source, target in (
        ("parent_anchor", "parent_mode"),
        ("child_anchor", "child_mode"),
        ("strategy", "strategy"),
    ):
        value = getattr(override, source)
        if value != "KEEP":
            changes[target] = value
    if override.follow_rotation != "KEEP":
        changes["follow_rotation"] = override.follow_rotation == "ENABLED"
    return replace(attachment, **changes)


def compute(engine: Any, context: ShortcutEdit, meshes: Any, cancel: Any) -> ShortcutEdit:
    records, bindings = {item.id: item for item in context.opening}, []
    for override in context.policy.descendants:
        if cancel.is_set():
            raise ValueError("Shortcut attachment capture cancelled.")
        bindings.append(capture_override(engine, records, override, meshes, cancel.handle))
    anchor = capture_owner(engine, records, context, meshes)
    return replace(
        context, opening=(), bindings=tuple(bindings), anchor=anchor, status="ready", error=""
    )


def capture_override(
    engine: Any, records: Any, override: Any, meshes: Any, cancel: int
) -> OverrideBinding:
    original = records[override.target]
    child = replace(original, attachment=effective(original.attachment, override))
    if not child.parent:
        raise ValueError("A shortcut descendant override requires an anatomical parent.")
    fields = ("parent_mode", "child_mode", "strategy")
    if any(
        getattr(original.attachment, field) != getattr(child.attachment, field) for field in fields
    ):
        child = attachments.capture(engine, child, records[child.parent], meshes, cancel)
    if not child.attachment.binding:
        raise ValueError("Capture the descendant attachment before applying shortcut overrides.")
    return OverrideBinding(child.id, child.attachment)


def capture_owner(
    engine: Any, records: Any, context: ShortcutEdit, meshes: Any
) -> OwnerAnchor | None:
    owner = records[context.owner]
    if not context.policy.backsolve or not owner.parent:
        return None
    return OwnerAnchor(*shortcut_attachments.capture(engine, owner, records[owner.parent], meshes))
