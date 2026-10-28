"""Accepted stacking providers are external inputs, without anatomical rebinding semantics."""

from dataclasses import replace
from typing import Any

from anthroforge.core import graph_records
from anthroforge.core.mirroring import MirrorInstance
from anthroforge.core.results import Port
from anthroforge.core.surface_references import SurfaceReference
from anthroforge.core.tissues import TissueVCP


def assess(bindings: Any, row: Any) -> None:
    previous = SurfaceReference(row["source"], "TISSUE_FINAL", row.get("instance", ""))
    current = SurfaceReference(row["target"], "TISSUE_FINAL", row.get("target_instance", ""))
    same = bindings.equivalent(previous, current)
    same = (
        same
        and bindings.source_provider(previous).frame == bindings.destination_provider(current).frame
    )
    if same:
        return
    bindings.p.mapping.changed_ports.update(
        Port(bindings.p.ids[key], "plan") for key in row["consumers"]
    )


def remap_orders(mapping: Any, original: Any, item: Any) -> Any:
    if not isinstance(item, TissueVCP):
        return item
    identities = dict(mapping.identities)
    identities.update(replacements(mapping.replacements.get(original.id, ())))
    orders = graph_records.rewritten(original.stack_plan.orders, identities)
    return replace(item, stack_plan=replace(item.stack_plan, orders=orders))


def replacements(rows: Any) -> dict[str, str]:
    return {
        source_identity(ref): target_identity(ref, choice, target)
        for ref, choice, target in rows
        if ref.relationship == "stacking"
    }


def source_identity(ref: Any) -> str:
    return MirrorInstance(ref.target, ref.instance).id if ref.instance else str(ref.target)


def target_identity(ref: Any, choice: Any, target: str) -> str:
    if ref.relationship == "stacking" and choice.get("instance"):
        return MirrorInstance(target, choice["instance"]).id
    return target
