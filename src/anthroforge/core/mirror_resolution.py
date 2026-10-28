"""Resolve hierarchy rules and required construction without extra authored nodes."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from . import attachment_references
from .entities import SCP
from .junctions import members
from .mirroring import MirrorInstance, MirrorRule
from .reference_images import ReferenceImage
from .tissues import TissueVCP


@dataclass(frozen=True, slots=True)
class MirrorIndex:
    signature: tuple[Any, ...]
    instances: Mapping[str, MirrorInstance]
    rules: Mapping[str, MirrorRule]
    conflicts: tuple[str, ...] = ()
    placements: Mapping[str, MirrorRule] = field(default_factory=dict)
    junctions: Mapping[str, tuple[Any, ...]] = field(default_factory=dict)

    def plane(self, instance: Any) -> MirrorRule:
        return self.placements.get(instance.id, self.rules[instance.rule])


def dependencies(item: Any) -> frozenset[str]:
    definition = getattr(item, "primitive", None) or item
    refs = {u.curve for u in getattr(definition, "curves", ())}
    refs.update(attachment_references.targets(item))
    if isinstance(item, TissueVCP):
        refs.add(item.source)
    return frozenset(refs)


def required(item: Any) -> frozenset[str]:
    definition = getattr(item, "primitive", None) or item
    refs = {u.curve for u in getattr(definition, "curves", ())}
    if isinstance(item, TissueVCP):
        refs.add(item.source)
    for binding in getattr(item, "deformers", ()):
        if binding.control:
            refs.add(binding.control)
    return frozenset(refs)


def signature(document: Any) -> tuple[Any, ...]:
    records = document.registry.records
    topology = tuple(
        (
            key,
            getattr(v, "parent", ""),
            dependencies(v),
            required(v),
            bool(getattr(v, "symmetric", None)),
            bool(getattr(v, "mirrored_rows", False)),
        )
        for key, v in records.items()
    )
    groups = tuple(members(document.objects).items()) if document.junctions else ()
    return document.mirror_rules, topology, document.junctions, groups


def build(document: Any, previous: MirrorIndex | None) -> MirrorIndex:
    if not document.mirror_rules:
        return empty(previous)
    key = signature(document)
    if previous is not None and previous.signature == key:
        return previous
    settings = validated_settings(document)
    seeds = anatomy_rules(document, settings)
    resolved, conflicts = construction_rules(document, settings, seeds)
    instances = instance_records(document, resolved)
    placements = retain_conflicts(document, previous, instances, settings, conflicts)
    return frozen_index(key, instances, settings, conflicts, placements)


def frozen_index(
    key: Any, instances: Any, settings: Any, conflicts: Any, placements: Any
) -> MirrorIndex:
    return MirrorIndex(
        key,
        MappingProxyType(instances),
        MappingProxyType(settings),
        conflicts,
        MappingProxyType(placements),
        junction_index(key[-1]),
    )


def junction_index(groups: Any) -> Mapping[str, tuple[Any, ...]]:
    found: dict[str, list[Any]] = {}
    for key, refs in groups:
        for ref in refs:
            found.setdefault(ref.curve, []).append((key, refs))
    return MappingProxyType({key: tuple(values) for key, values in found.items()})


def retain_conflicts(
    document: Any, previous: Any, instances: Any, settings: Any, conflicts: Any
) -> Any:
    placements = {key: settings[v.rule] for key, v in instances.items()}
    if previous is None:
        return placements
    for key, instance in previous.instances.items():
        if instance.source in conflicts and instance.rule in settings:
            instances[key] = instance
            placements[key] = previous.plane(instance)
    return placements


class ResolvedRules(dict[str, MirrorRule]):
    def __init__(self, rules: Any) -> None:
        super().__init__((r.target, r) for r in rules)
        self.boundaries: dict[str, set[str]] = {}
        for rule in rules:
            for key in rule.scope:
                if rule.enabled:
                    self.boundaries.setdefault(key, set()).add(rule.target)


def validated_settings(document: Any) -> ResolvedRules:
    settings = ResolvedRules(document.mirror_rules)
    ordinary = {r.target for r in settings.values() if not r.scope}
    scoped = {key for r in settings.values() for key in r.scope}
    unknown = (ordinary | scoped) - document.registry.records.keys()
    if len(settings) != len(document.mirror_rules) or unknown:
        raise ValueError("Mirror rules require unique existing authored targets.")
    if any(
        r.enabled and not r.scope and r.target not in document.registry.anatomy
        for r in settings.values()
    ):
        raise ValueError("Mirror Children requires an anatomical source.")
    return settings


def empty(previous: MirrorIndex | None) -> MirrorIndex:
    if previous is not None and not previous.signature:
        return previous
    return MirrorIndex((), MappingProxyType({}), MappingProxyType({}))


def anatomy_rules(document: Any, settings: ResolvedRules) -> dict[str, set[str]]:
    resolved = {key: set(value) for key, value in settings.boundaries.items()}
    sources: dict[str, set[str]] = {}
    for key in document.index.structure.order:
        item = document.entity(key)
        rule = settings.get(key, MirrorRule(key))
        inherited = sources.get(item.parent, set()) if rule.inherit else set()
        inherited = settings.boundaries.get(key, inherited)
        sources[key] = {key} if rule.enabled else inherited
        resolved[key] = inherited if inherited and not rule.enabled else set()
    return resolved


def construction_rules(document: Any, settings: Any, resolved: Any) -> tuple[Any, tuple[str, ...]]:
    records = document.registry.records
    groups = members(document.objects).values() if document.junctions else ()
    for _ in range(len(records) + 1):
        changed = propagate(records, settings, resolved)
        changed |= shared_junctions(groups, settings, resolved)
        if not changed:
            break
    conflicts = incompatible(records, settings, resolved)
    for target in conflicts:
        resolved[target] = set()
    return resolved, conflicts


def shared_junctions(groups: Any, settings: Any, resolved: Any) -> bool:
    changed = False
    for group in groups:
        choices = set().union(*(resolved.get(ref.curve, set()) for ref in group))
        for ref in group:
            changed |= merge(ref.curve, choices, settings, resolved)
    return changed


def propagate(records: Any, settings: Any, resolved: Any) -> bool:
    changed = False
    for key, item in records.items():
        if isinstance(item, ReferenceImage):
            continue
        choices = (
            inherited_choices(item, settings, resolved) if not isinstance(item, SCP) else set()
        )
        for ref in required(item):
            choices_for_ref = resolved.get(key, set())
            changed |= merge(ref, choices_for_ref, settings, resolved)
        if not isinstance(item, SCP):
            changed |= merge(key, choices, settings, resolved)
    return changed


def inherited_choices(item: Any, settings: Any, resolved: Any) -> set[str]:
    return set().union(
        *(
            {ref} if ref in settings and settings[ref].enabled else resolved.get(ref, set())
            for ref in dependencies(item)
        )
    )


def merge(key: str, choices: set[str], settings: Any, resolved: Any) -> bool:
    if key in settings.boundaries:
        return False
    rule = settings.get(key, MirrorRule(key))
    if not rule.inherit or rule.enabled:
        return False
    choices = {key} if choices and rule.override else choices
    before = resolved.setdefault(key, set())
    size = len(before)
    before.update(choices)
    return len(before) != size


def incompatible(records: Any, settings: Any, resolved: Any) -> tuple[str, ...]:
    return tuple(
        key
        for key, item in records.items()
        if attachment_references.targets(item)
        and len(resolved.get(key, ())) > 1
        and len({(settings[r].axis, settings[r].shift) for r in resolved[key]}) > 1
    )


def instance_records(document: Any, resolved: Any) -> dict[str, MirrorInstance]:
    output = {}
    for key, item in document.registry.records.items():
        if suppressed(document, item):
            continue
        for rule in sorted(resolved.get(key, ())):
            instance = MirrorInstance(key, rule)
            output[instance.id] = instance
    return output


def suppressed(document: Any, item: Any) -> bool:
    if getattr(item, "symmetric", None) or getattr(item, "mirrored_rows", False):
        return True
    if isinstance(item, TissueVCP):
        return bool(getattr(document.object(item.source), "mirrored_rows", False))
    return isinstance(item, ReferenceImage)
