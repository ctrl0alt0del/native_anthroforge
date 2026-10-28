"""Relationship-specific choices; names never substitute for identity or material coordinates."""

from dataclasses import dataclass, field, replace
from typing import Any, cast
from uuid import uuid4

from anthroforge.core import anatomical_surfaces, graph_records, numeric_properties
from anthroforge.core.assembly import ExternalReference, ReferenceUse
from anthroforge.core.surface_references import SurfaceReference

from . import assembly_graph, property_catalog


@dataclass
class Mappings:
    source: Any
    destination: Any
    identities: dict[str, str]
    choices: dict[str, Any]
    replacements: dict[str, list[Any]] = field(default_factory=dict)
    references: list[ExternalReference] = field(default_factory=list)
    findings: list[dict[str, Any]] = field(default_factory=list)
    reads: set[str] = field(default_factory=set)
    rebind: set[str] = field(default_factory=set)
    rows: list[dict[str, Any]] = field(default_factory=list)

    def assess(self, boundaries: Any) -> None:
        for row in boundaries:
            decision = assembly_graph.decision(self.choices, row)
            self.rows.append(describe(row, decision))
            try:
                self.add(row, decision)
            except ValueError as error:
                self.findings.append(dict(reference=row.key, message=str(error), blocking=True))

    def add(self, row: Any, decision: Any) -> None:
        action = decision.get("action", "later")
        target = self.target(row, decision, action)
        external = declared(self.source.document, row, self.identities, target)
        if action != "detach":
            self.references.append(external)
        for owner, ref in row.uses:
            self.replacements.setdefault(owner, []).append((ref, decision, target or external.id))
            if decision.get("rebind", False):
                self.rebind.add(self.identities.get(owner, owner))

    def target(self, row: Any, decision: Any, action: str) -> str:
        if action == "detach" and row.relationship == "parent":
            return ""
        if action == "later" and row.relationship != "parent":
            return ""
        if action != "map":
            raise ValueError("Map or include this transform parent, or explicitly detach to world.")
        target = str(decision.get("target", ""))
        compatible(self.source.document, self.destination, row, decision, target)
        self.reads.add(target)
        return target

    def patch(self, original: Any, item: Any) -> Any:
        for ref, decision, target in self.replacements.get(getattr(original, "id", ""), ()):
            value = "" if decision.get("action") == "detach" else target
            item = patch_reference(item, ref, decision, value)
        return disable_external_outputs(original, item, self.identities)

    def surface(self, reference: SurfaceReference) -> SurfaceReference:
        for replacements in self.replacements.values():
            for ref, _choice, target in replacements:
                if ref.relationship == "support" and (ref.target, ref.role) == (
                    reference.target,
                    reference.role,
                ):
                    return replace(reference, target=target)
        return cast(SurfaceReference, graph_records.rewritten(reference, self.identities))


def describe(row: Any, choice: Any) -> dict[str, Any]:
    return dict(
        key=row.key,
        source=row.source,
        name=row.name,
        kind=row.kind,
        relationship=row.relationship,
        role=row.role,
        action=choice.get("action", "later"),
        target=choice.get("target", ""),
    )


def declared(document: Any, row: Any, ids: Any, target: str) -> ExternalReference:
    details = property_details(document, row.property)
    return ExternalReference(
        str(uuid4()),
        str(document.id),
        row.source,
        document.revision,
        row.name,
        row.kind,
        reference_uses(row, ids),
        target,
        row.property,
        **details,
    )


def reference_uses(row: Any, ids: Any) -> tuple[ReferenceUse, ...]:
    return tuple(
        ReferenceUse(ids.get(owner, owner), ref.relationship, ref.output, ref.role, ref.path)
        for owner, ref in row.uses
    )


def property_details(document: Any, reference: Any) -> dict[str, Any]:
    if reference is None:
        return {}
    descriptor = property_catalog.resolve(document, reference)
    return dict(
        numeric_type=descriptor.numeric_type,
        dimension=descriptor.dimension,
        components=descriptor.components,
    )


def compatible(source: Any, destination: Any, row: Any, choice: Any, target: str) -> None:
    item = destination.object(target)
    if row.property is not None:
        property_compatible(source, destination, row.property, choice, target)
    elif row.role:
        anatomical_surfaces.reference(target, destination.registry.records, row.role)
    elif row.relationship in ("association", "policy", "stacking"):
        if target not in destination.registry.anatomy:
            raise ValueError("This relationship requires an anatomical target.")
    elif row.relationship != "parent" and type(item) is not type(source.object(row.source)):
        raise ValueError("Select a compatible destination object.")


def property_compatible(
    source: Any, destination: Any, reference: Any, choice: Any, target: str
) -> None:
    previous = property_catalog.resolve(source, reference)
    selected = property_catalog.resolve(destination, mapped_property(reference, choice, target))
    if property_signature(previous) != property_signature(selected):
        raise ValueError(
            "Mapped properties must have matching numerical types, units and components."
        )


def property_signature(descriptor: Any) -> tuple[Any, ...]:
    return descriptor.numeric_type, descriptor.dimension, descriptor.components


def mapped_property(previous: Any, choice: Any, target: str) -> Any:
    if choice.get("property"):
        selected = numeric_properties.decode_reference(choice["property"])
        if selected.target != target:
            raise ValueError("Property and destination target must agree.")
        return selected
    return replace(previous, target=target)


def patch_reference(item: Any, ref: Any, choice: Any, target: str) -> Any:
    parent = assembly_graph.at(item, ref.path[:-1])
    if isinstance(parent, numeric_properties.PropertyRef):
        value = mapped_property(parent, choice, target)
        return graph_records.replace_at(item, ref.path[:-1], value)
    return graph_records.replace_at(item, ref.path, target)


def disable_external_outputs(original: Any, item: Any, ids: Any) -> Any:
    from anthroforge.core.shortcuts import DrivingShortcut

    if not isinstance(item, DrivingShortcut):
        return item
    external = {ids[f.id] for f in original.formulas if f.target.target not in ids}
    return replace(
        item,
        formulas=tuple(replace(f, enabled=False) if f.id in external else f for f in item.formulas),
    )
