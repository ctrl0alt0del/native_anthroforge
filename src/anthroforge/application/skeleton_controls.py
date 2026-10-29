"""Retain destination controls; changes of target or formula authority require explicit review."""

from dataclasses import replace
from typing import Any

from anthroforge.core import graph_records
from anthroforge.core import numeric_properties as numeric
from anthroforge.core.shortcuts import implicit_identity
from anthroforge.core.skeleton_update import Finding

from . import property_catalog, shortcut_ownership, skeleton_correspondence
from .assembly_mapping import property_signature


def reconcile(context: Any, p: Any, options: Any) -> None:
    mapping = skeleton_correspondence.property_identities(p)
    wrappers = [wrapper(context, s, mapping, options) for s in context.baseline.shortcuts]
    drivers = tuple(
        driver(context, d, mapping, options) for d in context.document.driving_shortcuts
    )
    context.document = replace(
        context.document,
        shortcuts=tuple(s for s in wrappers if s is not None),
        driving_shortcuts=drivers,
    )
    remap_order(context, wrappers)


def remap_order(context: Any, wrappers: Any) -> None:
    order = {a.id: b.id for a, b in zip(context.baseline.shortcuts, wrappers, strict=True) if b}
    context.document = replace(
        context.document,
        shortcut_order=tuple(order.get(k, k) for k in context.baseline.shortcut_order),
    )


def wrapper(context: Any, item: Any, mapping: Any, options: Any) -> Any:
    if item.id in options.get("remove_shortcuts", ()):
        decision(context, "shortcut:" + item.id, item.id, "Remove this unavailable shortcut.")
        return None
    reference = mapped_reference(context, item.reference, mapping, options)
    return replace(item, reference=reference)


def driver(context: Any, item: Any, mapping: Any, options: Any) -> Any:
    original = {d.id for d in context.baseline.driving_shortcuts}
    if item.id not in original:
        mapping = {}
    formulas = tuple(formula(context, f, mapping, options) for f in item.formulas)
    return replace(
        item, formulas=formulas, generation=item.generation + int(formulas != item.formulas)
    )


def formula(context: Any, item: Any, mapping: Any, options: Any) -> Any:
    if item.id in options.get("disable_formulas", ()):
        decision(
            context, "disable:" + item.id, item.id, "Disable formula; retain replacement value."
        )
        return replace(item, enabled=False)
    if not item.enabled:
        return item
    target = mapped_reference(context, item.target, mapping, options)
    inputs = tuple(mapped_input(context, i, mapping, options) for i in item.inputs)
    return replace(item, target=target, inputs=inputs)


def mapped_input(context: Any, item: Any, mapping: Any, options: Any) -> Any:
    if item.property is None:
        return item
    return replace(item, property=mapped_reference(context, item.property, mapping, options))


def mapped_reference(context: Any, old: Any, mapping: Any, options: Any) -> Any:
    key = implicit_identity(old)
    explicit = options.get("property_mappings", {}).get(key)
    selected = (
        numeric.decode_reference(explicit) if explicit else graph_records.rewritten(old, mapping)
    )
    if selected == old and old.target not in context.fixed_poses:
        return old
    return reviewed_reference(context, old, selected, bool(explicit))


def reviewed_reference(context: Any, old: Any, selected: Any, explicit: bool) -> Any:
    key = implicit_identity(old)
    try:
        validate_reference(context, old, selected, explicit)
    except ValueError as error:
        context.findings.append(
            Finding("property:" + key, old.target, str(error), blocking=True, kind="property")
        )
        return old
    if explicit:
        decision(context, "property:" + key, old.target, "Use the selected replacement property.")
    return selected


def validate_reference(context: Any, old: Any, selected: Any, explicit: bool) -> None:
    current = property_catalog.resolve(context.document, selected)
    if old.target not in context.baseline.registry.records:
        return
    previous = property_catalog.resolve(context.baseline, old)
    if property_signature(previous) != property_signature(current):
        raise ValueError(
            "Choose a property with matching type, units and components, or disable this control."
        )
    owners = shortcut_ownership.property_owners(context.baseline, old.target)
    if selected != old and not explicit and owners - context.fixed_poses:
        raise ValueError(
            "Construction has other consumers; choose which property this control will edit."
        )


def decision(context: Any, key: str, owner: str, message: str) -> None:
    context.findings.append(Finding(key, owner, message, acknowledge=True, kind="property"))
