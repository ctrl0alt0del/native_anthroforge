"""Typed tissue strategies; anatomical labels never select numerical algorithms."""

from dataclasses import dataclass, field
from math import isfinite

INFLATION_MODES = frozenset(
    ("CTRL_POINT", "DISTRIBUTED", "SECTION_PROFILE", "RADIAL", "PROFILE", "NORMAL")
)


def finite_range(value: float, low: float, high: float, label: str) -> None:
    if not isfinite(value) or not low <= value <= high:
        raise ValueError(f"{label} must be finite and within {low}..{high}.")


def vector(values: tuple[float, ...], size: int, label: str) -> None:
    if len(values) != size or not all(map(isfinite, values)):
        raise ValueError(f"{label} requires {size} finite values.")


@dataclass(frozen=True, slots=True)
class SectionProfile:
    depths: tuple[float, ...] = (0.01, 0.02, 0.02, 0.01)
    peaks: tuple[float, ...] = (0.5, 0.5, 0.5, 0.5)
    roundness: float = 1.0
    direction: str = "SMOOTH"
    initialized: bool = False

    def __post_init__(self) -> None:
        vector(self.depths, 4, "Profile depths")
        vector(self.peaks, 4, "Profile peaks")
        for value in self.depths:
            finite_range(value, 0, 10, "Profile depth")
        for value in self.peaks:
            finite_range(value, 0.1, 0.9, "Profile peak")
        finite_range(self.roundness, 0.25, 4, "Profile roundness")
        if self.direction not in ("LOCAL", "SMOOTH", "SECTION"):
            raise ValueError("Unsupported profile direction.")


@dataclass(frozen=True, slots=True)
class HeightSmoothing:
    mode: str = "OFF"
    radius: float = 0.2
    strength: float = 0.8
    maximum_change: float = 0.05

    def __post_init__(self) -> None:
        if self.mode not in ("OFF", "HEIGHT"):
            raise ValueError("Unsupported height smoothing mode.")
        for value in (self.radius, self.strength, self.maximum_change):
            finite_range(value, 0, 1000, "Smoothing setting")


@dataclass(frozen=True, slots=True)
class TissueInflation:
    mode: str = "DISTRIBUTED"
    enabled: bool = True
    amount: float = 0.02
    minimum: float = 0.0
    scale: tuple[float, ...] = (1.0, 1.0, 1.0)
    power: float = 1.0
    width: float = 0.08
    segments: int = 11
    endpoint_taper: float = 0.12
    falloff: str = "SMOOTH"
    falloff_radius: float = 1.0
    direction_depth: float = 0.0
    boundary_strength: float = 1.0
    boundary_band: float = 0.1
    boundary_power: float = 1.0
    length_taper: float = 0.1
    control: tuple[float, ...] = ()
    profile: SectionProfile = field(default_factory=SectionProfile)

    def __post_init__(self) -> None:
        validate_inflation(self)


def validate_inflation(item: TissueInflation) -> None:
    if item.mode not in INFLATION_MODES:
        raise ValueError("Unsupported tissue inflation mode.")
    if item.falloff not in ("GAUSSIAN", "LINEAR", "SMOOTH", "SMOOTHSTEP"):
        raise ValueError("Unsupported inflation falloff.")
    vector(item.scale, 3, "Radial scale")
    if min(item.scale) <= 0 or not 3 <= item.segments <= 256:
        raise ValueError("Positive radial scales and 3..256 profile segments are required.")
    validate_inflation_values(item)
    if item.minimum > item.amount:
        raise ValueError("Minimum thickness exceeds maximum thickness.")
    if item.control:
        vector(item.control, 3, "Inflation control")


def validate_inflation_values(item: TissueInflation) -> None:
    lengths = (
        item.amount,
        item.minimum,
        item.falloff_radius,
        item.boundary_band,
        item.length_taper,
    )
    for value in lengths:
        finite_range(value, 0, 1000, "Inflation length")
    for value in (item.power, item.width, item.boundary_power):
        finite_range(value, 1e-12, 1000, "Inflation parameter")
    finite_range(item.endpoint_taper, 0, 1, "Endpoint taper")
    finite_range(item.boundary_strength, 0, 1, "Boundary strength")
    finite_range(item.direction_depth, -1000, 1000, "Direction depth")


@dataclass(frozen=True, slots=True)
class TissueSide:
    inflation: TissueInflation = field(default_factory=TissueInflation)
    smoothing: HeightSmoothing = field(default_factory=HeightSmoothing)


@dataclass(frozen=True, slots=True)
class TissuePart:
    id: str = "main"
    a: TissueSide = field(default_factory=TissueSide)
    b: TissueSide = field(default_factory=TissueSide)
    connector_width: float = 0.25
    connector_fullness: float = 0.0

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Tissue part identity must not be empty.")
        finite_range(self.connector_width, 1e-6, 0.499999, "Connector width")
        finite_range(self.connector_fullness, -1000, 1000, "Connector fullness")


@dataclass(frozen=True, slots=True)
class TissueRelaxation:
    mode: str = "NONE"
    gravity: tuple[float, ...] = (0.0, 0.0, -1.0)
    sagginess: float = 0.35
    sag_limit: float = 0.0
    shape_retention: float = 0.5
    volume_retention: float = 0.9
    slack: float = 0.0
    iterations: int = 24
    constraint_passes: int = 2
    tolerance: float = 1e-5

    def __post_init__(self) -> None:
        if self.mode not in ("NONE", "GEOMETRIC", "STATIC_PBD"):
            raise ValueError("Unsupported tissue relaxation mode.")
        vector(self.gravity, 3, "Gravity")
        for value in (self.sagginess, self.shape_retention, self.volume_retention, self.slack):
            finite_range(value, 0, 1, "Material setting")
        finite_range(self.sag_limit, 0, 1000, "Sag limit")
        finite_range(self.tolerance, 1e-12, 1, "Tolerance")
        if not 1 <= self.iterations <= 10000 or not 1 <= self.constraint_passes <= 100:
            raise ValueError("Invalid tissue iteration budget.")


@dataclass(frozen=True, slots=True)
class TissueCrop:
    enabled: bool = False
    origin: tuple[float, ...] = (0.0, 0.0, 0.0)
    normal: tuple[float, ...] = (1.0, 0.0, 0.0)
    positive: bool = True

    def __post_init__(self) -> None:
        vector(self.origin, 3, "Crop origin")
        vector(self.normal, 3, "Crop normal")
        if not any(self.normal):
            raise ValueError("Crop normal must be nonzero.")
