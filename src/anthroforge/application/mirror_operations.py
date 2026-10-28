"""Shared mirroring operations; sources are the only editable geometry owners."""

from dataclasses import asdict, replace
from typing import Any, cast

from anthroforge.core.mirroring import MirrorRule, SharedMirrorTarget, parse, require_source

from . import mirror_junctions, mirror_policy, workspace_policy


def queries(session: Any) -> dict[str, Any]:
    from .mirror_bindings import inspect as bindings

    return {
        "mirror.attachment.inspect": lambda **a: bindings(session, **a),
        "mirror.list": lambda **a: listing(session, **a),
        "mirror.inspect": lambda **a: inspect(session, **a),
        "mirror.source": lambda **a: source(session, **a),
        "mirror.removal.inspect": lambda **a: removal(session, **a),
        "mirror.attachment.shared": lambda **a: shared(session, **a),
        "mirror.planes": lambda: planes(session),
        "mirror.source.removal.inspect": lambda target: mirror_policy.removing(
            session.document, target
        ),
    }


def planes(session: Any) -> list[dict[str, Any]]:
    return [
        dict(asdict(rule), name=plane_name(session.document, rule))
        for rule in session.document.mirror_rules
        if rule.enabled or rule.override
    ]


def plane_name(document: Any, rule: MirrorRule) -> str:
    if rule.scope:
        return "Imported · " + str(document.object(rule.scope[0]).name)
    return str(document.object(rule.target).name)


def configure(session: Any, target: str, **values: Any) -> None:
    old = editable_rule(session, target)
    if set(values) & {"scope", "target"}:
        raise ValueError("Mirror ownership is managed through the source graph.")
    if values.get("enabled") and not old.scope and target not in session.document.registry.anatomy:
        raise ValueError("Mirror Children requires an anatomical source.")
    updated = replace(old, **values)
    if updated == old:
        return
    rules = tuple(r for r in session.document.mirror_rules if r.target != target)
    session.replace_document(mirror_rules=(*rules, updated))
    invalidate(session, target)


def editable_rule(session: Any, target: str) -> MirrorRule:
    require_source(target)
    old = session.document.mirrors.rules.get(target, MirrorRule(target))
    sources = old.scope or (target,)
    for key in sources:
        session.document.object(key)
    if not any(
        workspace_policy.included(session.document, session.workspace, key) for key in sources
    ):
        raise ValueError("The source is outside the focused workspace.")
    return cast(MirrorRule, old)


def invalidate(session: Any, target: str) -> None:
    from anthroforge.core.results import Port

    from . import dependent_tasks, scp_surface_parents

    ports = {Port(target, "mirror")}
    session.scheduler.invalidate_ports(ports)
    scp_surface_parents.invalidate(session, ports)
    dependent_tasks.changed(session, ports, published=False)


def listing(session: Any, source: str = "") -> list[dict[str, Any]]:
    document = session.document
    return [
        describe(document, instance)
        for instance in document.mirrors.instances.values()
        if not source or instance.source == source
    ]


def describe(document: Any, instance: Any) -> dict[str, Any]:
    item = document.object(instance.source)
    rule = document.mirrors.plane(instance)
    return dict(
        id=instance.id,
        source=instance.source,
        rule=instance.rule,
        name=item.name,
        readonly=True,
        axis=rule.axis,
        shift=rule.shift,
        source_revision=getattr(item, "result_generation", item.result.revision),
        junctions=mirror_junctions.describe(document, instance),
    )


def inspect(session: Any, target: str) -> dict[str, Any]:
    instance = session.document.mirrors.instances.get(target)
    if instance:
        return describe(session.document, instance)
    require_source(target)
    rule = session.document.mirrors.rules.get(target, MirrorRule(target))
    if not rule.scope:
        session.document.object(target)
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
    from .mirror_bindings import references

    require_source(source)
    if type(enabled) is not bool:
        raise ValueError("Target sharing requires a Boolean choice.")
    if not workspace_policy.included(session.document, session.workspace, source):
        raise ValueError("The source is outside the focused workspace.")
    if binding not in {key for key, _ in references(session.document.object(source))}:
        raise ValueError("Choose an existing anatomical binding on the source.")
    pair = SharedMirrorTarget(source, binding)
    existing = tuple(v for v in session.document.shared_mirror_targets if v != pair)
    session.replace_document(shared_mirror_targets=(*existing, pair) if enabled else existing)


def shared(session: Any, source: str, binding: str) -> bool:
    return SharedMirrorTarget(source, binding) in session.document.shared_mirror_targets


def source(session: Any, target: str) -> str:
    instance = parse(target)
    if instance is None or target not in session.document.mirrors.instances:
        raise ValueError("Choose an existing mirrored instance.")
    return instance.source
