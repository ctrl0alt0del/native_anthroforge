"""Preserve a consumer's controls when its internal construction identities change."""

from dataclasses import replace
from typing import Any

from .shortcut_copies import reference


def rewritten(document: Any, mapping: dict[str, str], targets: frozenset[str]) -> dict[str, Any]:
    scoped = {**mapping, **{key: key for key in targets}}
    wrappers = tuple(
        replace(s, reference=selected_reference(s.reference, scoped, targets))
        for s in document.shortcuts
    )
    drivers = tuple(driver(d, scoped, targets) for d in document.driving_shortcuts)
    order = {a.id: b.id for a, b in zip(document.shortcuts, wrappers, strict=True)}
    return dict(
        shortcuts=wrappers,
        driving_shortcuts=drivers,
        formula_results=document.formula_results,
        shortcut_order=tuple(order.get(key, key) for key in document.shortcut_order),
    )


def selected_reference(value: Any, mapping: dict[str, str], targets: frozenset[str]) -> Any:
    return reference(value, mapping) if value.target in targets else value


def driver(value: Any, mapping: dict[str, str], targets: frozenset[str]) -> Any:
    formulas = tuple(formula(f, mapping, targets) for f in value.formulas)
    return replace(
        value, formulas=formulas, generation=value.generation + int(formulas != value.formulas)
    )


def formula(value: Any, mapping: dict[str, str], targets: frozenset[str]) -> Any:
    return replace(
        value,
        target=selected_reference(value.target, mapping, targets),
        inputs=tuple(formula_input(i, mapping, targets) for i in value.inputs),
    )


def formula_input(value: Any, mapping: dict[str, str], targets: frozenset[str]) -> Any:
    if value.property is None:
        return value
    return replace(value, property=selected_reference(value.property, mapping, targets))
