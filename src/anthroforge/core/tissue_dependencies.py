"""Distinct binding, base, rest, intrinsic and final dependency outputs."""

from collections.abc import Mapping

from .anatomical_surfaces import port
from .object_outputs import output
from .objects import ObjectRecord
from .points import Anchor
from .results import Port
from .tissues import TissueVCP


def inputs(item: ObjectRecord, objects: tuple[ObjectRecord, ...]) -> set[Port]:
    if isinstance(item, Anchor):
        return {port(item.binding.reference), Port(item.binding.reference.target, "pose")}
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
        for value in (port(row.reference), Port(row.reference.target, "pose"))
    }


def edges(objects: tuple[ObjectRecord, ...]) -> dict[Port, set[Port]]:
    records = {o.id: o for o in objects}
    result: dict[Port, set[Port]] = {}
    for item in objects:
        if isinstance(item, TissueVCP):
            result.update(tissue_edges(item, records))
    return result


def tissue_edges(item: TissueVCP, records: Mapping[str, ObjectRecord]) -> dict[Port, set[Port]]:
    return {
        Port(item.id, "base"): source_inputs(item, records),
        Port(item.id, "rest"): {Port(item.id, "base")},
        Port(item.id, "intrinsic"): {Port(item.id, "rest")} | constraint_inputs(item),
        Port(item.id, "final"): {Port(item.id, "intrinsic")},
        Port(item.id, "geometry"): {Port(item.id, "final")},
    }
