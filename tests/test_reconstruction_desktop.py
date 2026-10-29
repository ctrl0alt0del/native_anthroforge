import json

from tests.conftest import CUBE
from tests.test_tissue_interaction import controller as controller


def imported(controller):
    key = controller.session.command("import", path=str(CUBE), units=1.0)["entity_id"]
    controller.session.wait()
    controller.refresh()
    controller.select(key)
    return key


def test_variant_panel_edits_through_normal_controller_and_restores_accepted(controller):
    key = imported(controller)
    original = controller.session.document.entity(key).name
    panel = controller.reconstruction_panel
    panel.create()
    assert json.loads(panel.dataJson)["active"]
    controller.run("scp.rename", dict(entity=key, name="Variant bone"))
    assert controller.selectedData["name"] == "Variant bone"
    panel.run("variant.leave", {})
    assert not json.loads(panel.dataJson)["active"]
    assert controller.selectedData["name"] == original


def test_panel_idle_does_not_rebuild_metadata(controller, monkeypatch):
    imported(controller)
    panel = controller.reconstruction_panel
    panel.synchronize()
    events = []
    panel.changed.connect(lambda: events.append(True))
    before = panel.dataJson
    for _ in range(20):
        panel.synchronize()
    assert not events and panel.dataJson is before


def control_project(session, path):
    bone = session.command("primitive.create", kind="BODY")
    session.wait()
    cage = session.command("control.create", kind="LATTICE", entity=bone)
    session.command("deformer.add", control=cage, target=dict(owner=bone))
    session.wait()
    session.command("save", path=str(path), blocked_policy="wait")
    session.file_lock.close()
    return bone, cage


def test_async_open_resets_projection_when_context_name_stays_accepted(
    controller, session, tmp_path
):
    from anthroforge.desktop.project_actions import start_open

    path = tmp_path / "controls.anthroforge"
    bone, cage = control_project(session, path)
    controller.refresh()
    journal = controller.session.changes
    start_open(controller, str(path))
    controller.session.wait()
    assert not controller.session.scheduler.errors
    assert controller.session.changes is not journal
    assert {bone, cage} <= controller.scene_projection.records.keys()
    assert cage in controller.construction.records
