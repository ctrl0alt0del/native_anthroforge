"""Effective consumer density shared by evaluation, estimates and component selection."""

from .construction import Primitive, ResolvedPrimitive


def counts(primitive: Primitive | ResolvedPrimitive | None) -> dict[str, int]:
    if primitive is None:
        raise ValueError("Sampling requires a primitive definition.")
    if isinstance(primitive, ResolvedPrimitive):
        return dict.fromkeys((curve.id for curve in primitive.curves), primitive.samples)
    values = {
        use.curve: primitive.samples if use.samples is None else use.samples
        for use in primitive.curves
    }
    if primitive.kind == "LOFT" and values:
        return dict.fromkeys(values, max(values.values()))
    return values


def count(primitive: Primitive | ResolvedPrimitive | None, curve: str = "") -> int:
    values = counts(primitive)
    assert primitive is not None
    return values[curve] if curve else max(values.values(), default=primitive.samples)
