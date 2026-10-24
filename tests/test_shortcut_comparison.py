"""Comparison snapshots and bounded journals never become authored document state."""

from anthroforge.application.comparison_journal import Journal
from tests.test_driving_formulas import curve, driver


def baseline(session):
    target = curve(session)
    key, _ = driver(session, target, "round(value)", value=8)
    session.wait(5)
    session.command("shortcut.comparison.capture", shortcut=key)
    return target, key


def test_capture_has_independent_ownership_and_no_undo(session):
    baseline(session)
    frozen = session.shortcut_comparison.baseline
    before, cursor = session.document, session.history.cursor
    result = session.command("shortcut.comparison.inspect", wait=True)
    assert result["comparison"]["changed"] == 0 and result["replay"]["complete"]
    assert session.document is before and session.history.cursor == cursor
    assert frozen.source.resources is not session.resources
    assert frozen.source.resources.paths is not session.resources.paths
    assert frozen.source.resources.paths
    session.command("shortcut.comparison.clear")
    assert not session.command("shortcut.comparison.inspect")["active"]


def test_shortcut_journal_preserves_gestures_and_waits(session):
    target, key = baseline(session)
    session.begin()
    session.command("driver.value", driver=key, value=12)
    session.command("driver.value", driver=key, value=16)
    session.commit()
    session.wait(5)
    events = session.shortcut_comparison.journal.events
    expected = ["begin", "driver.value", "driver.value", "commit", "wait"]
    assert [r["operation"] for r in events] == expected
    result = session.command("shortcut.comparison.inspect", wait=True)
    row = next(r for r in result["comparison"]["rows"] if r["id"] == target)
    assert "geometry" in row["changes"] and result["replay"]["complete"]


def test_unrelated_edits_and_undo_are_honest_replay_gaps(session):
    target, key = baseline(session)
    session.command("driver.configure", driver=key, changes=dict(label="Renamed"))
    assert "driver.configure" in session.shortcut_comparison.journal.reasons[0]
    session.command("undo")
    assert any("undo" in r for r in session.shortcut_comparison.journal.reasons)
    assert session.shortcut_comparison.baseline.source.document.object(target)


def test_provisional_capture_and_cancel_keep_baseline(session):
    _, key = baseline(session)
    session.begin()
    session.command("shortcut.comparison.capture", shortcut=key)
    assert session.command("shortcut.comparison.inspect")["provisional"]
    session.cancel()
    assert session.shortcut_comparison.baseline
    assert not session.shortcut_comparison.journal.describe()["complete"]


def test_journal_limits_do_not_silently_truncate_replay():
    journal = Journal()
    journal.events = [dict(operation="wait")] * 10000
    journal.append("begin")
    assert journal.stopped and not journal.describe()["complete"]
    assert len(journal.events) == 10000


def test_failed_capture_does_not_discard_previous_baseline(session):
    import pytest

    baseline(session)
    old = session.shortcut_comparison.baseline
    with pytest.raises(ValueError):
        session.command("shortcut.comparison.capture", shortcut="missing")
    assert session.shortcut_comparison.baseline is old


def test_geometry_queries_accept_controls_without_surface_results(session):
    hook = session.command("control.create")
    cage = session.command("control.create", kind="LATTICE")
    baseline(session)
    result = session.command("shortcut.comparison.inspect", wait=True)
    assert result["state"] == "succeeded", result["error"]
    controls = [row for row in result["comparison"]["rows"] if row["id"] in (hook, cage)]
    assert len(controls) == 2 and all(r["after"]["geometry"]["kind"] == "NONE" for r in controls)
