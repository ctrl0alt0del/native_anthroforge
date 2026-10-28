"""Mapped formula inputs retain their accepted values until the new read set is equivalent."""

from dataclasses import replace
from typing import Any

from anthroforge.core.formula_dependencies import property_port
from anthroforge.core.numeric_properties import PropertyRef
from anthroforge.core.results import Port

from . import assembly_graph, assembly_mapping, construction_policy


def remapped(preparation: Any, value: Any, owner: str) -> Any:
    document = preparation.source.document
    item = document.formula_index.drivers.get(owner) or document.registry.records.get(owner)
    for ref, choice, target in preparation.mapping.replacements.get(owner, ()):
        container = assembly_graph.at(item, ref.path[:-1])
        if isinstance(container, PropertyRef):
            previous = property_port(container)
            if previous == Port(value.owner, value.output):
                current = property_port(assembly_mapping.mapped_property(container, choice, target))
                return replace(value, owner=current.owner, output=current.output)
    return None


def invalidate_changed(preparation: Any, document: Any) -> None:
    mapped = {r.target for r in preparation.mapping.references if r.target}
    for result in preparation.values.get("formula_results", ()):
        pair = document.formula_index.formulas.get(result.formula)
        if pair and pair[1].enabled and changed_inputs(document, result, mapped):
            preparation.mapping.changed.add(result.formula)


def changed_inputs(document: Any, result: Any, mapped: set[str]) -> bool:
    return any(
        r.owner in mapped
        and r.output.startswith("property:")
        and r != construction_policy.revision(document, Port(r.owner, r.output))
        for r in result.inputs
    )
