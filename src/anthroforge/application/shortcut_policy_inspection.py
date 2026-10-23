"""Describe prospective policy and captured effective bindings without recapture."""

from dataclasses import asdict, replace
from typing import Any

from . import attachment_inspection, shortcut_effects, shortcut_ownership


def inspect(session: Any, shortcut: str) -> dict[str, Any]:
    value = shortcut_effects.selected(session, shortcut)
    scope = shortcut_ownership.attachment_scope(session.document, value)
    context = captured(session, shortcut)
    targets = {p.target for p in value.policy.descendants} | ({scope} if scope else set())
    return dict(
        shortcut=shortcut,
        revision=session.document.revision,
        scope=scope,
        policy=asdict(value.policy),
        captured=bool(context and context.status == "ready"),
        context=context.id if context else "",
        error=context.error if context else "",
        rows=[row(session, value, context, key) for key in sorted(targets)],
    )


def captured(session: Any, shortcut: str) -> Any:
    return next(
        (c for c in reversed(session.document.shortcut_edits) if c.shortcut == shortcut), None
    )


def captured_binding(context: Any, target: str) -> Any:
    return next((b for b in context.bindings if b.target == target), None) if context else None


def row(session: Any, value: Any, context: Any, key: str) -> dict[str, Any]:
    item = session.document.entity(key)
    override = next((p for p in value.policy.descendants if p.target == key), None)
    binding = captured_binding(context, key)
    return dict(
        target=key,
        name=item.name,
        authored=asdict(item.attachment),
        override=asdict(override) if override else None,
        effective=asdict(binding.attachment) if binding else None,
        anchor=owner_anchor(context, key),
        binding_available=bool(item.attachment.binding),
        result_revision=item.result.revision,
        pose_revision=item.pose_revision,
    )


def owner_anchor(context: Any, key: str) -> Any:
    return asdict(context.anchor) if context and key == context.owner and context.anchor else None


def anchors(session: Any, shortcut: str) -> dict[str, Any]:
    policy = inspect(session, shortcut)
    context = captured(session, shortcut)
    for item in policy["rows"]:
        source = session.document.entity(item["target"])
        item["authored_anchors"] = attachment_inspection.describe(session, source)["anchors"]
        binding = captured_binding(context, source.id)
        item["effective_anchors"] = effective_anchors(session, source, binding)
    return policy


def effective_anchors(session: Any, source: Any, binding: Any) -> Any:
    if binding is None:
        return None
    item = replace(source, attachment=binding.attachment)
    return attachment_inspection.describe(session, item)["anchors"]
