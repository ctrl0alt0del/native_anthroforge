"""Document-owned skin construction; no authored anatomical wrapper or native handles."""

from dataclasses import dataclass, field
from math import isfinite

from .results import EvaluationResult


def bounded(name: str, value: float, lower: float, upper: float) -> None:
    if isinstance(value, bool) or not isfinite(value) or not lower <= value <= upper:
        raise ValueError(f"{name} must be finite and between {lower} and {upper}.")


def choice(name: str, value: str, allowed: tuple[str, ...]) -> None:
    if value not in allowed:
        raise ValueError(f"Unsupported {name}: {value}.")


@dataclass(frozen=True, slots=True)
class EnvelopeSettings:
    minimum_offset_ratio: float = 1.189424086064195 / 220.0
    collagen_depth_ratio: float = (3.1717975628378534 - 1.189424086064195) / 220.0
    collagen_core_ratio: float = 4.75769634425678 / 220.0
    collagen_falloff_ratio: float = (13.480139642060877 - 4.75769634425678) / 220.0
    gap_limit_ratio: float = 0.005
    gap_strength: float = 1.0

    def __post_init__(self) -> None:
        limits = (0.02, 0.04, 0.05, 0.10, 1.0, 1.0)
        for name, limit in zip(self.__dataclass_fields__, limits, strict=True):
            bounded(name, getattr(self, name), 0, limit)


@dataclass(frozen=True, slots=True)
class TopologySettings:
    backend: str = "QUADWILD"
    target_quads: int = 8100
    refinement: str = "NONE"
    symmetry: str = "X"
    plane_origin: tuple[float, float, float] = (0.0, 0.0, 0.0)
    plane_normal: tuple[float, float, float] = (1.0, 0.0, 0.0)

    def __post_init__(self) -> None:
        choice("topology backend", self.backend, ("QUADWILD", "INSTANT"))
        choice("refinement", self.refinement, ("NONE", "MUSCLE_PROXIMITY"))
        choice("symmetry", self.symmetry, ("NONE", "X", "Y", "Z", "CUSTOM"))
        integer("target quads", self.target_quads, 1000, 500000)
        for vector in (self.plane_origin, self.plane_normal):
            if len(vector) != 3 or not all(isfinite(v) for v in vector):
                raise ValueError("Skin symmetry plane requires finite XYZ values.")
        if sum(v * v for v in self.plane_normal) < 1e-24:
            raise ValueError("Skin symmetry plane requires a nonzero normal.")


def integer(name: str, value: int, lower: int, upper: int) -> None:
    if type(value) is not int:
        raise ValueError(f"{name} requires an integer.")
    bounded(name, value, lower, upper)


@dataclass(frozen=True, slots=True)
class DeformationSettings:
    method: str = "LE"
    proxy_resolution: int = 48
    constraint_strength: float = 100.0
    fast_handles: int = 128

    def __post_init__(self) -> None:
        choice("skin deformation", self.method, ("LE", "FAST"))
        integer("proxy resolution", self.proxy_resolution, 8, 256)
        integer("FAST handles", self.fast_handles, 5, 1024)
        if not isfinite(self.constraint_strength) or self.constraint_strength <= 0:
            raise ValueError("Constraint strength must be finite and positive.")


@dataclass(frozen=True, slots=True)
class SkinContributor:
    owner: str
    collagen_mode: str = "AUTO"
    collagen: float = 1.0
    painted: str = ""
    gap_mode: str = "INHERIT"
    gap_limit_ratio: float = 0.005
    gap_strength: float = 1.0
    density_mode: str = "INHERIT"
    target_quads: int = 1000
    flow: bool = False

    def __post_init__(self) -> None:
        if not self.owner:
            raise ValueError("Skin contributor requires a source identity.")
        choice("collagen mode", self.collagen_mode, ("AUTO", "UNIFORM", "PAINTED"))
        choice("gap mode", self.gap_mode, ("INHERIT", "OVERRIDE"))
        choice("density mode", self.density_mode, ("INHERIT", "SUBTREE_BUDGET"))
        bounded("collagen", self.collagen, 0, 1)
        bounded("gap limit", self.gap_limit_ratio, 0, 1)
        bounded("gap strength", self.gap_strength, 0, 1)
        integer("subtree target quads", self.target_quads, 100, 500000)


@dataclass(frozen=True, slots=True)
class FittedShortcut:
    id: str
    shortcut: str
    reference: str
    data: str
    source_revision: int
    stale: bool = False


@dataclass(frozen=True, slots=True)
class SkinStage(EvaluationResult):
    data: str = ""


@dataclass(frozen=True, slots=True)
class Skin:
    envelope_settings: EnvelopeSettings = field(default_factory=EnvelopeSettings)
    topology_settings: TopologySettings = field(default_factory=TopologySettings)
    deformation_settings: DeformationSettings = field(default_factory=DeformationSettings)
    contributors: tuple[SkinContributor, ...] = ()
    envelope: SkinStage = field(default_factory=SkinStage)
    topology: SkinStage = field(default_factory=SkinStage)
    final: SkinStage = field(default_factory=SkinStage)
    reference: str = ""
    fits: tuple[FittedShortcut, ...] = ()
    construction_stale: bool = False
    revision: int = 0

    def __post_init__(self) -> None:
        if len({item.owner for item in self.contributors}) != len(self.contributors):
            raise ValueError("Skin contributor settings must have unique owners.")
        if len({item.id for item in self.fits}) != len(self.fits):
            raise ValueError("Fitted shortcut results must have unique identities.")


def effective_collagen(settings: SkinContributor, name: str) -> float:
    if settings.collagen_mode != "AUTO":
        return settings.collagen
    return 0.0 if any(term in name.lower() for term in ("ear", "cartilage", "nasal")) else 1.0
