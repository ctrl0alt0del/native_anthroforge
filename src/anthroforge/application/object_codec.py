"""Explicit construction record variants; no native handles or Python class names in files."""

from dataclasses import asdict
from typing import Any

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_engines import fields as curve_fields
from anthroforge.core.curve_uses import CurveUse
from anthroforge.core.entities import Attachment
from anthroforge.core.fiber_support_policy import FiberSupportPolicy
from anthroforge.core.fibers import Fiber, FiberBinding, FiberEdit
from anthroforge.core.membranes import Membrane
from anthroforge.core.mirroring import SymmetricHalf
from anthroforge.core.object_registry import Authored
from anthroforge.core.points import Anchor, Point
from anthroforge.core.reference_images import ImageCalibration, ReferenceImage
from anthroforge.core.results import EvaluationResult
from anthroforge.core.surface_branches import SurfaceBranch
from anthroforge.core.surface_references import SurfaceReference
from anthroforge.core.surfaces import Surface, SurfaceAlignment
from anthroforge.core.tissues import TissueVCP

from . import surface_reference_codec, tissue_codec
from .construction_codec import result_fields, tuples

KINDS = {
    Curve: "curve",
    Fiber: "fiber",
    Surface: "surface",
    ReferenceImage: "reference_image",
    Point: "point",
    Anchor: "anchor",
    Membrane: "membrane",
    TissueVCP: "tissue",
}


def encode(item: Authored) -> dict[str, Any]:
    return {"kind": KINDS[type(item)], "state": asdict(item)}


def decode(data: dict[str, Any]) -> Authored:
    kind, state = data["kind"], tuples(data["state"])
    state["result"] = EvaluationResult(**result_fields(state.get("result", {})))
    if kind in ("curve", "fiber"):
        return decode_curve(kind, state)
    if kind in ("surface", "membrane"):
        return decode_surface(kind, state)
    if kind in ("point", "anchor"):
        return tissue_codec.point(kind, state)
    if kind == "tissue":
        return tissue_codec.tissue(state)
    if kind == "reference_image":
        return decode_image(state)
    raise ValueError(f"Unsupported construction object kind: {kind}")


def decode_surface(kind: str, state: dict[str, Any]) -> Surface:
    state["mirror_plane"] = SymmetricHalf(**state.get("mirror_plane", {}))
    state["curves"] = tuple(CurveUse(**tuples(use)) for use in state["curves"])
    state["alignment"] = tuple(
        SurfaceAlignment(**tuples(row)) for row in state.get("alignment", ())
    )
    state["branches"] = tuple(SurfaceBranch(**tuples(row)) for row in state.get("branches", ()))
    return (Membrane if kind == "membrane" else Surface)(**state)


def decode_image(state: dict[str, Any]) -> ReferenceImage:
    calibration = state.get("calibration")
    state["calibration"] = ImageCalibration(**tuples(calibration)) if calibration else None
    return ReferenceImage(**state)


def decode_curve(kind: str, state: dict[str, Any]) -> Curve:
    state = curve_fields(state)
    state["symmetric"] = SymmetricHalf(**state["symmetric"]) if state.get("symmetric") else None
    state["points"] = tuple(CurvePoint(**tuples(point)) for point in state["points"])
    if kind == "fiber":
        state["bindings"] = tuple(decode_binding(binding) for binding in state["bindings"])
        state["edit"] = decode_edit(state.get("edit"))
        state["supports"] = tuple(surface_reference_codec.capture(row) for row in state["supports"])
        state["support_policy"] = decode_support_policy(state.get("support_policy", {}))
        return Fiber(**state)
    return Curve(**state)


def decode_support_policy(data: dict[str, Any]) -> FiberSupportPolicy:
    if set(data) - {"automatic", "included", "excluded"}:
        raise ValueError("Unknown deformation support policy setting.")
    fields = {
        key: tuple(SurfaceReference(**ref) for ref in data.get(key, ()))
        for key in ("included", "excluded")
    }
    return FiberSupportPolicy(automatic=data.get("automatic", True), **fields)


def decode_binding(data: dict[str, Any]) -> FiberBinding:
    state = dict(data)
    value = state.get("attachment")
    state["attachment"] = Attachment(**tuples(value)) if value else None
    return FiberBinding(**state)


def decode_edit(data: Any) -> FiberEdit | None:
    if not data:
        return None
    state = tuples(data)
    state["candidates"] = tuple(SurfaceReference(**row) for row in state["candidates"])
    return FiberEdit(**state)
