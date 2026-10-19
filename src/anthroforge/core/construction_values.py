"""Small shared construction value constraints, without object model dependencies."""

from math import isfinite


def integer(value: int, minimum: int, maximum: int) -> bool:
    return type(value) is int and minimum <= value <= maximum


def validate_range(start: float | None, span: float | None) -> None:
    if start is not None and (not isfinite(start) or not 0 <= start <= 1):
        raise ValueError("Sampling start must be between zero and one.")
    if span is not None and (not isfinite(span) or not 0 < span <= 1):
        raise ValueError("Sampling span must be greater than zero and at most one.")
