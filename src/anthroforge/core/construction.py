"""Editable geometric definitions, independent of evaluated meshes and presentation."""

from dataclasses import dataclass, field
from math import isfinite
from uuid import uuid4

from .construction_values import integer as integer
from .construction_values import validate_range as validate_range
from .curve_engines import BezierSettings, PathSettings, PolylineSettings, RoutingSettings
from .curve_uses import CurveUse
from .entities import IDENTITY, validate_matrix
from .objects import ConstructionObject
from .results import ControlResult
from .segment_chain import SegmentChain
from .shrinkwrap import Shrinkwrap


def identity() -> str:
    return str(uuid4())


def finite(values: tuple[float, ...], count: int) -> None:
    if len(values) != count or not all(map(isfinite, values)):
        raise ValueError(f"Expected {count} finite values.")


def validate_weights(weights: tuple[float, ...], count: int | None = None) -> None:
    if any(not isfinite(w) or not 0 <= w <= 1 for w in weights):
        raise ValueError("Influence weights must be finite and between zero and one.")
    if weights and count is not None and len(weights) != count:
        raise ValueError("Influence weights must match the target point count.")


@dataclass(frozen=True, slots=True)
class CurvePoint:
    position: tuple[float, ...] = (0.0, 0.0, 0.0)
    left: tuple[float, ...] = (-0.1, 0.0, 0.0)
    right: tuple[float, ...] = (0.1, 0.0, 0.0)
    left_mode: str = "AUTO"
    right_mode: str = "AUTO"
    radius: float = 1.0
    tilt: float = 0.0
    id: str = field(default_factory=identity)
    junction: str = ""
    stacking_fixed: bool = False
    protected_crease: bool = False

    def __post_init__(self) -> None:
        for value in (self.position, self.left, self.right):
            finite(value, 3)
        modes = ("AUTO", "ALIGNED", "FREE", "VECTOR")
        if self.left_mode not in modes or self.right_mode not in modes:
            raise ValueError("Unknown Bézier handle mode.")
        if not isfinite(self.radius) or self.radius < 0 or not isfinite(self.tilt):
            raise ValueError("Curve radius must be nonnegative and radius/tilt finite.")
        if type(self.stacking_fixed) is not bool or type(self.protected_crease) is not bool:
            raise ValueError("Curve point protection flags must be Boolean.")


@dataclass(frozen=True, slots=True)
class Curve(ConstructionObject):
    points: tuple[CurvePoint, ...]
    name: str = field(default="Curve", kw_only=True)
    closed: bool = False
    start: float | None = None
    span: float | None = None
    engine_settings: PathSettings = field(default_factory=BezierSettings)

    @property
    def engine(self) -> str:
        return self.engine_settings.kind

    @property
    def resolution(self) -> int:
        return (
            self.engine_settings.resolution
            if isinstance(self.engine_settings, BezierSettings)
            else 1
        )

    def __post_init__(self) -> None:
        ConstructionObject.__post_init__(self)
        if len(self.points) < 2 or len({p.id for p in self.points}) != len(self.points):
            raise ValueError("A curve needs at least two distinct control points.")
        if self.closed and len(self.points) < 3:
            raise ValueError("A closed curve needs at least three authored points.")
        if not isinstance(
            self.engine_settings, (BezierSettings, PolylineSettings, RoutingSettings)
        ):
            raise ValueError("Curve requires typed path engine settings.")
        validate_matrix(self.matrix)
        validate_range(self.start, self.span)


def cyclic(curve: Curve, primitive: "PrimitiveParameters") -> bool:
    return curve.closed and (primitive.span if curve.span is None else curve.span) == 1.0


@dataclass(frozen=True, slots=True)
class BodyPiece:
    curve: str
    shape: str = "CAPSULE"
    id: str = field(default_factory=identity)
    width: float = 0.1
    depth: float = 0.1
    fit: bool = True
    length: float = 1.0
    position: float = 0.0
    sides: int = 16
    subdivision: int = 0

    def __post_init__(self) -> None:
        if self.shape not in ("BOX", "CYLINDER", "CAPSULE"):
            raise ValueError("Body shape must be BOX, CYLINDER, or CAPSULE.")
        if any(not isfinite(v) or v <= 0 for v in (self.width, self.depth, self.length)):
            raise ValueError("Body dimensions must be positive and finite.")
        if not isfinite(self.position) or not integer(self.sides, 3, 256):
            raise ValueError("Invalid body position or radial resolution.")
        if not integer(self.subdivision, 0, 5):
            raise ValueError("Body base subdivision must be between zero and five.")


