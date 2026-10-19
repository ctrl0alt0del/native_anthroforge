"""Object-level transform capabilities, independent of component editing and parenting."""

from anthroforge.core.fibers import Fiber
from anthroforge.core.object_registry import SceneObject
from anthroforge.core.points import Anchor
from anthroforge.core.tissues import TissueVCP


def object_reason(item: SceneObject) -> str:
    if isinstance(item, TissueVCP):
        return "Tissue geometry is derived; edit its construction sources and parameters."
    if isinstance(item, Anchor):
        return "Anchors follow anatomical bindings; edit or rebind their position."
    if isinstance(item, Fiber):
        return "Fibers follow anatomical bindings; edit their curve points instead."
    return ""


def require_object_transform(item: SceneObject) -> None:
    reason = object_reason(item)
    if reason:
        raise ValueError(reason)
