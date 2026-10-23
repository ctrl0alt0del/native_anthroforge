"""Invalid initial curves have presentation geometry without an accepted result."""

import numpy as np

from tests.test_tissue_interaction import controller as controller


def failed_curve(controller):
    key = controller.session.command("curve.create", engine="PARAMETRIC", settings=dict(x="1/0"))
    controller.session.wait(5)
    controller.refresh()
    return key


def test_initial_failure_placeholder_is_unpickable_and_not_a_document_resource(controller):
    key = failed_curve(controller)
    session, placeholders = controller.session, controller.construction.placeholders
    row = next(row for row in placeholders.rows(controller) if row["id"] == key)
    assert row["placeholder"] and not row["pickable"]
    assert not session.document.object(key).result.asset
    assert row["geometry_asset"] not in session.resources.paths
    np.testing.assert_array_equal(placeholders.path.array()[:, :3], [[0, 0, 0], [1, 0, 0]])


def test_recovery_releases_placeholder_and_later_failure_keeps_accepted_geometry(controller):
    key = failed_curve(controller)
    session, placeholders = controller.session, controller.construction.placeholders
    session.command("curve.parametric.configure", curve=key, changes=dict(x="t*m"))
    session.wait(5)
    controller.refresh()
    accepted = session.document.object(key).result.asset
    assert accepted and not placeholders.rows(controller) and not placeholders.resources()
    session.command("curve.parametric.configure", curve=key, changes=dict(x="1/0"))
    session.wait(5)
    controller.refresh()
    assert session.document.object(key).result.asset == accepted
    assert not placeholders.rows(controller) and not placeholders.resources()
