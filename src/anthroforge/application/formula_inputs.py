"""Captured formula read sets and synthetic output revisions."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from anthroforge.core import numeric_properties as numeric
from anthroforge.core.entities import Workspace
from anthroforge.core.expressions import Symbol
from anthroforge.core.formula_dependencies import property_port, property_reference
from anthroforge.core.results import Port, ReadRevision

from . import property_catalog, property_operations


@dataclass
class Captured:
    document: Any
    resources: Any
    engine: Any
    workspace: Workspace = Workspace()
    waiting_save: bool = False

    def editable(self, target: str) -> Any:
        return self.document.entity(target)


def formulas(document: Any) -> Mapping[str, Any]:
    return document.formula_index.formulas


def property_revision(document: Any, port: Port) -> ReadRevision:
    item = document.registry.records.get(port.owner)
    reference = property_reference(port)
    try:
        value = (
            item.matrix
            if reference.path[0] in ("transform", "world_transform")
            else numeric.read(item, reference)
        )
    except (ValueError, AttributeError):
        value = None
    return ReadRevision(port.owner, port.output, 0, 0, (repr(value),))


def revision(document: Any, port: Port) -> ReadRevision | None:
    if port.output.startswith("property:"):
        return property_revision(document, port)
    index = document.formula_index
    driver = index.drivers.get(port.owner)
    if driver is not None:
        return ReadRevision(driver.id, port.output, driver.generation, 0)
    record = index.formulas.get(port.owner)
    if record is not None:
        result = index.results.get(port.owner)
        return ReadRevision(
            port.owner, port.output, record[0].generation, result.revision if result else 0
        )
    return None


def dependencies(document: Any, formula: Any) -> set[str]:
    from .dependencies import closure, graph

    ports = closure(graph(document), {Port(formula.id, "formula")})
    return {p.owner for p in ports if p.output == "formula" and p.owner != formula.id}


def symbols(context: Captured, driver: Any, formula: Any) -> tuple[Symbol, ...]:
    result = [Symbol("value", driver.numeric_type, driver.dimension)]
    for entry in formula.inputs:
        if entry.property:
            descriptor = property_catalog.resolve(context.document, entry.property)
            result.append(Symbol(entry.name, descriptor.numeric_type, descriptor.dimension))
        else:
            other = next(d for d in context.document.driving_shortcuts if d.id == entry.driver)
            result.append(Symbol(entry.name, other.numeric_type, other.dimension))
    return tuple(result)


def values(context: Captured, driver: Any, formula: Any, outputs: dict[str, Any]) -> dict[str, Any]:
    result = {"value": driver.value}
    for entry in formula.inputs:
        if entry.property:
            result[entry.name] = property_value(context, entry.property, outputs)
        else:
            result[entry.name] = next(
                d.value for d in context.document.driving_shortcuts if d.id == entry.driver
            )
    return result


def property_value(context: Captured, reference: Any, outputs: dict[str, Any]) -> Any:
    for key, (_, formula) in formulas(context.document).items():
        if key in outputs and numeric.overlaps(reference, formula.target):
            value = outputs[key]
            return value[reference.component] if isinstance(value, tuple) else value
    return property_operations.read(context, reference)


def target_value(context: Captured, formula: Any, program: Any, value: Any) -> Any:
    descriptor = property_catalog.resolve(context.document, formula.target)
    program.output.require(descriptor.numeric_type, descriptor.dimension)
    count = descriptor.components if formula.target.component is None else 1
    return descriptor.validate((value,) * count if count > 1 else value)


def observations(document: Any, ids: set[str]) -> set[Port]:
    from .dependencies import closure, graph

    selected = {Port(key, "formula") for key in ids}
    observed = closure(graph(document), selected)
    for key, (_, formula) in formulas(document).items():
        if key in ids:
            observed.add(property_port(formula.target))
    return observed
