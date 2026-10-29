"""Reports and pending saves retain the shared stroke's qualified field."""

from anthroforge.application import storage, tissue_inspection_capture
from tests.test_painting_system import append, begin
from tests.test_painting_system import painting_case as painting_case
from tests.test_tissue_painting import setup
from tests.test_tissue_painting_native import VIEW


def test_save_wait_contains_completed_stroke(session, painting_case, tmp_path):
    token = begin(session, painting_case)
    append(session, token)
    session.command("painting.finish", token=token)
    session.waiting_save = True
    path = tmp_path / "painted.anthroforge"
    result = session.command("save", path=str(path), blocked_policy="wait")
    restored, resources = storage.read_package(path, session.engine)
    assert result["status"] == "saved" and resources
    assert restored.objects == session.document.objects
    assert restored.skin == session.document.skin
    assert session.command("painting.status", token=token)["state"] == "committed"


def test_existing_export_captures_shared_candidate_without_inspection_slot(session):
    target = setup(session)
    state = ready_candidate(session, target)
    assert "paint" not in session.tissue_inspection.values
    value = tissue_inspection_capture.paint(session, target, "final")
    assert value["authored"] is False and value["options"]["samples"] == ((0, 0),)
    session.command("painting.cancel", token=state["token"])
    assert tissue_inspection_capture.paint(session, target, "final") == {}


def ready_candidate(session, target):
    value = session.command(
        "painting.preview",
        consumer="tissue_weights",
        target=target,
        name="paint",
        stage="final",
        view=VIEW,
        samples=[[0, 0]],
    )
    session.wait()
    return value
