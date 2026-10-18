"""Display lengths only; all authored/API geometry remains in canonical metres."""

from math import isfinite

METRES = {"m": 1.0, "cm": 0.01, "mm": 0.001}


def factor(unit: str) -> float:
    if unit not in METRES:
        raise ValueError("Display units must be m, cm or mm.")
    return METRES[unit]


def convert(value: float, source: str = "m", target: str = "m") -> float:
    result = float(value) * factor(source) / factor(target)
    if not isfinite(result):
        raise ValueError("Length must be finite.")
    return result
