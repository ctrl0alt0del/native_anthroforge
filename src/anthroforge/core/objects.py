"""Common authored construction state; relationships retain distinct meanings."""

from dataclasses import dataclass, field
from uuid import uuid4

from .entities import IDENTITY, validate_matrix
from .results import EvaluationResult


@dataclass(frozen=True, slots=True, kw_only=True)
class ConstructionObject:
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = "Object"
    matrix: tuple[float, ...] = IDENTITY
    parent: str = ""
    owners: tuple[str, ...] = ()
    update_mode: str = "INHERIT"
    generation: int = 0
    pose_revision: int = 0
    construction_revision: int = 0
    result: EvaluationResult = field(default_factory=EvaluationResult)

    def __post_init__(self) -> None:
        if not self.id or not self.name.strip():
            raise ValueError("Object identity and name must not be empty.")
        validate_matrix(self.matrix)
        if self.update_mode not in ("INHERIT", "LIVE", "ON_RELEASE", "MANUAL"):
            raise ValueError("Invalid object update mode.")
        if len(set(self.owners)) != len(self.owners) or any(not v for v in self.owners):
            raise ValueError("Workspace associations must be unique anatomical identities.")
        if min(self.generation, self.pose_revision, self.construction_revision) < 0:
            raise ValueError("Object revisions must be nonnegative.")
