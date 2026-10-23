"""Generated point records adopt native coordinates without authoring another edit."""

from dataclasses import replace
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.results import EvaluationResult
from anthroforge.native import curve_editing, parametric

from .path_assets import PathAsset


def evaluate(engine: Any, item: Curve, cancel: int) -> PathAsset:
    path, records = parametric.evaluate(engine, item, cancel)
    points = tuple(curve_editing.unpack(identity(item, i), row) for i, row in enumerate(records))
    authored = replace(item, points=points, result=EvaluationResult())
    return PathAsset(path, authored)


def identity(item: Curve, index: int) -> CurvePoint:
    if index < len(item.points):
        return item.points[index]
    key = str(uuid5(NAMESPACE_URL, "anthroforge:parametric:" + item.id + ":" + str(index)))
    return CurvePoint(id=key)
