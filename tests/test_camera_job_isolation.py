"""Camera persistence must not invalidate anatomy, diagnostics or scene payloads."""

from dataclasses import replace

import pytest

from anthroforge.application.changes import ChangeJournal
from anthroforge.application.issues import mirroring
from anthroforge.core.document import Document
from anthroforge.core.entities import Workspace
from tests.test_mirroring_desktop import controller as controller
from tests.test_mirroring_desktop import mirrored_cube


@pytest.mark.parametrize("field", [0, 4, 6])
def test_camera_save_preserves_scene_and_does_not_start_jobs(controller, field):
    mirrored_cube(controller)
    session = controller.session
    session.command("wait")
    controller.refresh()
    rows, jobs = controller._render_rows, len(session.scheduler.jobs)
    values = list(session.workspace.camera)
    values[field] += 0.1
    controller.viewport_view.saveCamera(values, session.workspace.orthographic)
    controller.tick()
    session.command("wait")
    assert session.workspace.camera == tuple(values)
    assert controller._render_rows is rows
    assert len(session.scheduler.jobs) == jobs


def test_camera_save_keeps_skin_assessment_cached(controller, monkeypatch):
    from anthroforge.application import skin_assessment

    mirrored_cube(controller)
    controller.session.command("wait")
    controller.refresh()
    status = controller.session.skin_status.pipeline_inputs()
    monkeypatch.setattr(skin_assessment, "assess", unexpected_assessment)
    controller.viewport_view.saveCamera([1, 0, 0, -20, 25, 0, 4], False)
    controller.tick()
    controller.notify()
    assert controller.session.skin_status.pipeline_inputs() is status


def test_camera_save_does_not_rebroadcast_unchanged_skin_panel(controller):
    mirrored_cube(controller)
    controller.session.command("wait")
    controller.refresh()
    notifications = []
    controller.skin_panel.changed.connect(lambda: notifications.append(True))
    controller.viewport_view.saveCamera([1, 0, 0, -20, 25, 0, 4], False)
    controller.tick()
    controller.notify()
    assert not notifications


def unexpected_assessment(*args):
    raise AssertionError("Camera/notification repeated a geometry-dependent skin assessment")


def test_visibility_still_updates_scene_after_camera_save(controller):
    _, child, _ = mirrored_cube(controller)
    controller.viewport_view.saveCamera([1, 0, 0, -20, 25, 0, 4], False)
    controller.tick()
    controller.session.command("workspace.update", hidden=[child])
    controller.tick()
    assert not controller.scene_projection.records[child]["visible"]


def test_mirror_read_set_rejects_pose_changes_but_accepts_camera(controller):
    root, _, _ = mirrored_cube(controller)
    document = controller.session.document
    captured = mirroring.source(document, "document")
    camera = replace(
        document, workspaces=(replace(document.workspaces[0], camera=(1, 0, 0, 0, 0, 0, 4)),)
    )
    assert mirroring.source(camera, "document") == captured
    matrix = list(document.entity(root).matrix)
    matrix[3] += 1
    moved = replace(document.entity(root), matrix=tuple(matrix))
    changed = replace(document, entities=(moved, *document.entities[1:]))
    assert mirroring.source(changed, "document") != captured


def test_journal_combines_camera_and_domain_changes_without_hiding_edits():
    journal, before = ChangeJournal(), Document()
    camera = replace(before, workspaces=(Workspace(camera=(1, 0, 0, 0, 0, 0, 4)),))
    journal.record(before, camera)
    assert journal.since(0).only_workspace({"camera", "orthographic"})
    changed = replace(camera, name="Renamed")
    journal.record(camera, changed)
    assert not journal.since(0).only_workspace({"camera", "orthographic"})
    assert not journal.since(-1).only_workspace({"camera", "orthographic"})


def test_mirror_rule_change_still_schedules_check(controller):
    root, _, _ = mirrored_cube(controller)
    session = controller.session
    session.command("wait")
    previous = {job.id for job in session.scheduler.jobs}
    session.command("mirror.configure", target=root, shift=3)
    session.command("wait")
    assert any(
        j.id not in previous and j.key == "issues:mirroring.v1" for j in session.scheduler.jobs
    )
