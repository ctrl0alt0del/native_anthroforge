"""Desktop shortcut adapters use the same commands and immutable authored identities."""

from tests.test_driving_formulas import curve, driver, reference
from tests.test_tissue_interaction import controller as controller


def test_driver_editor_and_numeric_scrub_share_one_transaction(controller):
    target = curve(controller.session)
    key, _ = driver(controller.session, target, "round(value)", value=8)
    panel = controller.shortcut_panel
    panel.configure(True, True, "")
    panel.editor.select(key)
    assert panel.editor.rows.rows[0]["expression"] == "round(value)"
    controller.session.begin()
    panel.editValue(key, -1, 11.0, False)
    panel.editValue(key, -1, 12.0, False)
    controller.session.commit()
    controller.session.wait(5)
    assert controller.session.document.object(target).resolution == 12
    controller.session.navigate(-1)
    assert controller.session.document.driving_shortcuts[0].value == 8


def test_point_properties_stay_discoverable_after_native_edit(controller):
    target = curve(controller.session)
    point = controller.session.document.object(target).points[-1].id
    ref = reference(target, ("points", "@" + point, "position"), 0)
    key, _ = driver(controller.session, target, "value*m", value=0.4, path=ref)
    controller.session.wait(5)
    editor = controller.shortcut_panel.editor
    editor.select(key)
    editor.discover("Position", "INPUT")
    assert "Point 2" in editor.rows.rows[0]["label"]
    assert editor.rows.rows[0]["label"].endswith(" · X")
    assert any(row["reference"] == ref for row in editor.choices.rows)


def test_hiding_and_relabeling_driver_do_not_recalculate(controller):
    target = curve(controller.session)
    key, _ = driver(controller.session, target, "8")
    controller.session.wait(5)
    old = controller.session.document.object(target)
    panel = controller.shortcut_panel
    panel.configure(True, True, "")
    panel.editor.select(key)
    panel.editor.configure("label", "Detail")
    panel.hide(key)
    controller.session.wait(5)
    assert controller.session.document.object(target) is old
    assert panel.model.rows == []
