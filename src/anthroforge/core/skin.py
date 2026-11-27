"""Document-owned skin construction; no authored anatomical wrapper or native handles."""

from dataclasses import dataclass, field
from math import isfinite

from .results import EvaluationResult, ReadRevision
from .skin_checkpoints import Checkpoint
from .skin_draft import AppliedDraftConfiguration, BuilderConfiguration, DraftSettings
from .skin_field import EnvelopeSettings as EnvelopeSettings
from .skin_field import effective_collagen as effective_collagen
from .skin_validation import bounded as bounded
from .skin_validation import choice as choice
from .skin_validation import integer as integer


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
    density_mode: str = "INHERIT"
    target_quads: int = 1000
    flow: bool = False

    def __post_init__(self) -> None:
        if not self.owner:
            raise ValueError("Skin contributor requires a source identity.")
        choice("density mode", self.density_mode, ("INHERIT", "SUBTREE_BUDGET"))
        integer("subtree target quads", self.target_quads, 100, 500000)


@dataclass(frozen=True, slots=True)
class FittedShortcut:
    id: str
    shortcut: str
    reference: str
    data: str
    source_revision: int
    stale: bool = False
    inputs: tuple[ReadRevision, ...] = ()
    definitions: str = ""


@dataclass(frozen=True, slots=True)
class SkinStage(EvaluationResult):
    data: str = ""


@dataclass(frozen=True, slots=True)
class Skin:
    topology_settings: TopologySettings = field(default_factory=TopologySettings)
    deformation_settings: DeformationSettings = field(default_factory=DeformationSettings)
    contributors: tuple[SkinContributor, ...] = ()
    envelope: SkinStage = field(default_factory=SkinStage)
    topology: SkinStage = field(default_factory=SkinStage)
    pending_topology: SkinStage = field(default_factory=SkinStage)
    final: SkinStage = field(default_factory=SkinStage)
    reference: str = ""
    reference_sources: tuple[str, ...] = ()
    build_error: str = ""
    fits: tuple[FittedShortcut, ...] = ()
    construction_stale: bool = False
    revision: int = 0
    draft_settings: DraftSettings = field(default_factory=DraftSettings)
    update_mode: str = "DRAFT"
    applied_draft: AppliedDraftConfiguration | None = None
    migration_draft: BuilderConfiguration | None = None
    checkpoints: tuple[Checkpoint, ...] = ()

    def __post_init__(self) -> None:
        choice("skin update mode", self.update_mode, ("DRAFT", "FINAL"))
        if len({item.owner for item in self.contributors}) != len(self.contributors):
            raise ValueError("Skin contributor settings must have unique owners.")
        if len({item.id for item in self.fits}) != len(self.fits):
            raise ValueError("Fitted shortcut results must have unique identities.")
