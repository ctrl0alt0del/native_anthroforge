"""Capture numerical construction provenance with the owned evaluation input."""

from dataclasses import replace
from typing import Any

from anthroforge.core.tissue_material import TissueMaterialState
from anthroforge.core.tissues import TissueVCP

from .object_frames import Frames

REST_FIELDS = ("base_state", "parts", "both_sides", "reverse", "fields")
INTRINSIC_FIELDS = ("relaxation", "crop", "constraints", "fields")


def capture(engine: Any, document: Any, item: TissueVCP, phase: str) -> TissueMaterialState | None:
    if phase == "rest":
        return TissueMaterialState(
            base=item.base_result.asset, **{key: getattr(item, key) for key in REST_FIELDS}
        )
    if phase == "intrinsic":
        if item.rest_material is None:
            raise ValueError("Missing accepted rest provenance; evaluate inflated rest first.")
        return replace(
            item.rest_material,
            frame=Frames(engine, document).world(item.id),
            **{key: getattr(item, key) for key in INTRINSIC_FIELDS},
        )
    return item.intrinsic_material if phase == "final" else None


def accepted(state: TissueMaterialState, phase: str, asset: str) -> TissueMaterialState:
    if phase == "intrinsic":
        return replace(state, own=asset)
    return replace(state, rest=asset) if phase == "rest" else replace(state, final=asset)


def effective(item: Any) -> Any:
    """Relaxation/cropping use the base and inflation that produced accepted rest."""
    state = item.rest_material
    if state is None:
        raise ValueError("Inflated rest has no accepted material provenance; evaluate it first.")
    changes = {key: getattr(state, key) for key in REST_FIELDS if key != "fields"}
    return replace(item, base_result=replace(item.base_result, asset=state.base), **changes)
