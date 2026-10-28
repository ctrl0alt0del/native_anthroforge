"""Typed document lookup and relationship integrity without an anatomical wrapper."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

from . import assembly, registry_validation
from .construction import Control, Curve
from .curve_dependencies import targets as curve_targets
from .deformer_references import sources as deformer_sources
from .entities import SCP
from .fibers import Fiber
from .junctions import Junction
from .junctions import validate as validate_junctions
from .membranes import Membrane
from .points import Anchor, Point
from .reference_images import ReferenceImage
from .surfaces import Surface
from .tissues import TissueVCP

if TYPE_CHECKING:
    from .document import Document

type Construction = Curve | Surface | ReferenceImage | Point
type Authored = Construction | TissueVCP
type Anatomy = SCP | TissueVCP
type SceneObject = SCP | Control | Authored


def kind(item: SceneObject) -> str:
    return {
        SCP: "SCP",
        Control: "CONTROL",
        Curve: "CURVE",
        Fiber: "FIBER",
        Surface: "SURFACE",
        Membrane: "MEMBRANE",
        Point: "POINT",
        Anchor: "ANCHOR",
        TissueVCP: "TISSUE",
        ReferenceImage: "IMAGE",
    }[type(item)]


@dataclass(frozen=True, slots=True)
class ObjectRegistry:
    records: Mapping[str, SceneObject]
    construction: Mapping[str, Construction]
    source: tuple[Authored, ...]
    entities: tuple[SCP, ...]
    controls: tuple[Control, ...]
    consumers: Mapping[str, frozenset[str]]
    junctions: tuple[Junction, ...]
    anatomy: Mapping[str, Anatomy]
    authored: Mapping[str, Authored]
    external: tuple[assembly.ExternalReference, ...] = ()

    def get(self, key: str) -> SceneObject:
        assembly.require_resolved(self.records, key)
        if key not in self.records:
            raise ValueError(f"Unknown object: {key}")
        return self.records[key]


def build(document: "Document", previous: ObjectRegistry | None) -> ObjectRegistry:
    if previous is not None and reusable(document, previous):
        return previous
    records, consumers = validated_records(document, previous)
    return indexed_records(document, records, consumers)


def indexed_records(document: "Document", records: Any, consumers: Any) -> ObjectRegistry:
    return ObjectRegistry(
        records,
        MappingProxyType({v.id: v for v in document.objects if not isinstance(v, TissueVCP)}),
        document.objects,
        document.entities,
        document.controls,
        consumers,
        document.junctions,
        MappingProxyType({k: v for k, v in records.items() if isinstance(v, (SCP, TissueVCP))}),
        MappingProxyType({v.id: v for v in document.objects}),
        document.external_references,
    )


def validated_records(
    document: "Document", previous: ObjectRegistry | None = None
) -> tuple[Mapping[str, SceneObject], Mapping[str, frozenset[str]]]:
    items = (*document.entities, *document.controls, *document.objects)
    records = assembly.records({item.id: item for item in items}, document.external_references)
    if len(records) != len(items):
        raise ValueError("Object identities must be unique across all object categories.")
    if previous and validation_reusable(document, records, previous):
        return records, previous.consumers
    validate(document, records)
    return records, construction_consumers(document)


def validation_reusable(document: "Document", records: Any, previous: ObjectRegistry) -> bool:
    return (
        document.external_references is previous.external
        and document.junctions == previous.junctions
        and registry_validation.reusable(records, previous.records)
    )


def construction_consumers(document: "Document") -> Mapping[str, frozenset[str]]:
    users: dict[str, set[str]] = {}
    for item in (*document.entities, *document.objects):
        definition = getattr(item, "primitive", None) or item
        for use in getattr(definition, "curves", ()):
            users.setdefault(use.curve, set()).add(item.id)
        if isinstance(item, TissueVCP):
            users.setdefault(item.source, set()).add(item.id)
    owners: tuple[SCP | Control, ...] = (*document.entities, *document.controls)
    for owner in owners:
        for binding in owner.deformers:
            for source in deformer_sources(binding):
                users.setdefault(source, set()).add(owner.id)
    return MappingProxyType({key: frozenset(value) for key, value in users.items()})


def reusable(document: "Document", previous: ObjectRegistry | None) -> bool:
    return bool(
        previous is not None
        and document.objects is previous.source
        and document.entities is previous.entities
        and document.controls is previous.controls
        and document.junctions is previous.junctions
        and document.external_references is previous.external
    )


def validate(document: "Document", records: Mapping[str, SceneObject]) -> None:
    validate_deformers(document, records)
    validate_junctions(document.junctions, document.objects)
    validate_primitives(document, records)
    for item in document.objects:
        validate_placement(document, item, records)
        validate_object(item, records)
    validate_parenting(document.objects)
    validate_point_ids(document)


def validate_deformers(document: "Document", records: Mapping[str, SceneObject]) -> None:
    from .anatomical_surfaces import reference

    for owner in document.entities:
        for binding in owner.deformers:
            if binding.shrinkwrap:
                surface = binding.shrinkwrap.surface
                reference(surface.target, records, surface.role)


def validate_object(item: Authored, records: Mapping[str, SceneObject]) -> None:
    from .tissue_policy import validate as validate_tissue

    if isinstance(item, Curve):
        validate_bindings(item, records)
    if isinstance(item, Surface):
        validate_sources(item, records)
    if isinstance(item, TissueVCP):
        validate_tissue(item, records)
    if isinstance(item, Anchor):
        validate_anchor(item, records)


def validate_placement(
    document: "Document", item: Authored, records: Mapping[str, SceneObject]
) -> None:
    if item.parent and (
        item.parent not in records or isinstance(records[item.parent], ReferenceImage)
    ):
        raise ValueError("Transform parent must exist and cannot be a reference image.")
    if any(not anatomical_or_external(records, key) for key in item.owners):
        raise ValueError("Workspace associations require anatomical objects.")


def validate_primitives(document: "Document", records: Mapping[str, SceneObject]) -> None:
    for item in document.entities:
        if item.primitive:
            for use in item.primitive.curves:
                if not isinstance(records.get(use.id), Curve):
                    raise ValueError("Primitive curve source does not exist.")


def validate_bindings(item: Curve, records: Mapping[str, SceneObject]) -> None:
    from .curve_engines import RoutingSettings

    excluded = (
        item.engine_settings.excluded_obstacles
        if isinstance(item.engine_settings, RoutingSettings)
        else ()
    )
    for target in curve_targets(item) | set(excluded):
        if not anatomical_or_external(records, target):
            raise ValueError(
                "Curve obstacles and fiber bindings require anatomical surface providers."
            )


def validate_sources(item: Surface, records: Mapping[str, SceneObject]) -> None:
    from .surface_branches import validate_sources as validate_branches

    sources = [records.get(use.curve) for use in item.curves]
    if isinstance(item, Membrane) and any(not isinstance(source, Fiber) for source in sources):
        raise ValueError("Membrane sources must all be Fibers.")
    if any(not isinstance(source, Curve) for source in sources):
        raise ValueError("Surface sources must be curves or fibers.")
    closed = {source.closed for source in sources if isinstance(source, Curve)}
    if len(closed) != 1 or (item.kind == "PATCH" and closed != {True}):
        raise ValueError("Surface sources have incompatible closure.")
    if item.kind == "BRANCHED" and closed != {False}:
        raise ValueError("Branched surfaces require open curves.")
    validate_branches(item, records)


def validate_parenting(objects: tuple[Authored, ...]) -> None:
    parents, visited = {item.id: item.parent for item in objects}, set()
    for item in objects:
        pending, key = set(), item.id
        while key in parents and key not in visited:
            if key in pending:
                raise ValueError("Cyclic ordinary transform parenting.")
            pending.add(key)
            key = parents[key]
        visited.update(pending)


def validate_point_ids(document: "Document") -> None:
    from .construction_validation import identities

    items: tuple[SCP | Control, ...] = (*document.entities, *document.controls)
    existing = [key for item in items for key in identities(item)]
    keys = [*existing, *(item.id for item in document.objects)]
    keys.extend(j.id for j in document.junctions)
    keys.extend(p.id for item in document.objects if isinstance(item, Curve) for p in item.points)
    if any(not key for key in keys) or len(set(keys)) != len(keys):
        raise ValueError("Authored identities must be nonempty and unique across the document.")


def validate_anchor(item: Anchor, records: Mapping[str, SceneObject]) -> None:
    from .anatomical_surfaces import reference

    target = item.binding.reference
    reference(target.target, records, target.role)


def anatomical_or_external(records: Mapping[str, SceneObject], key: str) -> bool:
    return isinstance(records.get(key), (SCP, TissueVCP)) or assembly.permits(
        records, key, ("SCP", "TISSUE")
    )
