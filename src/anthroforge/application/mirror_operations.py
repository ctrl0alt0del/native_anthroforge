"""Shared mirroring operations; sources are the only editable geometry owners."""

from dataclasses import asdict, replace
from typing import Any

from anthroforge.core.mirroring import MirrorRule, SharedMirrorTarget, parse, require_source

from . import mirror_policy, workspace_policy


def configure(session: Any, target: str, **values: Any) -> None:
    require_source(target)
    item = session.document.object(target)
    if not workspace_policy.included(session.document, session.workspace, target):
        raise ValueError("The source is outside the focused workspace.")
    if values.get("enabled") and target not in session.document.registry.anatomy:
        raise ValueError("Mirror Children belongs to anatomical sources, not individual construction.")
    old = session.document.mirrors.rules.get(target, MirrorRule(target))
    updated = replace(old, **values)
    rules = tuple(r for r in session.document.mirror_rules if r.target != item.id)
    session.replace_document(mirror_rules=(*rules, updated))


def listing(session: Any, source: str = "") -> list[dict[str, Any]]:
    document = session.document
    return [
        describe(document, instance) for instance in document.mirrors.instances.values()
        if not source or instance.source == source
    ]


def describe(document: Any, instance: Any) -> dict[str, Any]:
    item = document.object(instance.source)
    rule = document.mirrors.rules[instance.rule]
    return dict(
        id=instance.id, source=instance.source, rule=instance.rule,
        name=item.name, readonly=True, axis=rule.axis, shift=rule.shift,
        source_revision=getattr(item, "result_generation", item.result.revision),
    )


def inspect(session: Any, target: str) -> dict[str, Any]:
    instance = session.document.mirrors.instances.get(target)
    if instance:
        return describe(session.document, instance)
    require_source(target)
    session.document.object(target)
    rule = session.document.mirrors.rules.get(target, MirrorRule(target))
    return dict(rule=asdict(rule), instances=listing(session, target))


def removal(session: Any, target: str, **values: Any) -> list[dict[str, str]]:
    document = session.document
    old = document.mirrors.rules.get(target, MirrorRule(target))
    rule = replace(old, **values)
    rules = tuple(r for r in document.mirror_rules if r.target != target)
    candidate = replace(document, mirror_rules=(*rules, rule))
    removed = document.mirrors.instances.keys() - candidate.mirrors.instances.keys()
    return mirror_policy.blockers(document, removed)


def share_target(session: Any, source: str, binding: str, enabled: bool = True) -> None:
    require_source(source)
    session.document.object(source)
    pair = SharedMirrorTarget(source, binding)
    existing = tuple(v for v in session.document.shared_mirror_targets if v != pair)
    session.replace_document(shared_mirror_targets=(*existing, pair) if enabled else existing)


def source(session: Any, target: str) -> str:
    instance = parse(target)
    if instance is None or target not in session.document.mirrors.instances:
        raise ValueError("Choose an existing mirrored instance.")
    return instance.source
