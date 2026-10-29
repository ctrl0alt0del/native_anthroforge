from tests.test_skeleton_update_commands import replacement
from tests.test_tissue_interaction import controller as controller


def inspect(controller, tmp_path):
    from tests.conftest import CUBE

    session = controller.session
    key = session.command("import", path=str(CUBE), units=1.0)["entity_id"]
    session.wait()
    panel = controller.skeleton_panel
    panel.inspect(str(replacement(session, key, tmp_path)))
    session.wait()
    panel.synchronize()
    panel.timer.stop()
    panel.prepare()
    session.wait()
    panel.synchronize()
    return panel, key


def test_matching_prepares_and_apply_uses_prepared_geometry(controller, tmp_path):
    panel, key = inspect(controller, tmp_path)
    assert panel.state["ready"], panel.state
    assert panel.state["matches"] == {key: key}
    assert panel.scene.models[0].wanted and panel.scene.models[1].wanted
    before = controller.session.document
    panel.apply()
    assert controller.session.document.entity(key).matrix[3] == 2
    controller.session.command("undo")
    assert controller.session.document.entities == before.entities


def test_cancel_releases_staged_comparison_and_does_not_edit(controller, tmp_path):
    panel, _ = inspect(controller, tmp_path)
    before = controller.session.document
    panel.cancel()
    assert panel.scene.candidate is None
    assert all(not model.wanted and not model.pending for model in panel.scene.models)
    assert controller.session.document is before


def test_review_lists_do_not_republish_when_only_selection_changes(controller, tmp_path):
    panel, key = inspect(controller, tmp_path)
    notifications = []
    panel.reviewChanged.connect(lambda: notifications.append(True))
    before = panel.reviewJson
    assert before and "comparison" not in panel.state and "evidence" not in panel.state
    panel.selectObject(key)
    assert panel.state["selection"] == key and panel.reviewJson is before
    assert not notifications
