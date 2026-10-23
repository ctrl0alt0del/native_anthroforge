"""Parametric control deformers consume generated paths once and retain membership intent."""

import numpy as np
import pytest

from tests.test_parametric_curves import create, positions
from tests.test_primitives import mesh


def body_and_hook(session, restricted=False):
    curve = create(session, resolution=5, y="t*t*m")
    body = session.command("primitive.from_curves", curves=[curve], kind="BODY")
    session.wait(5)
    control = session.command("control.create", entity=body)
    binding = session.command(
        "deformer.add",
        control=control,
        target=dict(owner=body, stage="CURVE", component=curve),
        **(dict(indices=[12, 13, 14]) if restricted else {}),
    )
    session.wait(5)
    return curve, body, control, binding


def test_hook_changes_consumer_after_formulas_without_double_deformation_on_switch(session):
    curve, body, control, _ = body_and_hook(session)
    before, source = mesh(session, body).array(0).copy(), positions(session, curve)
    session.command("control.transform", control=control, values=[0, 0, 0.25, 0, 0, 0, 1, 1, 1])
    session.wait(5)
    changed = mesh(session, body).array(0).copy()
    np.testing.assert_allclose(changed, before + [0, 0, 0.25], atol=1e-12)
    np.testing.assert_array_equal(positions(session, curve), source)
    session.command("curve.engine", curve=curve, engine="BEZIER")
    session.wait(5)
    np.testing.assert_allclose(mesh(session, body).array(0), changed, atol=1e-12)
    session.command("curve.engine", curve=curve, engine="PARAMETRIC")
    session.wait(5)
    np.testing.assert_allclose(mesh(session, body).array(0), changed, atol=1e-12)


@pytest.mark.xfail(strict=True, reason="Resolution/membership policy awaits the user's decision")
def test_sampling_change_cannot_silently_retarget_restricted_generated_controls(session):
    curve, body, _, _ = body_and_hook(session, restricted=True)
    before = session.document.object(curve)
    with pytest.raises(ValueError, match="membership"):
        session.command("curve.parametric.configure", curve=curve, changes=dict(resolution=9))
    assert session.document.object(curve) == before
