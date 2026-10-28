"""Relationship-specific choices; names never substitute for identity or material coordinates."""

from dataclasses import asdict, dataclass, field, replace
from typing import Any, cast
from uuid import uuid4

from anthroforge.core import anatomical_surfaces, graph_records, numeric_properties
from anthroforge.core.assembly import ExternalReference, ReferenceUse, declaration
from anthroforge.core.results import Port
from anthroforge.core.surface_references import SurfaceReference

from . import assembly_graph, property_catalog


@dataclass
class Mappings:
    source: Any
    destination: Any
    identities: dict[str, str]
    choices: dict[str, Any]
    replacements: dict[str, list[Any]] = field(default_factory=dict)
    choices_by_reference: dict[str, tuple[Any, str]] = field(default_factory=dict)
    references: list[ExternalReference] = field(default_factory=list)
    findings: list[dict[str, Any]] = field(default_factory=list)
    reads: set[str] = field(default_factory=set)
    rebind: set[str] = field(default_factory=set)
    rows: list[dict[str, Any]] = field(default_factory=list)
    changed: set[str] = field(default_factory=set)
    changed_ports: set[Port] = field(default_factory=set)
    internal: frozenset[str] = field(init=False)

    def __post_init__(self) -> None:
        self.internal = frozenset(self.identities)

    def assess(self, boundaries: Any) -> None:
        for row in boundaries:
            decision = assembly_graph.decision(self.choices, row)
            self.rows.append(describe(row, decision))
            try:
                self.add(row, decision)
            except ValueError as error:
                self.findings.append(dict(reference=row.key, message=str(error), blocking=True))
        self.suggest()

    def suggest(self) -> None:
        from .assembly_choices import suggestions

        found = suggestions(self.source.document, self.destination, self.rows)
        for row in self.rows:
            if not row.get("instance"):
                row["suggested"] = found.get(row["key"], "")

    def add(self, row: Any, decision: Any) -> None:
        action = decision.get("action", "later")
        target = self.target(row, decision, action)
        external = declared(self.source.document, row, self.identities, target)
        external = replace(external, instance=decision.get("instance", "") if target else "")
        if action != "detach":
            self.references.append(external)
        self.choices_by_reference[row.key] = decision, target or external.id
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
        if decision.get("instance"):
            self.reads.add("mirror:" + decision["instance"])
        if row.property:
            self.reads.add("formula_writers")
        return target

    def patch(self, original: Any, item: Any) -> Any:
        if getattr(original, "id", "") not in self.replacements:
            return self.outputs(original, item)
        for ref in graph_records.references(original):
            selected = self.choices_by_reference.get(assembly_graph.boundary_key(original, ref)[0])
            if selected is None:
                continue
            decision, target = selected
            value = "" if decision.get("action") == "detach" else target
            item = patch_reference(item, ref, decision, value)
        return self.outputs(original, item)

    def outputs(self, original: Any, item: Any) -> Any:
        from .assembly_stacking import remap_orders

        item = remap_orders(self, original, item)
        return disable_external_outputs(original, item, self.identities, self.internal)

    def surface(self, reference: SurfaceReference) -> SurfaceReference:
        for replacements in self.replacements.values():
            for ref, _choice, target in replacements:
                if ref.relationship == "support" and (ref.target, ref.role, ref.instance) == (
                    reference.target,
                    reference.role,
                    reference.instance,
                ):
                    return replace(reference, target=target, instance=_choice.get("instance", ""))
        return cast(SurfaceReference, graph_records.rewritten(reference, self.identities))


def describe(row: Any, choice: Any) -> dict[str, Any]:
    return dict(
        key=row.key,
        source=row.source,
        name=row.name + (" · mirrored" if row.instance else ""),
        kind=row.kind,
        relationship=row.relationship,
        role=row.role,
        instance=row.instance,
        property=asdict(row.property) if row.property else None,
        consumers=tuple(dict.fromkeys(owner for owner, _ in row.uses)),
    ) | choice_details(choice)


def choice_details(choice: Any) -> dict[str, Any]:
    return dict(
        action=choice.get("action", "later"),
        target=choice.get("target", ""),
        target_instance=choice.get("instance", ""),
        rebind=bool(choice.get("rebind", False)),
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
        source_instance=row.instance,
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
    pending = declaration(document.registry.records, reference.target)
    descriptor = pending or property_catalog.resolve(document, reference)
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
        from .mirror_surfaces import normalize

        normalize(destination, SurfaceReference(target, row.role, choice.get("instance", "")))
    elif row.relationship in ("association", "policy", "stacking"):
        if target not in destination.registry.anatomy:
            raise ValueError("This relationship requires an anatomical target.")
    elif row.relationship != "parent":
        require_kind(item, row.kind)


def property_compatible(
    source: Any, destination: Any, reference: Any, choice: Any, target: str
) -> None:
    previous = property_details(source, reference)
    selected = property_catalog.resolve(destination, mapped_property(reference, choice, target))
    if tuple(
        previous[k] for k in ("numeric_type", "dimension", "components")
    ) != property_signature(selected):
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
    from .assembly_stacking import target_identity

    parent = assembly_graph.at(item, ref.path[:-1])
    if isinstance(parent, numeric_properties.PropertyRef):
        value = mapped_property(parent, choice, target)
        return graph_records.replace_at(item, ref.path[:-1], value)
    if ref.relationship == "support" and hasattr(parent, "instance"):
        value = replace(parent, target=target, instance=choice.get("instance", ""))
        return graph_records.replace_at(item, ref.path[:-1], value)
    value = target_identity(ref, choice, target)
    return graph_records.replace_at(item, ref.path, value)


def require_kind(item: Any, kind: str) -> None:
    from anthroforge.core.object_registry import kind as object_kind

    if object_kind(item) != kind:
        raise ValueError("Select a compatible destination object.")


def disable_external_outputs(original: Any, item: Any, ids: Any, internal: Any) -> Any:
    from anthroforge.core.shortcuts import DrivingShortcut

    if not isinstance(item, DrivingShortcut) or ids.get(original.id) == original.id:
        return item
    external = {ids.get(f.id, f.id) for f in original.formulas if f.target.target not in internal}
    return replace(
        item,
        formulas=tuple(replace(f, enabled=False) if f.id in external else f for f in item.formulas),
    )
