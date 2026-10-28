"""Distinct binding, base, rest, intrinsic and final dependency outputs."""

from collections.abc import Mapping

from . import tissue_groups
from .anatomical_surfaces import inputs as surface_inputs
from .mirroring import source as source_identity
from .object_outputs import output
from .objects import ObjectRecord
from .points import Anchor
from .results import Port
from .tissues import TissueVCP


def inputs(item: ObjectRecord, objects: tuple[ObjectRecord, ...]) -> set[Port]:
    if isinstance(item, Anchor):
        return surface_inputs(item.binding.reference)
    if isinstance(item, TissueVCP):
        records = {o.id: o for o in objects}
        return source_inputs(item, records) | constraint_inputs(item)
    return set()


def source_inputs(item: TissueVCP, records: Mapping[str, ObjectRecord]) -> set[Port]:
    source = records.get(item.source)
    role = output(source) if source is not None else "geometry"
    return {Port(item.source, role), Port(item.source, "pose")}


def constraint_inputs(item: TissueVCP) -> set[Port]:
    return {
        value
        for row in item.constraints
        if row.reference is not None
        for value in surface_inputs(row.reference)
    }


def edges(objects: tuple[ObjectRecord, ...]) -> dict[Port, set[Port]]:
    records = {o.id: o for o in objects}
    result: dict[Port, set[Port]] = {}
    groups = tissue_groups.groups(records)
    for item in objects:
        if isinstance(item, TissueVCP):
            result.update(tissue_edges(item, records))
            if item.id in groups:
                result[Port(item.id, "final")] = tissue_groups.inputs(records, groups[item.id])
    return result


def tissue_edges(item: TissueVCP, records: Mapping[str, ObjectRecord]) -> dict[Port, set[Port]]:
    return {
        Port(item.id, "base"): source_inputs(item, records) | {Port(item.id, "pose")},
        Port(item.id, "rest"): {Port(item.id, "base")},
        Port(item.id, "intrinsic"): {Port(item.id, "rest")} | constraint_inputs(item),
        Port(item.id, "stack_scope"): set(),
        Port(item.id, "plan"): plan_inputs(item, records),
        Port(item.id, "final"): final_inputs(item),
        Port(item.id, "geometry"): {Port(item.id, "final")},
    }


def final_inputs(item: TissueVCP) -> set[Port]:
    if not item.stacking:
        return {Port(item.id, "intrinsic"), Port(item.id, "plan")}
    return {Port(item.id, "plan")} | {Port(key, "final") for key in item.stack_plan.providers}


def plan_inputs(item: TissueVCP, records: Mapping[str, ObjectRecord]) -> set[Port]:
    required = {*item.stack_plan.providers, *(r.other for r in item.stack_relationships)}
    missing = {Port(key, "final") for key in required if source_identity(key) not in records}
    return {Port(item.id, "intrinsic"), Port(item.id, "stack_scope")} | missing


def signature(item: ObjectRecord) -> tuple[object, ...]:
    if not isinstance(item, TissueVCP):
        return ()
    return (
        item.stacking,
        item.stack_plan.providers,
        tuple(r.other for r in item.stack_relationships),
    )
