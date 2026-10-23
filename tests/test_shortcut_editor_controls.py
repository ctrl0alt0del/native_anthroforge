"""Shortcut field transport, controlling-driver navigation and scoped policy editing."""

import pytest

from tests.test_driving_formulas import curve, driver, reference
from tests.test_shortcut_copy import hierarchy
from tests.test_tissue_interaction import controller as controller


def policy_editor(controller):
    root, child = hierarchy(controller.session)
    ref = reference(root, ("transform", "rotation"), 2)
    key = controller.session.command("shortcut.expose", reference=ref)
    panel = controller.shortcut_panel
    panel.configure(True, True, "")
    panel.editor.select(key)
    return panel.editor.policy_editor, root, child, ref


def test_policy_editor_search_and_configuration_do_not_move_anatomy(controller):
    editor, root, child, ref = policy_editor(controller)
    before = controller.session.document.entities
    assert editor.ownerName == "Root"
    editor.filter("child")
    assert [row["target"] for row in editor.rows.rows] == [child]
    editor.override(child, "follow_rotation", "DISABLED")
    state = controller.session.command("shortcut.inspect", reference=ref)
    assert state["policy"]["descendants"][0]["follow_rotation"] == "DISABLED"
    assert controller.session.document.entities == before
    editor.override(child, "follow_rotation", "KEEP")
    assert (
        controller.session.command("shortcut.inspect", reference=ref)["policy"]["descendants"] == ()
    )


def test_policy_editor_rejects_override_outside_owner_descendants(controller):
    editor, root, _, ref = policy_editor(controller)
    editor.override(root, "follow_rotation", "DISABLED")
    assert (
        controller.session.command("shortcut.inspect", reference=ref)["policy"]["descendants"] == ()
    )
    assert "descendants" in controller.message


@pytest.mark.parametrize("kind", ["PROPERTY", "DRIVER"])
def test_integer_controls_accept_integral_qml_numbers_without_truncating(controller, kind):
    session, panel = controller.session, controller.shortcut_panel
    target = curve(session)
    ref = reference(target)
    key = session.command("shortcut.expose", reference=ref)
    if kind == "DRIVER":
        key, _ = driver(session, target, "value", kind="INTEGER", value=8)
    panel.editValue(key, -1, 11.0, False)
    session.wait(5)
    assert session.document.object(target).resolution == 11
    panel.editValue(key, -1, 11.5, False)
    session.wait(5)
    assert session.document.object(target).resolution == 11
    assert "Integer" in controller.message


def test_driven_field_navigation_opens_hidden_controlling_driver(controller):
    session, panel = controller.session, controller.shortcut_panel
    target = curve(session)
    ref = reference(target)
    key, formula = driver(session, target, "8")
    session.command("driver.configure", driver=key, changes=dict(label="Detail", exposed=False))
    session.wait(5)
    state = panel.propertyState(ref, session.document.revision)
    assert not state["writable"] and state["driver"] == key and state["formula"] == formula
    requested = []
    panel.revealRequested.connect(lambda: requested.append(True))
    panel.openDriver(ref)
    assert panel.editor.key == key and requested == [True]
    assert session.document.driving_shortcuts[0].exposed is False
