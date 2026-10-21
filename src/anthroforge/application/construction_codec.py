"""Portable construction records. JSON arrays become immutable tuples at this boundary."""

from typing import Any

from anthroforge.core.construction import (
    BodyPiece,
    Control,
    Curve,
    CurvePoint,
    Deformer,
    Primitive,
    ResolvedPrimitive,
    Target,
    Thickness,
)
from anthroforge.core.curve_engines import fields as curve_fields
from anthroforge.core.curve_uses import CurveUse
from anthroforge.core.results import ControlResult, EvaluationResult, ReadRevision
from anthroforge.core.shrinkwrap import Shrinkwrap
from anthroforge.core.surface_references import SurfaceReference


def tuples(data: dict[str, Any]) -> dict[str, Any]:
    return {key: immutable(value) for key, value in data.items()}


def immutable(value: Any) -> Any:
    return tuple(immutable(item) for item in value) if isinstance(value, list) else value


def curve(data: dict[str, Any]) -> Curve:
    state = curve_fields(tuples(data))
    state["points"] = tuple(CurvePoint(**tuples(p)) for p in state["points"])
    state["result"] = EvaluationResult(**result_fields(state.get("result", {})))
    return Curve(**state)


def primitive(data: dict[str, Any] | None) -> Primitive | None:
    if data is None:
        return None
    state = tuples(data)
    state["curves"] = tuple(CurveUse(**tuples(c)) for c in state.get("curves", ()))
    state["pieces"] = tuple(BodyPiece(**p) for p in state.get("pieces", ()))
    return Primitive(**state)


def resolved_primitive(data: dict[str, Any]) -> ResolvedPrimitive:
    state = tuples(data)
    state["curves"] = tuple(curve(c) for c in state.get("curves", ()))
    state["pieces"] = tuple(BodyPiece(**p) for p in state.get("pieces", ()))
    return ResolvedPrimitive(**state)


def deformer(data: dict[str, Any]) -> Deformer:
    state = tuples(data)
    state["target"] = Target(**state["target"])
    if state.get("shrinkwrap"):
        settings = dict(state["shrinkwrap"])
        settings["surface"] = SurfaceReference(**settings["surface"])
        state["shrinkwrap"] = Shrinkwrap(**settings)
    return Deformer(**state)


def control(data: dict[str, Any]) -> Control:
    state = tuples(data)
    state["deformers"] = tuple(deformer(d) for d in state.get("deformers", ()))
    state["result"] = ControlResult(**result_fields(state.get("result", {})))
    return Control(**state)


def entity_construction(data: dict[str, Any]) -> dict[str, Any]:
    data = tuples(data)
    data["primitive"] = primitive(data.get("primitive"))
    data["deformers"] = tuple(deformer(d) for d in data.get("deformers", ()))
    thickness = data.get("thickness")
    data["thickness"] = Thickness(**tuples(thickness)) if thickness else None
    data["result"] = EvaluationResult(**result_fields(data.get("result", {})))
    return migrate_imported(data)


def migrate_imported(data: dict[str, Any]) -> dict[str, Any]:
    if data.get("asset") and data["primitive"] is None:
        data["primitive"] = Primitive("IMPORTED", source=data["asset"])
        data["result"] = EvaluationResult(asset=data["asset"])
    return data


def result_fields(data: dict[str, Any]) -> dict[str, Any]:
    state = tuples(data)
    state["inputs"] = tuple(ReadRevision(**tuples(entry)) for entry in data.get("inputs", ()))
    return state
