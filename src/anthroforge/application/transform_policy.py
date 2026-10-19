"""Object-level transform capabilities, independent of component editing and parenting."""

from anthroforge.core.fibers import Fiber
from anthroforge.core.object_registry import SceneObject


def object_reason(item: SceneObject) -> str:
    if isinstance(item, Fiber):
        return "Fibers follow anatomical bindings; edit their curve points instead."
    return ""


def require_object_transform(item: SceneObject) -> None:
    reason = object_reason(item)
    if reason:
        raise ValueError(reason)
