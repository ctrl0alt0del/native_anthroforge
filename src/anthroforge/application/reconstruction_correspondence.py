"""Material comparison requires construction lineage and the actual sampled domain."""

from typing import Any

from anthroforge.core import graph_records
from anthroforge.core.entities import SCP
from anthroforge.core.tissues import TissueVCP
from anthroforge.native import topology

from . import curve_sources, field_domains, primitive_operations, tissue_inspection_stages


def mapping(view: Any) -> dict[str, str]:
    return {new: old for old, new in view.provenance.get("construction_map", ())}


def verified(first: Any, second: Any, cancel: int) -> bool:
    a, b = first.layers[0], second.layers[0]
    if a.lineage is None or b.lineage is None or first.subject != second.subject:
        return False
    if not topology.same_topology(a.resource, b.resource, cancel):
        return False
    if field_domains.mesh_domain(a.resource) != field_domains.mesh_domain(b.resource):
        return False
    left, right = (v.source.document.object(v.subject) for v in (first, second))
    if isinstance(left, SCP) and isinstance(right, SCP):
        return primitive(first, second, left, right, cancel)
    return isinstance(left, TissueVCP) and isinstance(right, TissueVCP) and tissue(first, second)


def primitive(a: Any, b: Any, left: Any, right: Any, cancel: int) -> bool:
    x, y = left.primitive, right.primitive
    if not x or not y or x.kind != y.kind:
        return False
    if x.kind == "IMPORTED":
        return topology.same_content(
            a.source.assets[x.source].mesh, b.source.assets[y.source].mesh, cancel
        )
    return bool(signature(a, left) == signature(b, right))


def signature(view: Any, item: Any) -> Any:
    primitive = curve_sources.resolve(view.source.engine, view.source.document, item)
    return primitive_operations.topology_signature(
        graph_records.rewritten(primitive, mapping(view))
    )


def tissue(first: Any, second: Any) -> bool:
    states = []
    for view in (first, second):
        item = view.source.document.object(view.subject)
        material = tissue_inspection_stages.material(item, view.stage)
        if material is None:
            return False
        source = mapping(view).get(item.source, item.source)
        state = graph_records.rewritten(material.base_state, mapping(view))
        states.append((source, state))
    return states[0] == states[1]
