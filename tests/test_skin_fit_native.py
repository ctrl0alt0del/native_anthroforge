"""Fitting parity uses captured original addon output, with independent ABI guard checks."""

import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.native import skin_fit
from anthroforge.native.mesh import NativeCancellation

FIXTURE = json.loads((Path(__file__).parent / "fixtures/skin/fitting.json").read_text())


@pytest.mark.parametrize("strategy", ["SCALE_AWARE", "SINGLE_ACTIVE"])
def test_native_fitter_matches_original_addon(session, strategy):
    data = FIXTURE["cases"][strategy]
    weights, matrices, _ = skin_fit.fit(session.engine, data, dict(bones=3, strategy=strategy))
    np.testing.assert_allclose(weights, data["weights"], atol=1e-8)
    np.testing.assert_allclose(matrices, data["training"], atol=1e-8)
    arrays = dict(data, weights=weights, matrices=matrices)
    transforms, points = skin_fit.predict(session.engine, arrays)
    np.testing.assert_allclose(transforms, data["prediction"]["matrices"], atol=1e-8)
    np.testing.assert_allclose(points, data["prediction"]["positions"], atol=1e-8)


def test_fitting_rejects_cancelled_or_invalid_inputs(session):
    data = FIXTURE["cases"]["SCALE_AWARE"]
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        skin_fit.fit(session.engine, data, {}, cancel.handle)
    with pytest.raises(ValueError, match="settings"):
        skin_fit.fit(session.engine, data, dict(bones=65))
    with pytest.raises(ValueError, match="finite"):
        targets = np.array(data["targets"])
        targets[0, 0, 0] = float("nan")
        skin_fit.fit(session.engine, dict(data, targets=targets), {})
