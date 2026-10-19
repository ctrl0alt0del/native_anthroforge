"""Compare the adapter with Blender 5.0.1's actual background Draw operator."""

import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.drawing import FitSettings
from anthroforge.native.construction import curve_records
from anthroforge.native.drawing import fit

REFERENCE = json.loads(
    (Path(__file__).parent / "fixtures/primitives/blender501_drawing.json").read_text()
)


@pytest.mark.parametrize("case", REFERENCE["cases"])
def test_native_fit_matches_blender_draw_operator(session, case):
    settings = FitSettings(method=case["method"], error=0.005, closed=case["closed"])
    actual = fit(session.engine, case["samples"], settings)
    expected = Curve(tuple(CurvePoint(**row) for row in case["expected"]), closed=case["closed"])
    np.testing.assert_allclose(actual, curve_records(expected), atol=3e-6)
