"""Project-local reconstruction records; geometry snapshots never contain nested projects."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, cast
from uuid import uuid4

from .entities import IDENTITY

if TYPE_CHECKING:
    from .document import Document


def identity() -> str:
    return str(uuid4())


@dataclass(frozen=True, slots=True)
class SceneSnapshot:
    scene: "Document"
    id: str = field(default_factory=identity)

    def __post_init__(self) -> None:
        if self.scene.reconstruction != Reconstruction():
            raise ValueError("A reconstruction snapshot cannot contain project records.")


@dataclass(frozen=True, slots=True)
class Variant:
    name: str
    subjects: tuple[str, ...]
    editable: tuple[str, ...]
    baseline: str
    current: str
    id: str = field(default_factory=identity)
    parent: str = ""
    checkpoint: bool = False
    construction_map: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True, slots=True)
class AnatomicalType:
    name: str
    category: str = "OTHER"
    aliases: tuple[str, ...] = ()
    description: str = ""
    id: str = field(default_factory=identity)


@dataclass(frozen=True, slots=True)
class AnatomicalAssignment:
    target: str
    type_id: str
    side: str = "UNSPECIFIED"
    label: str = ""


@dataclass(frozen=True, slots=True)
class ReviewCollection:
    name: str
    members: tuple[str, ...] = ()
    id: str = field(default_factory=identity)


@dataclass(frozen=True, slots=True)
class SurfaceRegion:
    name: str
    target: str
    role: str
    topology: str
    triangles: tuple[int, ...]
    asset: str
    variant: str = ""
    id: str = field(default_factory=identity)


@dataclass(frozen=True, slots=True)
class ReconstructionStage:
    subject: str
    stage: str
    asset: str
    frame: tuple[float, ...] = IDENTITY
    variant: str = ""
    name: str = ""
    source: str = ""
    fingerprint: str = ""
    source_entity: str = ""
    source_revision: int = 0
    correspondence: str = ""
    id: str = field(default_factory=identity)


@dataclass(frozen=True, slots=True)
class Review:
    subject: str
    dimension: str
    signature: str
    decision: str = "PENDING"
    variant: str = ""
    stage: str = "final"
    reviewer: str = ""
    comment: str = ""
    evidence: tuple[str, ...] = ()
    id: str = field(default_factory=identity)


@dataclass(frozen=True, slots=True)
class ReconstructionWork:
    subject: str
    type_id: str = ""
    owner: str = ""
    status: str = "TODO"
    next_action: str = ""
    blocker: str = ""
    approach: str = ""
    checkpoint: str = ""
    id: str = field(default_factory=identity)


@dataclass(frozen=True, slots=True)
class Reconstruction:
    variants: tuple[Variant, ...] = ()
    snapshots: tuple[SceneSnapshot, ...] = ()
    types: tuple[AnatomicalType, ...] = ()
    assignments: tuple[AnatomicalAssignment, ...] = ()
    collections: tuple[ReviewCollection, ...] = ()
    regions: tuple[SurfaceRegion, ...] = ()
    stages: tuple[ReconstructionStage, ...] = ()
    reviews: tuple[Review, ...] = ()
    work: tuple[ReconstructionWork, ...] = ()

    def variant(self, key: str) -> Variant:
        return cast(Variant, next_record(self.variants, key, "variant"))

    def snapshot(self, key: str) -> "Document":
        return cast("Document", next_record(self.snapshots, key, "snapshot").scene)


def next_record(records: Any, key: str, kind: str) -> Any:
    item = next((row for row in records if row.id == key), None)
    if item is None:
        raise ValueError("Unknown " + kind + ": " + key)
    return item
