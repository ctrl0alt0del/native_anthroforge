"""Explicit construction record variants; no native handles or Python class names in files."""

from dataclasses import asdict
from typing import Any

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_engines import fields as curve_fields
from anthroforge.core.curve_uses import CurveUse
from anthroforge.core.entities import Attachment
from anthroforge.core.fibers import Fiber, FiberBinding, FiberEdit
from anthroforge.core.object_registry import Construction
from anthroforge.core.reference_images import ImageCalibration, ReferenceImage
from anthroforge.core.results import EvaluationResult
from anthroforge.core.surfaces import Surface

from .construction_codec import result_fields, tuples

KINDS = {Curve: "curve", Fiber: "fiber", Surface: "surface", ReferenceImage: "reference_image"}


def encode(item: Construction) -> dict[str, Any]:
    return {"kind": KINDS[type(item)], "state": asdict(item)}


def decode(data: dict[str, Any]) -> Construction:
    kind, state = data["kind"], tuples(data["state"])
    state["result"] = EvaluationResult(**result_fields(state.get("result", {})))
    if kind in ("curve", "fiber"):
        return decode_curve(kind, state)
    if kind == "surface":
        state["curves"] = tuple(CurveUse(**tuples(use)) for use in state["curves"])
        return Surface(**state)
    if kind == "reference_image":
        calibration = state.get("calibration")
        state["calibration"] = ImageCalibration(**tuples(calibration)) if calibration else None
        return ReferenceImage(**state)
    raise ValueError(f"Unsupported construction object kind: {kind}")


def decode_curve(kind: str, state: dict[str, Any]) -> Curve:
    state = curve_fields(state)
    state["points"] = tuple(CurvePoint(**tuples(point)) for point in state["points"])
    if kind == "fiber":
        state["bindings"] = tuple(decode_binding(binding) for binding in state["bindings"])
        state["edit"] = FiberEdit(**tuples(state["edit"])) if state.get("edit") else None
        return Fiber(**state)
    return Curve(**state)


def decode_binding(data: dict[str, Any]) -> FiberBinding:
    state = dict(data)
    value = state.get("attachment")
    state["attachment"] = Attachment(**tuples(value)) if value else None
    return FiberBinding(**state)
