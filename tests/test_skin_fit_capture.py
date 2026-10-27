"""Real shortcut capture and fitting preserve live anatomy, references and sample identity."""

import numpy as np

from anthroforge.application import skin_fit_capture, skin_fit_evaluation
from anthroforge.core.skin_fitting import Settings
from anthroforge.native.mesh import NativeCancellation
from tests.test_skin_reference import build, topology


def setup(session):
    bone = topology(session)
    build(session)
    ref = dict(target=bone, path=["transform", "position"], component=1)
    return session.command("shortcut.expose", reference=ref, label="Translate Y")


def test_actual_sampling_is_isolated_and_uses_fixed_topology(session):
    identity = setup(session)
    before, resources = session.document, set(session.assets)
    settings, cancel = Settings(0, 0.2, bones=1, samples=5), NativeCancellation(session.engine)
    payload = before, session.resources, session.preferences.value, identity, settings
    arrays, error = skin_fit_capture.capture(*payload, cancel)
    assert session.document is before and set(session.assets) == resources
    assert error < 1e-8 and arrays["targets"].shape == (5, 8, 3)
    expected = arrays["vertices"][None] + arrays["values"][:, None, None] * np.array([0, 1, 0])
    np.testing.assert_allclose(arrays["targets"], expected, atol=1e-7)
    output = skin_fit_evaluation.compile_samples(session.engine, arrays, settings, cancel.handle)
    assert max(row["maximum"] for row in output["report"]) < 1e-6
    assert output["weights"].shape == (8, 1)
