"""Authoring capabilities of construction targets, independent of UI presentation."""

from .construction import Control, Curve
from .entities import SCP
from .tissues import TissueVCP


def stable_geometry_members(item: object) -> bool:
    primitive = getattr(item, "primitive", None)
    return primitive is None or primitive.kind != "SEGMENT_CHAIN"


def component_editing(item: object) -> bool:
    if isinstance(item, (Control, Curve, TissueVCP)):
        return True
    return isinstance(item, SCP) and bool(item.primitive) and stable_geometry_members(item)
