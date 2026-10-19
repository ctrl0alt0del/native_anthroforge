"""Engine conversion is a bounded preview, followed by one checked authored transaction."""

from threading import Event
from weakref import ref

import numpy as np
import pytest

from anthroforge.application import curve_conversion, storage
from anthroforge.core.curve_engines import BezierSettings, PolylineSettings, RoutingSettings


def source(session, closed=False):
    points = [dict(position=point) for point in ((-0.5, 0, 0), (0, 1, 0), (0.5, 0, 0))]
    key = session.command("curve.create", points=points, closed=closed)
    session.wait(5)
    return key


def preview(session, key, **options):
    result = session.command("curve.conversion.preview", curve=key, engine="POLYLINE", **options)
    session.wait(5)
    assert session.command("curve.conversion.status")["state"] == "ready"
    return result["token"]


def test_preview_changes_no_document_or_history_and_accept_is_one_undo(session):
    key = source(session)
    document, cursor = session.document, session.history.cursor
    token = preview(session, key, samples=12)
    assert session.document is document and session.history.cursor == cursor
    assert isinstance(session.conversion.asset.authored.engine_settings, PolylineSettings)
    session.command("curve.conversion.accept", token=token)
    session.wait(5)
    assert (
        session.history.cursor == cursor + 1 and session.document.object(key).engine == "POLYLINE"
    )
    session.command("undo")
    assert session.document.object(key).points == document.object(key).points
    assert isinstance(session.document.object(key).engine_settings, BezierSettings)


def test_conversion_rejects_stale_shape_and_keeps_latest_accepted_result(session):
    key = source(session)
    token = preview(session, key)
    point = session.document.object(key).points[1].id
    session.command("curve.point.update", curve=key, point=point, position=[0, 2, 0])
    session.wait(5)
    before = session.document.object(key)
    assert session.command("curve.conversion.status")["state"] == "stale"
    with pytest.raises(ValueError, match="current successful"):
        session.command("curve.conversion.accept", token=token)
    assert session.document.object(key) == before


def test_accept_preserves_metadata_edited_after_preview(session):
    key = source(session)
    token = preview(session, key, mode="AUTHORED")
    session.command("object.rename", target=key, name="Latest name")
    session.command("curve.conversion.accept", token=token)
    session.wait(5)
    assert session.document.object(key).name == "Latest name"
    assert len(session.document.object(key).points) == 3


def test_closed_conversion_retains_start_without_duplicate_endpoint(session):
    key = source(session, closed=True)
    first = session.document.object(key).points[0]
    preview(session, key, samples=17)
    candidate = session.conversion.asset.authored
    assert candidate.closed and len(candidate.points) == 17
    assert candidate.points[0].id == first.id
    np.testing.assert_allclose(candidate.points[0].position, first.position)
    assert candidate.points[-1].position != candidate.points[0].position


def test_shared_topology_lock_applies_to_conversion_and_unlocks(session):
    key = source(session)
    consumer = session.command("primitive.from_curves", curves=[key], kind="BODY")
    child = session.command("scp.empty", name="Attached child", parent=consumer)
    session.wait(5)
    with pytest.raises(ValueError, match=child):
        preview(session, key)
    session.command("scp.delete", entity=child)
    preview(session, key)


def test_routing_defaults_to_all_authored_points(session):
    key = source(session)
    points = session.document.object(key).points
    session.command("curve.conversion.preview", curve=key, engine="ROUTED")
    session.wait(5)
    assert session.conversion.state == "ready", session.conversion.error
    assert session.conversion.asset.authored.points == points


def test_routing_rejects_an_explicitly_empty_constraint_selection(session):
    key = source(session)
    before = len(session.scheduler.jobs)
    with pytest.raises(ValueError, match="explicitly selected"):
        session.command("curve.conversion.preview", curve=key, engine="ROUTED", points=[])
    assert len(session.scheduler.jobs) == before and session.conversion.state == "idle"


def test_cancel_releases_preview_and_project_open_discards_it(session, tmp_path):
    key = source(session)
    path = tmp_path / "source.anthroforge"
    storage.atomic_save(path, session.document, session.resources)
    preview(session, key)
    resource = ref(session.conversion.asset.path)
    session.command("curve.conversion.cancel")
    assert resource() is None
    preview(session, key)
    session.command("open", path=str(path))
    assert session.conversion.state == "idle"
    session.command("curve.conversion.cancel")


def test_engine_specific_configuration_roundtrips(session, tmp_path):
    key = session.command("curve.create", settings=dict(resolution=7))
    session.wait(5)
    path = tmp_path / "settings.anthroforge"
    storage.atomic_save(path, session.document, session.resources)
    document, _ = storage.read_package(path, session.engine)
    assert document.object(key).engine_settings == BezierSettings(7)
    assert RoutingSettings(obstacles=("surface",)).kind == "ROUTED"
    with pytest.raises(TypeError):
        session.command("curve.create", engine="POLYLINE", settings=dict(resolution=7))


def blocked_compute(monkeypatch):
    original, gate = curve_conversion.compute, Event()

    def execute(*args):
        assert gate.wait(4)
        return original(*args)

    monkeypatch.setattr(curve_conversion, "compute", execute)
    return gate


def test_running_preview_does_not_block_save_and_obsolete_result_cannot_publish(
    session, monkeypatch
):
    key = source(session)
    gate = blocked_compute(monkeypatch)
    try:
        session.command("curve.conversion.preview", curve=key, engine="POLYLINE")
        session.scheduler.tick()
        assert not session.scheduler.blocked
        session.command("curve.conversion.cancel")
    finally:
        gate.set()
    session.wait(5)
    assert session.conversion.state == "idle" and session.document.object(key).engine == "BEZIER"
