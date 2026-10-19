"""One identity remapping for independent authored curve and fiber copies."""

from dataclasses import replace
from typing import Any
from uuid import uuid4

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.curve_engines import RoutingSettings
from anthroforge.core.fibers import Fiber
from anthroforge.core.results import EvaluationResult

from .surface_reference_codec import remap, remap_capture


def mapping(curve: Curve) -> dict[str, str]:
    return {key: str(uuid4()) for key in (curve.id, *(p.id for p in curve.points))}


def clone(curve: Curve, identities: dict[str, str]) -> Curve:
    return replace(
        curve,
        id=identities[curve.id],
        name=curve.name + " copy",
        parent=identities.get(curve.parent, curve.parent),
        owners=tuple(identities.get(key, key) for key in curve.owners),
        points=point_copies(curve, identities),
        generation=0,
        pose_revision=0,
        construction_revision=0,
        result=EvaluationResult(),
        engine_settings=engine_settings(curve, identities),
        **binding_changes(curve, identities),
    )


def point_copies(curve: Curve, identities: dict[str, str]) -> tuple[CurvePoint, ...]:
    return tuple(
        replace(p, id=identities[p.id], junction=identities.get(p.junction, ""))
        for p in curve.points
    )


def binding_changes(curve: Curve, identities: dict[str, str]) -> dict[str, Any]:
    if not isinstance(curve, Fiber):
        return {}
    bindings = tuple(
        replace(b, point=identities[b.point], target=identities.get(b.target, b.target))
        for b in curve.bindings
    )
    return dict(
        bindings=bindings,
        supports=tuple(remap_capture(s, identities) for s in curve.supports),
        edit=copied_edit(curve, identities),
    )


def copied_edit(curve: Fiber, identities: dict[str, str]) -> Any:
    if not curve.edit:
        return None
    return replace(
        curve.edit,
        candidates=tuple(remap(r, identities) for r in curve.edit.candidates),
        rebind=tuple(identities.get(k, k) for k in curve.edit.rebind),
    )


def engine_settings(curve: Curve, identities: dict[str, str]) -> Any:
    settings = curve.engine_settings
    if isinstance(settings, RoutingSettings):
        return replace(
            settings,
            obstacles=tuple(identities.get(k, k) for k in settings.obstacles),
            excluded_obstacles=tuple(identities.get(k, k) for k in settings.excluded_obstacles),
        )
    return settings
