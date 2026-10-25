"""User settings never become authored edits or alter existing calculation snapshots."""

import json
from dataclasses import replace

import pytest

from anthroforge.application.preferences import PreferenceStore
from anthroforge.application.session import Session
from anthroforge.core.preferences import Preferences
from tests.test_automatic_routing import cube, curve, ready
from tests.test_automatic_routing_lifecycle import block_routing, dispatch


def diagnostic(session, key):
    item = ready(session, key)
    return session.resources.paths[item.result.asset].diagnostics


def test_preferences_persist_without_project_or_undo_changes(session):
    before, history = session.document, tuple(session.history.entries)
    result = session.command("preferences.set", routing_backend="PIQP")
    other = Session()
    try:
        assert other.command("preferences.get")["routing_backend"] == "PIQP"
        assert session.document is before and tuple(session.history.entries) == history
        assert not session.scheduler.blocked and result["path"]
    finally:
        other.close()


def test_invalid_and_failed_preferences_keep_previous_value(tmp_path, monkeypatch):
    from anthroforge.application import preferences

    store = PreferenceStore(tmp_path / "settings.json")
    with pytest.raises(ValueError, match="CUSTOM or PIQP"):
        store.update(routing_backend="DENSE")
    monkeypatch.setattr(
        preferences.os, "replace", lambda *args: (_ for _ in ()).throw(OSError("disk"))
    )
    with pytest.raises(OSError, match="disk"):
        store.update(routing_backend="PIQP")
    assert store.value == Preferences() and not list(tmp_path.iterdir())


def test_corrupt_preferences_do_not_break_startup_or_get_overwritten(tmp_path):
    path = tmp_path / "bad.json"
    original = '{"schema":999,"values":{"routing_backend":"PIQP"}}'
    path.write_text(original)
    store = PreferenceStore(path)
    assert store.value == Preferences() and store.error
    with pytest.raises(ValueError, match="Correct or remove"):
        store.update(routing_backend="PIQP")
    assert path.read_text() == original


def test_switch_preserves_results_and_manual_mode(session):
    cube(session)
    key = curve(session)
    session.command("update_mode", entity=key, mode="MANUAL")
    before = ready(session, key)
    session.command("preferences.set", routing_backend="PIQP")
    assert ready(session, key) == before and diagnostic(session, key).backend == "CUSTOM"
    session.command("curve.evaluate", curve=key)
    assert diagnostic(session, key).backend == "PIQP"


def test_running_job_uses_captured_backend_and_next_dispatch_uses_new_choice(session, monkeypatch):
    cube(session)
    key = curve(session)
    gate, started = block_routing(monkeypatch)
    try:
        job = dispatch(session, key)
        assert started.wait(2)
        session.command("preferences.set", routing_backend="PIQP")
    finally:
        gate.set()
    assert diagnostic(session, key).backend == "CUSTOM" and job.state == "succeeded"
    session.command("curve.evaluate", curve=key)
    assert diagnostic(session, key).backend == "PIQP"


def test_queued_job_captures_preference_at_dispatch(session):
    key = curve(session)
    from anthroforge.application.path_tasks import make_job

    job = make_job(session, key)
    session.command("preferences.set", routing_backend="PIQP")
    assert job.prepare(session.document)[2] == Preferences("PIQP")


def test_saved_result_records_backend_without_saving_preferences(session, tmp_path):
    from anthroforge.application import storage

    session.command("preferences.set", routing_backend="PIQP")
    key = curve(session)
    file = tmp_path / "result.anthroforge"
    storage.atomic_save(file, session.document, session.resources)
    document, resources = storage.read_package(file, session.engine)
    assert resources.paths[document.object(key).result.asset].diagnostics.backend == "PIQP"
    assert session.command("preferences.get")["routing_backend"] == "PIQP"


def test_in_memory_preferences_do_not_touch_user_settings(tmp_path):
    store = PreferenceStore()
    store.update(routing_backend="PIQP")
    assert store.path is None and store.describe()["routing_backend"] == "PIQP"
    assert replace(store.value, routing_backend="CUSTOM") == Preferences()
    assert not (tmp_path / "preferences.json").exists()


def test_preference_file_contains_only_settings(session):
    from pathlib import Path

    result = session.command("preferences.set", routing_backend="PIQP")
    data = json.loads(Path(result["path"]).read_text())
    assert data == {
        "schema": 1,
        "values": {
            "routing_backend": "PIQP",
            "routing_conversion_points": "ENDPOINTS",
            "fiber_propagation": "SMOOTH_SHAPE",
            "autosave_enabled": True,
            "autosave_minutes": 5,
        },
    }


def test_conversion_preview_uses_selected_backend_without_committing(session):
    cube(session)
    key = session.command("curve.create", points=[dict(position=[x, 0, 0]) for x in (-2, 2)])
    session.wait()
    original = session.document
    session.command("preferences.set", routing_backend="PIQP")
    session.command("curve.conversion.preview", curve=key, engine="ROUTED")
    session.wait()
    assert session.conversion.state == "ready", session.conversion.error
    assert session.conversion.asset.diagnostics.backend == "PIQP"
    assert session.document is original


def test_backend_failure_retains_accepted_geometry_without_fallback(session, monkeypatch):
    from anthroforge.native import routing

    key = curve(session)
    before = ready(session, key).result.asset
    session.command("preferences.set", routing_backend="PIQP")
    monkeypatch.setattr(routing, "evaluate", fail_backend)
    session.command("curve.evaluate", curve=key)
    session.wait()
    result = session.document.object(key).result
    assert result.asset == before and result.status == "failed"
    assert (
        "PIQP" in result.error and session.resources.paths[before].diagnostics.backend == "CUSTOM"
    )


def fail_backend(engine, inputs, cancel=0):
    assert inputs.backend == "PIQP"
    raise ValueError("PIQP routing subproblem failed (status -8).")
