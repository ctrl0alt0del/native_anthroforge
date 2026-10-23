"""Copy shortcut definitions with the construction identities that own their outputs."""

from dataclasses import replace
from typing import Any
from uuid import uuid4

from anthroforge.core.numeric_properties import PropertyRef


def state(
    document: Any, mapping: dict[str, str], rewired: frozenset[str] = frozenset()
) -> dict[str, Any]:
    from .shortcut_references import rewritten

    selected = drivers(document, mapping)
    identities = control_identities(selected, mapping)
    additions = records(document, selected, identities)
    original = rewritten(document, mapping, rewired)
    return {name: (*original[name], *values) for name, values in additions.items()}


def records(document: Any, selected: tuple[Any, ...], identities: dict[str, str]) -> dict[str, Any]:
    wrappers = tuple(
        wrapper(s, identities) for s in document.shortcuts if s.reference.target in identities
    )
    copied = tuple(driver(d, identities) for d in selected)
    order = copied_order(document, wrappers, identities)
    return dict(
        shortcuts=wrappers,
        driving_shortcuts=copied,
        formula_results=results(document, identities),
        shortcut_order=order,
    )


def drivers(document: Any, mapping: dict[str, str]) -> tuple[Any, ...]:
    return tuple(
        replace(d, formulas=selected)
        for d in document.driving_shortcuts
        if (selected := tuple(f for f in d.formulas if f.target.target in mapping))
    )


def control_identities(selected: tuple[Any, ...], mapping: dict[str, str]) -> dict[str, str]:
    keys = {d.id for d in selected} | {f.id for d in selected for f in d.formulas}
    return {**mapping, **{key: str(uuid4()) for key in keys}}


def reference(value: PropertyRef, mapping: dict[str, str]) -> PropertyRef:
    if value.target not in mapping:
        return value
    path = tuple(
        "@" + mapping.get(token[1:], token[1:]) if token.startswith("@") else token
        for token in value.path
    )
    return replace(value, target=mapping[value.target], path=path)


def policy(value: Any, mapping: dict[str, str]) -> Any:
    return replace(
        value,
        scope=mapping.get(value.scope, value.scope),
        descendants=tuple(
            replace(p, target=mapping.get(p.target, p.target)) for p in value.descendants
        ),
    )


def wrapper(value: Any, mapping: dict[str, str]) -> Any:
    return replace(
        value, reference=reference(value.reference, mapping), policy=policy(value.policy, mapping)
    )


def driver(value: Any, mapping: dict[str, str]) -> Any:
    return replace(
        value,
        id=mapping[value.id],
        formulas=tuple(formula(f, mapping) for f in value.formulas),
        policy=policy(value.policy, mapping),
    )


def formula(value: Any, mapping: dict[str, str]) -> Any:
    return replace(
        value,
        id=mapping[value.id],
        target=reference(value.target, mapping),
        inputs=tuple(formula_input(i, mapping) for i in value.inputs),
    )


def formula_input(value: Any, mapping: dict[str, str]) -> Any:
    return replace(
        value,
        property=reference(value.property, mapping) if value.property else None,
        driver=mapping.get(value.driver, value.driver),
    )


def results(document: Any, mapping: dict[str, str]) -> tuple[Any, ...]:
    from .construction_copy import remap_inputs

    return tuple(
        replace(
            row,
            formula=mapping[row.formula],
            inputs=remap_inputs(row.inputs, mapping),
            pending=tuple(mapping.get(key, key) for key in row.pending),
        )
        for row in document.formula_results
        if row.formula in mapping
    )


def copied_order(
    document: Any, wrappers: tuple[Any, ...], mapping: dict[str, str]
) -> tuple[str, ...]:
    from .shortcut_operations import ordered

    source = tuple(s for s in document.shortcuts if s.reference.target in mapping)
    identities = {**mapping, **{old.id: new.id for old, new in zip(source, wrappers, strict=True)}}
    return tuple(identities[v.id] for v in ordered(document) if v.id in identities)
