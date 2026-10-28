"""Verified authored lineage and native connectivity, never name/count-based correspondence."""

from typing import Any

from anthroforge.core import graph_records
from anthroforge.core.results import geometry_asset
from anthroforge.native import topology

from . import curve_sources, primitive_operations, skeleton_matching


def identities(source: Any, destination: Any) -> dict[str, str]:
    indexed: dict[Any, set[str]] = {}
    for key in owned(destination):
        for origin in skeleton_matching.origins(destination, key):
            indexed.setdefault(origin, set()).add(key)
    found = {}
    for key in owned(source):
        matches = set().union(
            *(indexed.get(o, set()) for o in skeleton_matching.origins(source, key))
        )
        if len(matches) == 1:
            found[key] = next(iter(matches))
    return found


def owned(document: Any) -> set[str]:
    rows = (*document.entities, *document.objects, *document.controls, *document.driving_shortcuts)
    return set().union(*(graph_records.owned(row) for row in rows))


def material(context: Any, p: Any, before: Any, after: Any, original: Any) -> bool:
    first, second = geometry_asset(before), geometry_asset(after)
    if not first or not second:
        return not first and not second
    a, b = context.assets[first].mesh, context.assets[second].mesh
    cancel = context.cancel.handle
    if topology.same_content(a, b, cancel):
        return True
    if not topology.same_topology(a, b, cancel):
        return False
    return construction_lineage(context, p, before, original)


def construction_lineage(context: Any, p: Any, before: Any, original: Any) -> bool:
    a, b = before.primitive, original.primitive
    if a is None or b is None or a.kind != b.kind:
        return False
    if a.kind == "IMPORTED":
        first, second = context.assets[a.source], context.assets[p.assets[b.source]]
        return topology.same_content(first.mesh, second.mesh, context.cancel.handle)
    return generated_lineage(context, p, before, original)


def generated_lineage(context: Any, p: Any, before: Any, original: Any) -> bool:
    mapping = identities(p.source.document, context.baseline)
    if mapping.get(original.id) != before.id:
        return False
    old = curve_sources.resolve(context.engine, context.baseline, before)
    new = curve_sources.resolve(context.engine, p.source.document, original)
    mapped = graph_records.rewritten(new, mapping)
    return primitive_operations.topology_signature(old) == primitive_operations.topology_signature(
        mapped
    )


def property_identities(p: Any) -> dict[str, str]:
    verified = identities(p.source.document, p.destination)
    return {old: p.ids[key] for key, old in verified.items() if key in p.ids}
