"""Immutable construction provenance belonging to an accepted tissue result."""

from dataclasses import dataclass, field

from .entities import IDENTITY
from .tissue_base import TissueBaseState
from .tissue_constraints import TissueConstraint, TissueField
from .tissue_settings import TissueCrop, TissuePart, TissueRelaxation


@dataclass(frozen=True, slots=True)
class TissueMaterialState:
    base: str = ""
    rest: str = ""
    own: str = ""
    final: str = ""
    frame: tuple[float, ...] = IDENTITY
    base_state: TissueBaseState = field(default_factory=TissueBaseState)
    parts: tuple[TissuePart, ...] = (TissuePart(),)
    both_sides: bool = False
    reverse: bool = False
    crop: TissueCrop = field(default_factory=TissueCrop)
    crop_base: str = ""
    relaxation: TissueRelaxation = field(default_factory=TissueRelaxation)
    fields: tuple[TissueField, ...] = ()
    constraints: tuple[TissueConstraint, ...] = ()
