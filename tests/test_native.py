import math

import pytest

from anthroforge.native.bridge import NativeEngine


def test_native_bounds_and_input_ownership():
    coordinates = [-2.0, 4.0, 1.0, 3.0, -5.0, 9.0]
    before = coordinates.copy()
    assert NativeEngine().bounds(coordinates) == (-2.0, -5.0, 1.0, 3.0, 4.0, 9.0)
    assert coordinates == before


@pytest.mark.parametrize("coordinates", [[], [1.0], [0.0, 0.0, math.nan], [0.0, math.inf, 0.0]])
def test_invalid_native_inputs_are_rejected(coordinates):
    with pytest.raises(ValueError):
        NativeEngine().bounds(coordinates)


def test_missing_native_library_is_explicit(tmp_path):
    with pytest.raises(OSError):
        NativeEngine(tmp_path / "does-not-exist.dll")
