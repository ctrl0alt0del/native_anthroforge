"""Anatomical tissue composes construction and strategies without anatomical subclasses."""

from dataclasses import dataclass, field

from .objects import ObjectRecord
from .results import EvaluationResult
from .tissue_base import TissueBaseState
from .tissue_constraints import TissueConstraint, TissueField
from .tissue_diagnostics import TissueDiagnostic
from .tissue_material import TissueMaterialState
from .tissue_settings import TissueCrop, TissuePart, TissueRelaxation
from .tissue_stacking import StackPlan, StackRelationship, StackSettings, validate_group


@dataclass(frozen=True, slots=True)
class TissueVCP(ObjectRecord):
    source: str = ""
    classification: str = "MUSCLE"
    preset: str = "MUSCLE"
    color: str = "#ad625e"
    parts: tuple[TissuePart, ...] = (TissuePart(),)
    both_sides: bool = False
    reverse: bool = False
    resolution: int = 24
    relaxation: TissueRelaxation = field(default_factory=TissueRelaxation)
    crop: TissueCrop = field(default_factory=TissueCrop)
    fields: tuple[TissueField, ...] = ()
    constraints: tuple[TissueConstraint, ...] = ()
    stacking: bool = False
    stack_settings: StackSettings = field(default_factory=StackSettings)
    stack_relationships: tuple[StackRelationship, ...] = ()
    stack_plan: StackPlan = field(default_factory=StackPlan)
    group: str = ""
    base_state: TissueBaseState = field(default_factory=TissueBaseState)
    diagnostics: tuple[TissueDiagnostic, ...] = ()
    base_revision: int = 0
    rest_revision: int = 0
    intrinsic_revision: int = 0
    plan_revision: int = 0
    final_revision: int = 0
    base_result: EvaluationResult = field(default_factory=EvaluationResult)
    rest_result: EvaluationResult = field(default_factory=EvaluationResult)
    intrinsic_result: EvaluationResult = field(default_factory=EvaluationResult)
    plan_result: EvaluationResult = field(default_factory=EvaluationResult)
    final_result: EvaluationResult = field(default_factory=EvaluationResult)
    rest_material: TissueMaterialState | None = None
    intrinsic_material: TissueMaterialState | None = None
    final_material: TissueMaterialState | None = None

    def __post_init__(self) -> None:
        ObjectRecord.__post_init__(self)
        validate_group(self.group)
        if not self.source or not self.classification.strip():
            raise ValueError("Tissue needs a construction source and classification.")
        if not self.parts or self.parts[0].id != "main":
            raise ValueError("Tissue requires its main part first.")
        if len({p.id for p in self.parts}) != len(self.parts):
            raise ValueError("Tissue part identities must be unique.")
        if len({f.name for f in self.fields}) != len(self.fields):
            raise ValueError("Tissue fields must have unique names.")
        if not 3 <= self.resolution <= 256:
            raise ValueError("Tissue resolution must be between 3 and 256.")
