"""Material proof for related variant construction, not vertex-count similarity."""

from typing import Any

from anthroforge.core import graph_records
from anthroforge.core.entities import SCP
from anthroforge.core.results import geometry_asset
from anthroforge.core.tissues import TissueVCP
from anthroforge.native import topology

from . import curve_sources, field_domains, primitive_operations


def verified(context: Any, old: Any, new: Any, mapping: Any) -> bool:
    a, b = geometry_asset(old) if old else "", geometry_asset(new)
    if not a or not b:
        return not a and not b
    if a == b:
        return True
    first, second = context.assets[a].mesh, context.assets[b].mesh
    if topology.same_content(first, second, context.cancel.handle):
        return True
    if not topology.same_topology(first, second, context.cancel.handle):
        return False
    if field_domains.mesh_domain(first) != field_domains.mesh_domain(second):
        return False
    return lineage(context, old, new, mapping)


def lineage(context: Any, old: Any, new: Any, mapping: Any) -> bool:
    if isinstance(old, SCP) and isinstance(new, SCP):
        return primitive(context, old, new, mapping)
    if isinstance(old, TissueVCP) and isinstance(new, TissueVCP):
        material = graph_records.rewritten(new.final_material, mapping)
        return (
            old.final_material is not None
            and material is not None
            and (
                old.source == mapping.get(new.source, new.source)
                and old.final_material.base_state == material.base_state
            )
        )
    return False


def primitive(context: Any, old: Any, new: Any, mapping: Any) -> bool:
    a, b = old.primitive, new.primitive
    if not a or not b or a.kind != b.kind:
        return False
    if a.kind == "IMPORTED":
        return topology.same_content(
            context.assets[a.source].mesh, context.assets[b.source].mesh, context.cancel.handle
        )
    first = curve_sources.resolve(context.engine, context.baseline, old)
    second = curve_sources.resolve(context.engine, context.document, new)
    mapped = graph_records.rewritten(second, mapping)
    signature = primitive_operations.topology_signature
    return signature(first) == signature(mapped)
