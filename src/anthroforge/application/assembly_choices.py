"""Searchable mapping candidates; labels aid search, never establish correspondence."""

from dataclasses import asdict
from typing import Any

from anthroforge.core import anatomical_surfaces
from anthroforge.core.object_registry import kind

from . import assembly_mapping, property_catalog


def targets(document: Any, row: Any) -> list[dict[str, Any]]:
    found = []
    for item in document.registry.records.values():
        if eligible(document, item, row):
            found.append(dict(key=item.id, target=item.id, name=item.name, instance=""))
    return found + mirrored_targets(document, row)


def mirrored_targets(document: Any, row: Any) -> list[dict[str, Any]]:
    found = []
    if row.get("role"):
        for instance in document.mirrors.instances.values():
            item = document.object(instance.source)
            if eligible(document, item, row):
                found.append(
                    dict(
                        key=instance.id,
                        target=item.id,
                        instance=instance.rule,
                        name=item.name + " · mirrored",
                    )
                )
    return found


def eligible(document: Any, item: Any, row: Any) -> bool:
    if row.get("property"):
        return True
    if row.get("role"):
        return row["role"] in anatomical_surfaces.roles(item, document.registry.records)
    if row.get("relationship") == "parent":
        return kind(item) != "IMAGE"
    if row.get("relationship") in ("association", "policy", "stacking"):
        return item.id in document.registry.anatomy
    return bool(kind(item) == row["kind"])


def properties(source: Any, destination: Any, row: Any, target: str) -> list[dict[str, Any]]:
    from anthroforge.core.numeric_properties import decode_reference

    reference = decode_reference(row["property"])
    expected = assembly_mapping.property_details(source, reference)
    signature = tuple(expected[k] for k in ("numeric_type", "dimension", "components"))
    return [
        dict(name=d.label, property=asdict(d.reference))
        for d in property_catalog.descriptors(destination.object(target))
        if assembly_mapping.property_signature(d) == signature
    ]


def suggestions(source: Any, document: Any, rows: Any) -> dict[str, str]:
    matches: dict[str, set[str]] = {}
    for imported in document.imports:
        if imported.source_document == str(source.id):
            for original, copied in imported.identities:
                if copied in document.registry.records:
                    matches.setdefault(original, set()).add(copied)
    return {
        r["key"]: next(iter(matches[r["source"]]))
        for r in rows
        if len(matches.get(r["source"], ())) == 1
    }
