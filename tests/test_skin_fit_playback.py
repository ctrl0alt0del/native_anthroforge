"""Compare actual Blender armature playback, including between keys and clamping."""

import json
from pathlib import Path

import numpy as np
import pytest

from anthroforge.native import skin_fit_playback
from tests.test_skin_fit_native import FIXTURE

PLAYBACK = json.loads((Path(__file__).parent / "fixtures/skin/fitted_playback.json").read_text())


@pytest.mark.parametrize("strategy", ["SCALE_AWARE", "SINGLE_ACTIVE"])
def test_channels_and_actual_intermediate_playback_match_blender(session, strategy):
    data, expected = FIXTURE["cases"][strategy], PLAYBACK["cases"][strategy]
    arrays = dict(data, keys=data["values"], matrices=data["prediction"]["matrices"])
    bases, channels = skin_fit_playback.channels(session.engine, arrays)
    np.testing.assert_allclose(bases, expected["bases"], atol=2e-7)
    compare_channels(channels, expected["channels"])
    playback = dict(arrays, bases=bases, channels=channels)
    for value, points in zip(expected["values"], expected["positions"], strict=True):
        actual = skin_fit_playback.evaluate(session.engine, playback, value)
        np.testing.assert_allclose(actual, points, atol=1e-6)


def compare_channels(actual, expected):
    expected = np.array(expected)
    # Quaternion signs are equivalent; each stored sequence preserves temporal continuity.
    sign = np.sign(np.sum(actual[0, :, 3:7] * expected[0, :, 3:7], axis=1))
    expected[:, :, 3:7] *= sign[None, :, None]
    np.testing.assert_allclose(actual, expected, atol=4e-7)
