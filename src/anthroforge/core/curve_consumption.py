"""Live curve references belong to their primitive or surface consumer."""

from dataclasses import replace

from .construction import Primitive
from .curve_uses import CurveUse
from .entities import SCP
from .surfaces import Surface


def uses(item: object) -> tuple[CurveUse, ...]:
    if isinstance(item, Surface):
        return item.curves
    if isinstance(item, SCP) and isinstance(item.primitive, Primitive):
        return item.primitive.curves
    return ()


def with_uses[T: SCP | Surface](item: T, sources: tuple[CurveUse, ...]) -> T:
    if isinstance(item, Surface):
        return replace(item, curves=sources)
    if not isinstance(item.primitive, Primitive):
        raise ValueError("This object has no curve construction.")
    return replace(item, primitive=replace(item.primitive, curves=sources))
