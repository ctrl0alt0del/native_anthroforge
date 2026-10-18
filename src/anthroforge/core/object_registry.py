"""Typed document lookup and relationship integrity without an anatomical wrapper."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import TYPE_CHECKING

from .construction import Control, Curve
from .curve_dependencies import targets as curve_targets
from .entities import SCP
from .fibers import Fiber
from .junctions import Junction
from .junctions import validate as validate_junctions
from .reference_images import ReferenceImage
from .surfaces import Surface

if TYPE_CHECKING:
    from .document import Document

type Construction = Curve | Surface | ReferenceImage
type SceneObject = SCP | Control | Construction


def kind(item: SceneObject) -> str:
    return {
        SCP: "SCP",
        Control: "CONTROL",
        Curve: "CURVE",
        Fiber: "FIBER",
        Surface: "SURFACE",
        ReferenceImage: "IMAGE",
    }[type(item)]


@dataclass(frozen=True, slots=True)
class ObjectRegistry:
    records: Mapping[str, SceneObject]
    construction: Mapping[str, Construction]
    source: tuple[Construction, ...]
    entities: tuple[SCP, ...]
    controls: tuple[Control, ...]
    consumers: Mapping[str, frozenset[str]]
    junctions: tuple[Junction, ...]

    def get(self, key: str) -> SceneObject:
        if key not in self.records:
            raise ValueError(f"Unknown object: {key}")
        return self.records[key]


def build(document: "Document", previous: ObjectRegistry | None) -> ObjectRegistry:
    if previous is not None and reusable(document, previous):
        return previous
    records = validated_records(document)
    return ObjectRegistry(
        MappingProxyType(records),
        MappingProxyType({v.id: v for v in document.objects}),
        document.objects,
        document.entities,
        document.controls,
        construction_consumers(document),
        document.junctions,
    )


def validated_records(document: "Document") -> dict[str, SceneObject]:
    items = (*document.entities, *document.controls, *document.objects)
    records = {item.id: item for item in items}
    if len(records) != len(items):
        raise ValueError("Object identities must be unique across all object categories.")
    validate(document, records)
    return records


def construction_consumers(document: "Document") -> Mapping[str, frozenset[str]]:
    users: dict[str, set[str]] = {}
    for item in (*document.entities, *document.objects):
        definition = getattr(item, "primitive", None) or item
        for use in getattr(definition, "curves", ()):
            users.setdefault(use.curve, set()).add(item.id)
    owners: tuple[SCP | Control, ...] = (*document.entities, *document.controls)
    for owner in owners:
        for binding in owner.deformers:
            users.setdefault(binding.control, set()).add(owner.id)
    return MappingProxyType({key: frozenset(value) for key, value in users.items()})


def reusable(document: "Document", previous: ObjectRegistry | None) -> bool:
    return bool(
        previous is not None
        and document.objects is previous.source
        and document.entities is previous.entities
        and document.controls is previous.controls
        and document.junctions is previous.junctions
    )


def validate(document: "Document", records: dict[str, SceneObject]) -> None:
    validate_junctions(document.junctions, document.objects)
    validate_primitives(document, records)
    for item in document.objects:
        validate_placement(document, item, records)
        if isinstance(item, Curve):
            validate_bindings(item, records)
        if isinstance(item, Surface):
            validate_sources(item, records)
    validate_parenting(document.objects)
    validate_point_ids(document)


def validate_placement(
    document: "Document", item: Construction, records: Mapping[str, SceneObject]
) -> None:
    if item.parent and (
        item.parent not in records or isinstance(records[item.parent], ReferenceImage)
    ):
        raise ValueError("Transform parent must exist and cannot be a reference image.")
    if set(item.owners) - document.index.entities.keys():
        raise ValueError("Workspace associations require anatomical objects.")


def validate_primitives(document: "Document", records: dict[str, SceneObject]) -> None:
    for item in document.entities:
        if item.primitive:
            for use in item.primitive.curves:
                if not isinstance(records.get(use.id), Curve):
                    raise ValueError("Primitive curve source does not exist.")


def validate_bindings(item: Curve, records: dict[str, SceneObject]) -> None:
    for target in curve_targets(item):
        if not isinstance(records.get(target), SCP):
            raise ValueError(
                "Curve obstacles and fiber bindings require anatomical surface providers."
            )


def validate_sources(item: Surface, records: Mapping[str, SceneObject]) -> None:
    sources = [records.get(use.curve) for use in item.curves]
    if any(not isinstance(source, Curve) for source in sources):
        raise ValueError("Surface sources must be curves or fibers.")
    closed = {source.closed for source in sources if isinstance(source, Curve)}
    if len(closed) != 1 or (item.kind == "PATCH" and closed != {True}):
        raise ValueError("Surface sources have incompatible closure.")
    if item.kind == "BRANCHED" and closed != {False}:
        raise ValueError("Branched surfaces require open curves.")


def validate_parenting(objects: tuple[Construction, ...]) -> None:
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
