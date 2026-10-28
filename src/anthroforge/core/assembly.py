"""Persisted import provenance and declared references, never placeholder scene objects."""

from collections.abc import Iterator, Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

from .numeric_properties import PropertyRef


@dataclass(frozen=True, slots=True)
class ReferenceUse:
    owner: str
    relationship: str
    output: str = "geometry"
    role: str = ""
    path: tuple[str | int, ...] = ()


@dataclass(frozen=True, slots=True)
class ExternalReference:
    id: str
    source_document: str
    source_entity: str
    source_revision: int
    name: str
    kind: str
    uses: tuple[ReferenceUse, ...] = ()
    target: str = ""
    property: PropertyRef | None = None
    numeric_type: str = ""
    dimension: str = ""
    components: int = 0
    surface_asset: str = ""
    surface_frame: tuple[float, ...] = ()
    source_instance: str = ""
    instance: str = ""

    def __post_init__(self) -> None:
        if not all((self.id, self.source_document, self.source_entity, self.kind)):
            raise ValueError("An external reference requires a complete source identity.")
        if self.source_revision < 0 or self.id == self.target:
            raise ValueError("Invalid external reference revision or resolution.")


@dataclass(frozen=True, slots=True)
class ImportProvenance:
    id: str
    source_document: str
    source_revision: int
    package_digest: str
    source_name: str
    identities: tuple[tuple[str, str], ...] = ()
    mappings: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class ReferenceRecords(Mapping[str, Any]):
    """Only real objects are iterable; external declarations are separate capabilities."""

    objects: Mapping[str, Any]
    external: Mapping[str, ExternalReference] = field(default_factory=dict)

    def __iter__(self) -> Iterator[str]:
        return iter(self.objects)

    def __len__(self) -> int:
        return len(self.objects)

    def __getitem__(self, key: str) -> Any:
        return self.objects[key]


def records(
    objects: Mapping[str, Any], references: tuple[ExternalReference, ...]
) -> ReferenceRecords:
    pending = {ref.id: ref for ref in references if not ref.target}
    if len({ref.id for ref in references}) != len(references) or pending.keys() & objects.keys():
        raise ValueError("External reference identities must be distinct from scene objects.")
    return ReferenceRecords(MappingProxyType(dict(objects)), MappingProxyType(pending))


def declaration(records: Mapping[str, Any], key: str) -> ExternalReference | None:
    return getattr(records, "external", {}).get(key)


def permits(records: Mapping[str, Any], key: str, kinds: tuple[str, ...]) -> bool:
    value = declaration(records, key)
    return bool(value and value.kind in kinds)


def require_resolved(records: Mapping[str, Any], key: str) -> None:
    value = declaration(records, key)
    if value is not None:
        raise ValueError(f"Resolve imported reference '{value.name}' before this calculation.")
