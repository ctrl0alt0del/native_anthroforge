"""Validated remesher exchange; numerical preparation remains in native adapters."""

from pathlib import Path
from typing import Any

import numpy as np


def read_field(path: Path, count: int) -> Any:
    values = np.loadtxt(path, skiprows=2, ndmin=2)
    if values.shape != (count, 3) or not np.isfinite(values).all():
        raise ValueError("QuadWild prior field does not match its triangle mesh.")
    return values


def write_field(path: Path, values: Any) -> None:
    np.savetxt(path, values, header=f"{len(values)}\n4", comments="")


def write_features(path: Path, values: Any) -> None:
    np.savetxt(path, values, fmt="%d", delimiter=",", header=str(len(values)), comments="")
