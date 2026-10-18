"""One identity remapping for independent authored curve and fiber copies."""

from dataclasses import replace
from typing import Any
from uuid import uuid4

from anthroforge.core.construction import Curve
from anthroforge.core.fibers import Fiber
from anthroforge.core.results import EvaluationResult


def mapping(curve: Curve) -> dict[str, str]:
    return {key: str(uuid4()) for key in (curve.id, *(p.id for p in curve.points))}


def clone(curve: Curve, identities: dict[str, str]) -> Curve:
    return replace(
        curve,
        id=identities[curve.id],
        name=curve.name + " copy",
        parent=identities.get(curve.parent, curve.parent),
        owners=tuple(identities.get(key, key) for key in curve.owners),
        points=tuple(replace(p, id=identities[p.id]) for p in curve.points),
        generation=0,
        pose_revision=0,
        construction_revision=0,
        result=EvaluationResult(),
        **binding_changes(curve, identities),
    )


def binding_changes(curve: Curve, identities: dict[str, str]) -> dict[str, Any]:
    if not isinstance(curve, Fiber):
        return {}
    bindings = tuple(
        replace(b, point=identities[b.point], target=identities.get(b.target, b.target))
        for b in curve.bindings
    )
    return {"bindings": bindings}
