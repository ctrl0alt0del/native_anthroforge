"""Numerical operations use the same semantic installation paths as ordinary tools."""

from dataclasses import asdict
from typing import Any

from anthroforge.core import numeric_properties as numeric

from . import property_catalog


def discover(session: Any, target: str = "", search: str = "") -> list[dict[str, Any]]:
    items = (
        (session.document.object(target),) if target else session.document.registry.records.values()
    )
    return [
        describe(session, descriptor)
        for item in items
        for descriptor in property_catalog.descriptors(item)
        if search.casefold() in (item.name + " " + descriptor.label).casefold()
    ]


def describe(session: Any, descriptor: numeric.NumericDescriptor) -> dict[str, Any]:
    from .property_guards import driven
    from .shortcut_ownership import property_owners

    reference = descriptor.reference
    return dict(
        asdict(descriptor),
        value=read(session, reference),
        owners=sorted(property_owners(session.document, reference.target)),
        driven_by=driven(session.document, reference),
    )


def get(session: Any, reference: dict[str, Any]) -> dict[str, Any]:
    return describe(
        session, property_catalog.resolve(session.document, numeric.decode_reference(reference))
    )


def read(session: Any, reference: numeric.PropertyRef, item: Any = None) -> Any:
    if reference.path[0] in ("transform", "world_transform"):
        from .property_transforms import read as transform_read

        return transform_read(session, reference, item)
    return numeric.read(item or session.document.object(reference.target), reference)


def set_value(session: Any, reference: dict[str, Any], value: Any, uniform: bool = False) -> None:
    selected = property_catalog.resolve(session.document, numeric.decode_reference(reference))
    if uniform and selected.reference.component is None and selected.components > 1:
        value = (value,) * selected.components
    write(session, ((selected.reference, selected.validate(value)),))


def write(session: Any, updates: tuple[tuple[numeric.PropertyRef, Any], ...]) -> None:
    from .property_writes import install, prepare

    grouped: dict[str, list[tuple[numeric.PropertyRef, Any]]] = {}
    for reference, value in updates:
        descriptor = property_catalog.resolve(session.document, reference)
        if not descriptor.writable:
            raise ValueError(descriptor.reason or "This numerical property is read-only.")
        grouped.setdefault(reference.target, []).append((reference, descriptor.validate(value)))
    candidates = [prepare(session, key, tuple(values)) for key, values in grouped.items()]
    for before, after in candidates:
        install(session, before, after)