@dataclass(frozen=True, slots=True)
class PrimitiveParameters:
    kind: str
    source: str = ""
    pieces: tuple[BodyPiece, ...] = ()
    samples: int = 32
    strips: int = 1
    start: float = 0.0
    span: float = 1.0
    caps: bool = False
    chain: SegmentChain | None = None

    def __post_init__(self) -> None:
        if self.kind not in ("IMPORTED", "LOFT", "BODY", "SEGMENT_CHAIN"):
            raise ValueError("Unknown primitive family.")
        if (self.kind == "SEGMENT_CHAIN") != isinstance(self.chain, SegmentChain):
            raise ValueError("Segment Chain requires its own typed parameters.")
        if not integer(self.samples, 2, 4096) or not integer(self.strips, 1, 256):
            raise ValueError("Invalid primitive resolution.")
        validate_range(self.start, self.span)


@dataclass(frozen=True, slots=True)
class Primitive(PrimitiveParameters):
    curves: tuple[CurveUse, ...] = ()

    def __post_init__(self) -> None:
        PrimitiveParameters.__post_init__(self)
        if any(not isinstance(use, CurveUse) for use in self.curves):
            raise ValueError("Primitive definitions require curve references, not embedded curves.")
        if self.kind == "BODY" and any(
            use.samples is not None and use.samples < 3 for use in self.curves
        ):
            raise ValueError("Body construction needs at least three longitudinal samples.")
        validate_family(self)


@dataclass(frozen=True, slots=True)
class ResolvedPrimitive(PrimitiveParameters):
    """Transient owned evaluation/edit input; never stored in a document."""

    curves: tuple[Curve, ...] = ()

    def __post_init__(self) -> None:
        PrimitiveParameters.__post_init__(self)
        validate_family(self)


def validate_family(value: Primitive | ResolvedPrimitive) -> None:
    ids = {c.id for c in value.curves}
    if len(ids) != len(value.curves):
        raise ValueError("Duplicate construction curve.")
    if value.kind == "BODY" and value.samples < 3:
        raise ValueError("Body construction needs at least three longitudinal samples.")
    if value.kind == "IMPORTED" and (not value.source or value.curves or value.pieces):
        raise ValueError("Imported construction requires only a source mesh.")
    if value.kind == "LOFT" and (len(ids) < 2 or value.pieces):
        raise ValueError("Loft requires at least two curves and no body pieces.")
    if value.kind == "BODY" and (not value.pieces or any(p.curve not in ids for p in value.pieces)):
        raise ValueError("Every body piece must reference a source curve.")
    if value.kind == "SEGMENT_CHAIN" and (value.curves or value.pieces or value.source):
        raise ValueError("Segment Chain is parameter-driven and has no curve or mesh source.")


@dataclass(frozen=True, slots=True)
class Target:
    owner: str
    stage: str = "GEOMETRY"
    component: str = ""

    def __post_init__(self) -> None:
        if self.stage not in ("CURVE", "BASE", "GEOMETRY", "LATTICE"):
            raise ValueError("Unknown deformation target stage.")


@dataclass(frozen=True, slots=True)
class Deformer:
    kind: str
    control: str
    target: Target
    id: str = field(default_factory=identity)
    enabled: bool = True
    strength: float = 1.0
    indices: tuple[int, ...] = ()
    members: tuple[str, ...] = ()
    restrict: bool = False
    weights: tuple[float, ...] = ()
    weighted_members: tuple[tuple[str, float], ...] = ()
    invert: bool = False
    bind: tuple[float, ...] = IDENTITY
    center: tuple[float, ...] = (0.0, 0.0, 0.0)
    radius: float = 0.0
    falloff: str = "NONE"
    uniform: bool = False
    custom: tuple[float, ...] = (0.0, 0.0, 1.0, 1.0)
    custom_handles: tuple[str, ...] = ()
    custom_extrapolate: bool = True
    shrinkwrap: Shrinkwrap | None = None
    subdivision: int | None = None
    displacement: tuple[float, ...] | None = None

    def __post_init__(self) -> None:
        validate_matrix(self.bind)
        finite(self.center, 3)
        if not 0 <= self.strength <= 1:
            raise ValueError("Invalid deformer kind or strength.")
        validate_deformer_settings(self)
        validate_membership(self)
        validate_falloff(self.falloff, self.custom)
        validate_custom_handles(self.custom, self.custom_handles)
        if not isfinite(self.radius) or self.radius < 0:
            raise ValueError("Hook radius must be finite and nonnegative.")


def validate_deformer_settings(value: Deformer) -> None:
    settings = {
        "SHRINKWRAP": value.shrinkwrap,
        "SUBDIVISION": value.subdivision,
        "DISPLACE": value.displacement,
    }
    if value.kind not in (*settings, "HOOK", "LATTICE"):
        raise ValueError("Unknown construction modifier.")
    if any((value.kind == kind) != (setting is not None) for kind, setting in settings.items()):
        raise ValueError("Construction modifier requires its own settings.")
    if value.kind in settings and value.control:
        raise ValueError("This modifier has no shared control.")
    validate_geometry_modifier(value)


