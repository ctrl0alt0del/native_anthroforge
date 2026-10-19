"""Schema-four tissue and binding records without runtime handles or class names."""

from typing import Any

from anthroforge.core.entities import Attachment
from anthroforge.core.points import Anchor, Point
from anthroforge.core.results import EvaluationResult
from anthroforge.core.surface_references import SurfaceBinding, SurfaceReference
from anthroforge.core.tissue_base import TissueBaseState
from anthroforge.core.tissue_constraints import TissueConstraint, TissueField
from anthroforge.core.tissue_diagnostics import TissueDiagnostic
from anthroforge.core.tissue_settings import (
    HeightSmoothing,
    SectionProfile,
    TissueCrop,
    TissueInflation,
    TissuePart,
    TissueRelaxation,
    TissueSide,
)
from anthroforge.core.tissues import TissueVCP

from .construction_codec import result_fields, tuples


def binding(data: dict[str, Any]) -> SurfaceBinding:
    state = dict(data)
    state["reference"] = SurfaceReference(**state["reference"])
    state["attachment"] = Attachment(**tuples(state.get("attachment", {})))
    return SurfaceBinding(**state)


def point(kind: str, state: dict[str, Any]) -> Point:
    if kind == "anchor":
        state["binding"] = binding(state["binding"])
        return Anchor(**state)
    return Point(**state)


def inflation(data: dict[str, Any]) -> TissueInflation:
    state = tuples(data)
    state["profile"] = SectionProfile(**tuples(state.get("profile", {})))
    return TissueInflation(**state)


def side(data: dict[str, Any]) -> TissueSide:
    return TissueSide(
        inflation(data.get("inflation", {})),
        HeightSmoothing(**data.get("smoothing", {})),
    )


def part(data: dict[str, Any]) -> TissuePart:
    state = dict(data, a=side(data.get("a", {})), b=side(data.get("b", {})))
    return TissuePart(**state)


def constraint(data: dict[str, Any]) -> TissueConstraint:
    state = tuples(data)
    reference = state.get("reference")
    state["reference"] = SurfaceReference(**reference) if reference else None
    return TissueConstraint(**state)


def tissue(state: dict[str, Any]) -> TissueVCP:
    completed_states(state)
    state["diagnostics"] = tuple(TissueDiagnostic(**row) for row in state.get("diagnostics", ()))
    state["base_state"] = TissueBaseState(**tuples(state.get("base_state", {})))
    state["parts"] = tuple(part(row) for row in state.get("parts", (dict(id="main"),)))
    state["relaxation"] = TissueRelaxation(**tuples(state.get("relaxation", {})))
    state["crop"] = TissueCrop(**tuples(state.get("crop", {})))
    state["fields"] = tuple(TissueField(**tuples(row)) for row in state.get("fields", ()))
    state["constraints"] = tuple(constraint(row) for row in state.get("constraints", ()))
    return TissueVCP(**state)


def completed_states(state: dict[str, Any]) -> None:
    from . import tissue_stack_codec
    from .tissue_material_codec import decode

    for name in ("base_result", "rest_result", "intrinsic_result", "plan_result", "final_result"):
        state[name] = EvaluationResult(**result_fields(state.get(name, {})))
    for name in ("rest_material", "intrinsic_material", "final_material"):
        state[name] = decode(state.get(name))
    tissue_stack_codec.decode(state)
