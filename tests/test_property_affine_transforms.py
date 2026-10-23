"""Numeric channel editing retains the affine frames used by migrated cages/hooks."""

from dataclasses import replace
from math import ulp

import pytest

FRAME = (2.0, 1.0, 0.0, 3.0, 0.0, 3.0, 0.0, 4.0, 0.0, 0.0, 4.0, 5.0, 0.0, 0.0, 0.0, 1.0)


def control(session):
    key = session.command("control.create", kind="HOOK")
    item = replace(session.document.control(key), matrix=FRAME)
    session.replace_document(controls=(item,))
    return key


def reference(key, field, component=0):
    return dict(target=key, path=["transform", field], component=component)


@pytest.mark.parametrize("field", ("position", "rotation", "scale"))
def test_unchanged_channel_preserves_exact_sheared_frame(session, field):
    key = control(session)
    ref = reference(key, field)
    value = session.command("property.get", reference=ref)["value"]
    before = session.document.control(key)
    session.command("property.set", reference=ref, value=value)
    assert session.document.control(key) == before


def test_translation_preserves_shear_and_other_channels(session):
    key = control(session)
    session.command("property.set", reference=reference(key, "position"), value=7.0)
    frame = session.document.control(key).matrix
    assert frame[:3] == FRAME[:3] and frame[4:] == FRAME[4:]
    assert session.engine.world_point(frame, (1, 1, 1)) == [10.0, 7.0, 9.0]
    session.command("undo")
    assert session.document.control(key).matrix == FRAME


def test_scale_preserves_oblique_basis_and_translation(session):
    key = control(session)
    session.command("property.set", reference=reference(key, "scale"), value=4.0)
    frame = session.document.control(key).matrix
    assert session.engine.world_point(frame, (1, 1, 1)) == [8.0, 7.0, 9.0]
    assert frame[1:] == FRAME[1:]
    session.command("undo")
    assert session.document.control(key).matrix == FRAME


def test_native_rotation_retains_oblique_basis(session):
    engine = session.engine
    values = engine.decompose(FRAME)
    values[5] += 90.0
    frame = engine.transform_channels(FRAME, values)
    assert engine.world_point(frame, (1, 1, 1)) == pytest.approx((0, 7, 9))
    assert engine.decompose(frame)[6:] == pytest.approx(engine.decompose(FRAME)[6:])


def test_driving_formula_with_same_value_does_not_deform_control(session):
    key = control(session)
    driver = session.command("driver.create", value=2.0)
    session.command(
        "driver.formula.add", driver=driver, target=reference(key, "scale"), expression="value"
    )
    session.wait()
    assert session.document.control(key).matrix == FRAME
    session.command("driver.value", driver=driver, value=4.0)
    session.wait()
    assert session.engine.world_point(session.document.control(key).matrix, (1, 1, 1)) == [8, 7, 9]


def test_roundoff_in_transform_formula_is_not_an_authored_edit(session):
    key = control(session)
    ref = reference(key, "scale")
    before = session.document.control(key)
    session.command("property.set", reference=ref, value=2.0 + 2 * ulp(2.0))
    assert session.document.control(key) == before
    session.command("property.set", reference=ref, value=2.0 + 32 * ulp(2.0))
    assert session.document.control(key).matrix != before.matrix


def test_small_transform_values_are_not_compared_with_absolute_tolerance(session):
    key = control(session)
    ref = reference(key, "position")
    session.command("property.set", reference=ref, value=1e-14)
    session.command("property.set", reference=ref, value=2e-14)
    assert session.command("property.get", reference=ref)["value"] == 2e-14
