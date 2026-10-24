"""Resolve hierarchy rules and required construction without extra authored nodes."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from . import attachment_references
from .deformer_references import sources as deformer_sources
from .entities import SCP
from .mirroring import MirrorInstance, MirrorRule
from .reference_images import ReferenceImage
from .tissues import TissueVCP


@dataclass(frozen=True, slots=True)
class MirrorIndex:
    signature: tuple[Any, ...]
    instances: Mapping[str, MirrorInstance]
    rules: Mapping[str, MirrorRule]
    conflicts: tuple[str, ...] = ()


def dependencies(item: Any) -> frozenset[str]:
    definition = getattr(item, "primitive", None) or item
    refs = {u.curve for u in getattr(definition, "curves", ())}
    refs.update(getattr(item, "owners", ()))
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
    return document.mirror_rules, topology


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
    return MirrorIndex(key, MappingProxyType(instances), MappingProxyType(settings), conflicts)


def validated_settings(document: Any) -> dict[str, MirrorRule]:
    settings = {r.target: r for r in document.mirror_rules}
    unknown = settings.keys() - document.registry.records.keys()
    if len(settings) != len(document.mirror_rules) or unknown:
        raise ValueError("Mirror rules require unique existing authored targets.")
    if any(r.enabled and r.target not in document.registry.anatomy for r in settings.values()):
        raise ValueError("Mirror Children requires an anatomical source.")
    return settings


def empty(previous: MirrorIndex | None) -> MirrorIndex:
    if previous is not None and not previous.signature:
        return previous
    return MirrorIndex((), MappingProxyType({}), MappingProxyType({}))


def anatomy_rules(document: Any, settings: dict[str, MirrorRule]) -> dict[str, set[str]]:
    resolved: dict[str, set[str]] = {}
    sources: dict[str, str] = {}
    for key in document.index.structure.order:
        item = document.entity(key)
        rule = settings.get(key, MirrorRule(key))
        inherited = sources.get(item.parent, "") if rule.inherit else ""
        sources[key] = key if rule.enabled else inherited
        resolved[key] = {inherited} if inherited and not rule.enabled else set()
    return resolved


def construction_rules(document: Any, settings: Any, resolved: Any) -> tuple[Any, tuple[str, ...]]:
    records = document.registry.records
    for _ in range(len(records) + 1):
        changed = propagate(records, settings, resolved)
        if not changed:
            break
    conflicts = incompatible(records, settings, resolved)
    for target in conflicts:
        resolved[target] = set()
    return resolved, conflicts


def propagate(records: Any, settings: Any, resolved: Any) -> bool:
    changed = False
    for key, item in records.items():
        if isinstance(item, ReferenceImage):
            continue
        choices = inherited_choices(item, settings, resolved) if not isinstance(item, SCP) else set()
        for ref in required(item):
            choices_for_ref = resolved.get(key, set())
            changed |= merge(ref, choices_for_ref, settings, resolved)
        if not isinstance(item, SCP):
            changed |= merge(key, choices, settings, resolved)
    return changed


def inherited_choices(item: Any, settings: Any, resolved: Any) -> set[str]:
    return set().union(*(
        {ref} if ref in settings and settings[ref].enabled else resolved.get(ref, set())
        for ref in dependencies(item)
    ))


def merge(key: str, choices: set[str], settings: Any, resolved: Any) -> bool:
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