def validate_geometry_modifier(value: Deformer) -> None:
    if value.subdivision is not None and not integer(value.subdivision, 0, 5):
        raise ValueError("Simple subdivision supports zero to five levels.")
    if value.displacement is not None:
        finite(value.displacement, 3)
    if value.kind == "SUBDIVISION" and (value.weights or value.strength != 1 or value.invert):
        raise ValueError("Subdivision has no point weights or strength.")


def validate_membership(binding: Deformer) -> None:
    indices = binding.indices
    if any(not integer(i, 0, 2147483647) for i in indices) or len(set(indices)) != len(indices):
        raise ValueError("Deformer membership must contain unique nonnegative indices.")
    validate_weights(binding.weights)
    validate_weights(tuple(weight for _, weight in binding.weighted_members))
    keys = [key for key, _ in binding.weighted_members]
    for members in (binding.members, keys):
        if len(set(members)) != len(members):
            raise ValueError("Stable curve membership must be unique.")
        if any(m.rsplit(":", 1)[-1] not in ("left", "point", "right") for m in members):
            raise ValueError("Invalid stable curve membership.")


FALLOFF_TYPES = {
    "NONE",
    "CURVE",
    "SMOOTH",
    "SPHERE",
    "ROOT",
    "SHARP",
    "LINEAR",
    "CONSTANT",
    "INVERSE_SQUARE",
}


def validate_custom_handles(points: tuple[float, ...], handles: tuple[str, ...]) -> None:
    if handles and (
        len(handles) != len(points) // 2
        or any(mode not in ("AUTO", "VECTOR", "AUTO_CLAMPED") for mode in handles)
    ):
        raise ValueError("Every custom falloff point needs a valid handle type.")


def validate_falloff(kind: str, custom: tuple[float, ...]) -> None:
    if kind not in FALLOFF_TYPES:
        raise ValueError("Unknown Hook falloff.")
    if len(custom) < 4 or len(custom) % 2 or not all(map(isfinite, custom)):
        raise ValueError("Custom falloff requires finite XY pairs.")
    if any(a >= b for a, b in zip(custom[::2], custom[2::2], strict=False)):
        raise ValueError("Custom falloff X coordinates must increase.")


@dataclass(frozen=True, slots=True)
class Thickness:
    enabled: bool = True
    thickness: float = 0.01
    offset: float = -1.0
    rim: bool = True
    rim_only: bool = False
    even: bool = False
    high_quality_normals: bool = False
    flip: bool = False
    clamp: float = 0.0
    angle_clamp: bool = False
    weights: tuple[float, ...] = ()
    invert: bool = False
    minimum: float = 0.0

    def __post_init__(self) -> None:
        finite((self.thickness, self.offset, self.clamp, self.minimum), 4)
        if not -1 <= self.offset <= 1 or not 0 <= self.clamp <= 2 or not 0 <= self.minimum <= 1:
            raise ValueError("Invalid Simple Solidify settings.")
        validate_weights(self.weights)


@dataclass(frozen=True, slots=True)
class Control:
    name: str
    kind: str = "HOOK"
    id: str = field(default_factory=identity)
    follow: str = ""
    owners: tuple[str, ...] = ()
    matrix: tuple[float, ...] = IDENTITY
    points: tuple[tuple[float, ...], ...] = ()
    resolution: tuple[int, ...] = (2, 2, 2)
    interpolation: tuple[str, ...] = ("BSPLINE", "BSPLINE", "BSPLINE")
    outside: bool = False
    weights: tuple[float, ...] = ()
    deformers: tuple[Deformer, ...] = ()
    generation: int = 0
    result: ControlResult = field(default_factory=ControlResult)

    def __post_init__(self) -> None:
        validate_matrix(self.matrix)
        if self.kind not in ("HOOK", "LATTICE") or not self.name.strip():
            raise ValueError("Invalid shared control.")
        validate_cage(self)
        if len(self.interpolation) != 3 or any(
            i not in ("LINEAR", "CARDINAL", "CATMULL_ROM", "BSPLINE") for i in self.interpolation
        ):
            raise ValueError("Unknown lattice interpolation.")
        for point in self.points:
            finite(point, 3)


def validate_cage(control: Control) -> None:
    if len(control.resolution) != 3 or any(not integer(n, 1, 64) for n in control.resolution):
        raise ValueError("Lattice resolution must be between 1 and 64 per axis.")
    count = control.resolution[0] * control.resolution[1] * control.resolution[2]
    if count > 32000 or (control.kind == "LATTICE" and len(control.points) != count):
        raise ValueError("Lattice points must match resolution, at most 32000 points.")
    validate_weights(control.weights, len(control.points))
