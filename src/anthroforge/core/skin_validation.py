"""Value validation shared by skin records, independent of any builder policy."""

from math import isfinite


def bounded(name: str, value: float, lower: float, upper: float) -> None:
    if isinstance(value, bool) or not isfinite(value) or not lower <= value <= upper:
        raise ValueError(f"{name} must be finite and between {lower} and {upper}.")


def choice(name: str, value: str, allowed: tuple[str, ...]) -> None:
    if value not in allowed:
        raise ValueError(f"Unsupported {name}: {value}.")


def integer(name: str, value: int, lower: int, upper: int) -> None:
    if type(value) is not int:
        raise ValueError(f"{name} requires an integer.")
    bounded(name, value, lower, upper)
