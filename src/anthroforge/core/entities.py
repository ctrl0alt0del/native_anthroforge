"""Immutable authored SCP records; mesh buffers have independent ownership."""

from dataclasses import dataclass, field
from math import isfinite
from typing import TYPE_CHECKING
from uuid import uuid4

from .image_presentation import ImagePresentation
from .inspection_views import CameraBookmark, Measurement
from .presentation import validate_categories
from .results import EvaluationResult
from .units import factor

if TYPE_CHECKING:
    from .construction import Deformer, Primitive, ResolvedPrimitive, Thickness

IDENTITY = (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0)


@dataclass(frozen=True, slots=True)
class Attachment:
    parent_mode: str = "SURFACE_NEAREST"
    child_mode: str = "FACE_CENTER"
    follow_rotation: bool = True
    strategy: str = "AUTO"
    face_lock: int = -1
    vertex_lock: int = -1
    binding: tuple[float, ...] = ()
    material_asset: str = ""
    parent_instance: str = ""

    def __post_init__(self) -> None:
        if self.parent_mode not in ("SURFACE_NEAREST", "OBJECT_ORIGIN"):
            raise ValueError("Invalid parent anchor mode.")
        if self.child_mode not in ("FACE_CENTER", "VERTEX_NEAREST", "OBJECT_ORIGIN"):
            raise ValueError("Invalid child anchor mode.")
        if self.strategy not in ("AUTO", "STABLE_SURFACE", "DEFORMATION_FLOW"):
            raise ValueError("Invalid rotation strategy.")
        if self.binding and (len(self.binding) != 28 or not all(map(isfinite, self.binding))):
            raise ValueError("Invalid attachment binding.")


@dataclass(frozen=True, slots=True)
class AttachmentReceipt:
    parent: str
    parent_matrix: tuple[float, ...]
    parent_offset: tuple[float, ...]
    parent_asset: str
    child_matrix: tuple[float, ...]
    child_offset: tuple[float, ...]
    settings: Attachment
    evaluator_version: int = 0
    effective: Attachment | None = None
    parent_reflection: tuple[float, ...] = ()


@dataclass(frozen=True, slots=True)
class SCP:
    name: str
    id: str = field(default_factory=lambda: str(uuid4()))
    parent: str = ""
    asset: str = ""
    matrix: tuple[float, ...] = IDENTITY
    geometry_offset: tuple[float, ...] = (0.0, 0.0, 0.0)
    attachment: Attachment = field(default_factory=Attachment)
    color: str = "#72b8ad"
    update_mode: str = "INHERIT"
    generation: int = 0
    status: str = "ready"
    error: str = ""
    capture_parent_matrix: tuple[float, ...] = ()
    capture_parent_offset: tuple[float, ...] = (0.0, 0.0, 0.0)
    primitive: "Primitive | ResolvedPrimitive | None" = None
    deformers: tuple["Deformer", ...] = ()
    thickness: "Thickness | None" = None
    result: EvaluationResult = field(default_factory=EvaluationResult)
    result_generation: int = 0
    pose_revision: int = 0
    construction_revision: int = 0
    pose_receipt: AttachmentReceipt | None = None

    def __post_init__(self) -> None:
        if not self.id or not self.name.strip():
            raise ValueError("SCP identity and name must not be empty.")
        validate_matrix(self.matrix)
        if self.capture_parent_matrix:
            validate_matrix(self.capture_parent_matrix)
        if len(self.geometry_offset) != 3 or not all(map(isfinite, self.geometry_offset)):
            raise ValueError("Invalid geometry offset.")
        if self.update_mode not in ("INHERIT", "LIVE", "ON_RELEASE", "MANUAL"):
            raise ValueError("Invalid SCP update mode.")


@dataclass(frozen=True, slots=True)
class Workspace:
    name: str = "Whole document"
    members: tuple[str, ...] = ()
    focused: bool = False
    hidden: tuple[str, ...] = ()
    unpickable: tuple[str, ...] = ()
    camera: tuple[float, ...] = (0.0, 0.0, 0.0, -20.0, 25.0, 0.0, 4.0)
    orthographic: bool = False
    handles: bool = True
    anchors: bool = True
    diagnostics: bool = True
    hidden_categories: tuple[str, ...] = ()
    unpickable_categories: tuple[str, ...] = ()
    display_units: str = "m"
    measurements: tuple[Measurement, ...] = ()
    bookmarks: tuple[CameraBookmark, ...] = ()
    reference_images: tuple[ImagePresentation, ...] = ()
    cursor: tuple[float, ...] = (0.0, 0.0, 0.0)
    mirror_display: str = "BOTH"

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Workspace name must not be empty.")
        factor(self.display_units)
        if self.mirror_display not in ("BOTH", "SOURCE", "MIRROR"):
            raise ValueError("Mirror display must be BOTH, SOURCE or MIRROR.")
        validate_categories(self.hidden_categories)
        validate_categories(self.unpickable_categories)
        if len({v.target for v in self.reference_images}) != len(self.reference_images):
            raise ValueError("Image appearance must have unique targets.")
        if len(self.camera) != 7 or not all(map(isfinite, self.camera)) or self.camera[6] <= 0:
            raise ValueError("Invalid workspace camera.")
        if len(self.cursor) != 3 or not all(map(isfinite, self.cursor)):
            raise ValueError("Cursor needs three finite world coordinates.")


def validate_matrix(matrix: tuple[float, ...]) -> None:
    if len(matrix) != 16 or not all(map(isfinite, matrix)):
        raise ValueError("Transform must have sixteen finite elements.")
    if matrix[12:] != (0.0, 0.0, 0.0, 1.0):
        raise ValueError("Transform must be affine.")
    a, b, c, d, e, f, g, h, i = (matrix[x] for x in (0, 1, 2, 4, 5, 6, 8, 9, 10))
    if abs(a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)) < 1e-30:
        raise ValueError("Transform scale must be nonzero.")


def descendants(entities: tuple[SCP, ...], entity_id: str) -> set[str]:
    children: dict[str, list[str]] = {}
    for item in entities:
        children.setdefault(item.parent, []).append(item.id)
    result, pending = set(), [entity_id]
    while pending:
        current = pending.pop()
        if current in result:
            raise ValueError("Cyclic SCP hierarchy.")
        result.add(current)
        pending.extend(children.get(current, ()))
    return result


def validate_tree(entities: tuple[SCP, ...]) -> None:
    ids = {item.id for item in entities}
    roots = [item.id for item in entities if not item.parent]
    if len(ids) != len(entities):
        raise ValueError("Duplicate SCP identity.")
    if entities and (len(roots) != 1 or descendants(entities, roots[0]) != ids):
        raise ValueError("SCPs must form one connected tree with exactly one root.")
    if any(item.parent and item.parent not in ids for item in entities):
        raise ValueError("Missing SCP parent.")
