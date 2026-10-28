"""Import boundaries retain source reflection rules without manufacturing hierarchy nodes."""

from dataclasses import replace
from typing import Any, cast
from uuid import uuid4

from anthroforge.core import graph_records
from anthroforge.core.mirror_resolution import dependencies
from anthroforge.core.mirroring import MirrorRule

from . import assembly_graph


def required(document: Any, selection: Any) -> set[str]:
    found = {v.rule for v in document.mirrors.instances.values() if v.source in selection.records}
    found |= {r.target for r in document.mirror_rules if r.target in selection.records}
    found |= {
        ref.target
        for item in assembly_graph.records(selection)
        for ref in graph_records.references(item)
        if ref.relationship == "mirror"
    }
    return found & set(document.mirrors.rules)


def allocate(document: Any, selection: Any, identities: dict[str, str]) -> None:
    for key in required(document, selection):
        identities.setdefault(key, str(uuid4()))


def copy(document: Any, selection: Any, identities: Any) -> tuple[Any, ...]:
    copied = {}
    for key in required(document, selection):
        rule = document.mirrors.rules[key]
        updated = imported_rule(document, selection, rule, identities)
        copied[updated.target] = updated
    prevent_new_inheritance(document, selection, identities, copied)
    return tuple(copied.values())


def imported_rule(document: Any, selection: Any, rule: MirrorRule, ids: Any) -> MirrorRule:
    if not rule.scope and rule.target in selection.records:
        return cast(MirrorRule, graph_records.rewritten(rule, ids))
    members = {
        v.source
        for v in document.mirrors.instances.values()
        if v.rule == rule.target and v.source in selection.records
    }
    members |= plane_consumers(selection, rule.target)
    return replace(
        rule, target=ids[rule.target], enabled=True, scope=tuple(ids[k] for k in sorted(members))
    )


def plane_consumers(selection: Any, rule: str) -> set[str]:
    return {
        item.id
        for item in selection.records.values()
        if any(
            ref.relationship == "mirror" and ref.target == rule
            for ref in graph_records.references(item)
        )
    }


def prevent_new_inheritance(document: Any, selection: Any, ids: Any, rules: Any) -> None:
    mirrored = {v.source for v in document.mirrors.instances.values()}
    roots = set(assembly_graph.roots(selection))
    external = {
        key
        for key, value in selection.records.items()
        if dependencies(value) - selection.records.keys()
    }
    for key in roots | (external - mirrored):
        target = ids[key]
        current = rules.get(target, MirrorRule(target))
        rules[target] = replace(current, inherit=False)


def shared(document: Any, identities: Any) -> tuple[Any, ...]:
    return tuple(
        graph_records.rewritten(row, identities)
        for row in document.shared_mirror_targets
        if row.source in identities
    )
