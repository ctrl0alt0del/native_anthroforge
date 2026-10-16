import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.application.construction_codec import curve as decode_curve
from anthroforge.core.construction import BodyPiece
from anthroforge.native import bodies
from anthroforge.native.mesh import GeometryEngine

REFERENCE = json.loads(
    (Path(__file__).parent / "fixtures/primitives/blender501_curves.json").read_text()
)


@pytest.fixture(scope="module")
def engine():
    return GeometryEngine()


def reference_curve(case):
    record = dict(case["curve"])
    assert record.pop("radius_interpolation") == record.pop("tilt_interpolation") == "LINEAR"
    return decode_curve(record)


@pytest.mark.parametrize("case", REFERENCE["cases"])
def test_curve_modifier_matches_blender(engine, case):
    curve = reference_curve(case)
    samples = bodies.path(engine, curve, 0)
    offsets = np.cumsum([0, *map(len, case["faces"])])
    base = engine.create_mesh(case["vertices"], np.concatenate(case["faces"]), offsets)
    piece = BodyPiece(curve.id, fit=case["fit"])
    actual = bodies.bend(base, samples, piece, curve.closed, 0)
    np.testing.assert_allclose(actual.array(0), case["expected"], atol=2e-5)
