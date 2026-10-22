"""Shortcut wrappers and driver intent, separate from property storage and results."""

from dataclasses import dataclass, field
from uuid import NAMESPACE_URL, uuid4, uuid5

from .numeric_properties import PropertyRef, validate_number
from .results import ReadRevision


@dataclass(frozen=True, slots=True)
class DescendantOverride:
    target: str
    parent_anchor: str = "KEEP"
    child_anchor: str = "KEEP"
    follow_rotation: str = "KEEP"
    strategy: str = "KEEP"

    def __post_init__(self) -> None:
        allowed = (
            (self.parent_anchor, ("KEEP", "SURFACE_NEAREST", "OBJECT_ORIGIN")),
            (self.child_anchor, ("KEEP", "FACE_CENTER", "VERTEX_NEAREST", "OBJECT_ORIGIN")),
            (self.follow_rotation, ("KEEP", "ENABLED", "DISABLED")),
            (self.strategy, ("KEEP", "AUTO", "STABLE_SURFACE", "DEFORMATION_FLOW")),
        )
        if not self.target or any(value not in choices for value, choices in allowed):
            raise ValueError("Invalid shortcut descendant attachment policy.")


@dataclass(frozen=True, slots=True)
class AttachmentPolicy:
    backsolve: bool = False
    descendants: tuple[DescendantOverride, ...] = ()

    def __post_init__(self) -> None:
        if type(self.backsolve) is not bool:
            raise ValueError("Backsolve must be Boolean.")
        if len({v.target for v in self.descendants}) != len(self.descendants):
            raise ValueError("A descendant can have only one shortcut override.")


def implicit_identity(reference: PropertyRef) -> str:
    address = repr((reference.target, reference.path, reference.component))
    return str(uuid5(NAMESPACE_URL, "anthroforge:shortcut:" + address))


@dataclass(frozen=True, slots=True)
class Shortcut:
    reference: PropertyRef
    label: str = ""
    exposed: bool = False
    policy: AttachmentPolicy = field(default_factory=AttachmentPolicy)

    @property
    def id(self) -> str:
        return implicit_identity(self.reference)


@dataclass(frozen=True, slots=True)
class FormulaInput:
    name: str
    property: PropertyRef | None = None
    driver: str = ""

    def __post_init__(self) -> None:
        if not self.name.isidentifier() or self.name.startswith("_"):
            raise ValueError("Formula inputs require public identifiers.")
        if (self.property is None) == (not self.driver):
            raise ValueError("An input refers to one property or driving shortcut.")


@dataclass(frozen=True, slots=True)
class DrivingFormula:
    target: PropertyRef
    expression: str
    inputs: tuple[FormulaInput, ...] = ()
    enabled: bool = True
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        if len(self.expression) > 8192:
            raise ValueError("A formula supports at most 8192 characters.")
        names = [item.name for item in self.inputs]
        if len(set(names)) != len(names) or "value" in names:
            raise ValueError("Formula input names must be unique; value is reserved.")


@dataclass(frozen=True, slots=True)
class DrivingShortcut:
    label: str = "Driver"
    value: int | float = 0.0
    numeric_type: str = "REAL"
    dimension: str = "SCALAR"
    formulas: tuple[DrivingFormula, ...] = ()
    exposed: bool = True
    policy: AttachmentPolicy = field(default_factory=AttachmentPolicy)
    id: str = field(default_factory=lambda: str(uuid4()))
    generation: int = 0

    def __post_init__(self) -> None:
        if self.numeric_type not in ("INTEGER", "REAL"):
            raise ValueError("Driving values require INTEGER or REAL type.")
        if self.dimension not in ("SCALAR", "LENGTH", "ANGLE"):
            raise ValueError("Unknown numerical dimension.")
        validate_number(self.value, self.numeric_type)


@dataclass(frozen=True, slots=True)
class FormulaResult:
    formula: str
    value: int | float | tuple[int | float, ...] | None = None
    status: str = "pending"
    error: str = ""
    revision: int = 0
    inputs: tuple[ReadRevision, ...] = ()
    pending: tuple[str, ...] = ()
