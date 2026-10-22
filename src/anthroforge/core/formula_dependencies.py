"""Formula/component ports participate in the application's existing output graph."""

from typing import Any

from .construction import Control
from .entities import SCP
from .numeric_properties import PropertyRef, overlaps
from .object_outputs import output
from .results import Port
from .shortcuts import DrivingShortcut
from .tissues import TissueVCP


def property_port(reference: PropertyRef) -> Port:
    suffix = "*" if reference.component is None else str(reference.component)
    return Port(reference.target, "property:" + "/".join(reference.path) + ":" + suffix)


def signature(drivers: tuple[DrivingShortcut, ...]) -> tuple[Any, ...]:
    return tuple(
        (d.id, tuple((f.id, f.enabled, f.target, f.inputs) for f in d.formulas)) for d in drivers
    )


def extend(
    edges: dict[Port, set[Port]], drivers: tuple[DrivingShortcut, ...], records: Any
) -> None:
    formulas = [(d, f) for d in drivers for f in d.formulas if f.enabled]
    references = {f.target for _, f in formulas}
    references.update(i.property for _, f in formulas for i in f.inputs if i.property is not None)
    for driver in drivers:
        edges[Port(driver.id, "driver")] = set()
    for reference in references:
        add_property(edges, reference, formulas, records)
    for driver, formula in formulas:
        add_formula(edges, driver, formula, records)


def add_formula(edges: Any, driver: Any, formula: Any, records: Any) -> None:
    inputs = {
        property_port(i.property) if i.property else Port(i.driver, "driver")
        for i in formula.inputs
    }
    edges[Port(formula.id, "formula")] = inputs | {Port(driver.id, "driver")}
    for port in effects(records.get(formula.target.target), formula.target):
        edges.setdefault(port, set()).add(property_port(formula.target))


def add_property(edges: Any, reference: PropertyRef, formulas: Any, records: Any) -> None:
    writers = {Port(f.id, "formula") for _, f in formulas if overlaps(reference, f.target)}
    if reference.path[0] == "world_transform":
        writers.add(Port(reference.target, "pose"))
    if reference.target not in records:
        writers.add(Port(reference.target, "missing_property"))
    edges[property_port(reference)] = writers


def effects(item: Any, reference: PropertyRef) -> set[Port]:
    if item is None:
        return set()
    field = reference.path[0]
    if field in ("transform", "geometry_offset"):
        return {Port(item.id, pose_role(item))}
    if isinstance(item, TissueVCP):
        from .tissue_revisions import ports

        return ports(item.id, {field})
    return {Port(item.id, "cage" if isinstance(item, Control) else output(item))}


def pose_role(item: Any) -> str:
    if isinstance(item, Control):
        return "control"
    return "pose" if isinstance(item, SCP) else "local_pose"
