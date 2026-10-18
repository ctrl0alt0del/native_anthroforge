"""Native stroke shape, async authorship and independent creation contracts."""

from dataclasses import replace
from threading import Event

import numpy as np
import pytest

from anthroforge.application import drawing_tasks, storage
from anthroforge.core.construction import Curve, CurvePoint
from anthroforge.core.drawing import FitSettings
from anthroforge.native import curve_editing, drawing, paths
from anthroforge.native.mesh import NativeCancellation


def arc(count=81, closed=False):
    angle = np.linspace(0, 2 * np.pi if closed else np.pi, count, endpoint=not closed)
    return np.column_stack((np.cos(angle), np.sin(angle), angle * 0))


@pytest.mark.parametrize("method", ["REFIT", "SPLIT"])
def test_fitting_preserves_endpoints_and_bounds_error(session, method):
    samples = arc()
    settings = FitSettings(method=method, error=0.005, corner_angle=np.pi)
    points = drawing.fit(session.engine, samples, settings)
    np.testing.assert_allclose(points[0, :3], samples[0], atol=1e-6)
    np.testing.assert_allclose(points[-1, :3], samples[-1], atol=1e-6)
    assert 2 <= len(points) < len(samples) / 4
    assert np.isfinite(points).all()
    curve = Curve(tuple(curve_editing.unpack(CurvePoint(), p) for p in points))
    evaluated = paths.evaluate(session.engine, curve).array()[:, :3]
    assert np.max(np.abs(np.linalg.norm(evaluated, axis=1) - 1)) < settings.error * 2


def test_closed_fitting_has_no_duplicate_endpoint(session):
    points = drawing.fit(session.engine, arc(closed=True), FitSettings(closed=True))
    assert len(points) >= 3
    assert not np.allclose(points[0, :3], points[-1, :3])


def test_exact_polyline_retains_positions_and_radius_without_duplicate_closure(session):
    samples = [[0, 0, 0, 1], [1, 0, 0, 2], [1, 0, 0, 2], [1, 1, 0, 3], [0, 0, 0, 1]]
    points = drawing.fit(session.engine, samples, FitSettings(method="POLYLINE", closed=True))
    np.testing.assert_array_equal(points[:, :3], np.array(samples)[[0, 1, 3], :3])
    np.testing.assert_array_equal(points[:, 9], [1, 2, 3])
    assert np.all(points[:, 11:] == 3)


def test_fit_cancellation_and_degenerate_input_fail_before_publication(session):
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="cancel"):
        drawing.fit(session.engine, arc(), FitSettings(), cancel.handle)
    with pytest.raises(ValueError, match="distinct"):
        drawing.fit(session.engine, [[0, 0, 0], [0, 0, 0]], FitSettings())


def test_drawn_curve_has_one_undo_and_complete_persisted_result(session, tmp_path):
    before = session.history.cursor
    target = session.command("curve.draw", points=arc().tolist())["object_id"]
    session.wait(5)
    item = session.document.object(target)
    assert item.result.status == "ready" and not session.document.entities
    assert session.history.cursor == before + 1
    path = tmp_path / "draw.anthroforge"
    storage.atomic_save(path, session.document, session.resources)
    document, resources = storage.read_package(path, session.engine)
    assert document.object(target) == item and item.result.asset in resources.paths
    session.command("undo")
    assert not session.document.objects
    session.command("redo")
    assert session.document.object(target) == item and not session.scheduler.blocked


def delayed_fit(monkeypatch):
    original, gate = drawing_tasks.compute, Event()

    def compute(*args):
        assert gate.wait(4)
        return original(*args)

    monkeypatch.setattr(drawing_tasks, "compute", compute)
    return gate


def test_fitting_publishes_to_original_undo_entry_across_later_edits(session, monkeypatch):
    gate = delayed_fit(monkeypatch)
    target = session.command("curve.draw", points=arc().tolist())["object_id"]
    session.scheduler.tick()
    other = session.command("curve.create")
    gate.set()
    session.wait(5)
    session.command("undo")
    assert target in session.document.registry.records
    assert other not in session.document.registry.records
    session.command("undo")
    assert not session.document.objects


def test_drawing_undo_during_fitting_then_redo_restarts(session, monkeypatch):
    gate = delayed_fit(monkeypatch)
    target = session.command("curve.draw", points=arc().tolist())["object_id"]
    session.scheduler.tick()
    session.command("undo")
    session.command("redo")
    gate.set()
    session.wait(5)
    assert [o.id for o in session.document.objects] == [target]
    assert any(j.state == "obsolete" for j in session.scheduler.jobs)


def test_unknown_or_invalid_fit_settings_fail_without_history(session):
    before = session.document
    with pytest.raises(ValueError, match="fitting method"):
        session.command("curve.draw", points=arc().tolist(), settings={"method": "OTHER"})
    with pytest.raises(ValueError, match="positive"):
        replace(FitSettings(), error=0)
    assert session.document == before
