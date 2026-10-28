"""Collagen painting shares native visibility and atomic stroke publication."""

import numpy as np
import pytest

from anthroforge.application import skin_operations
from tests.test_skin_jobs import imported
from tests.test_tissue_painting_native import VIEW


def request(session, target, through=False):
    result = session.command(
        "skin.inspect.paint",
        target=target,
        view=VIEW,
        samples=[[0, 0]],
        brush=[1000, 1, 1, 1, through],
    )
    session.wait()
    state = session.command("skin.inspect.status")
    assert state["state"] == "ready", state
    return result["job"]


def test_readonly_preview_then_one_undo(session, monkeypatch):
    target = imported(session, monkeypatch)
    session.command("skin.collagen.fill", owner=target, value=0)
    before, count = session.document, len(session.history.entries)
    job = request(session, target)
    assert session.document is before and len(session.history.entries) == count
    session.command("skin.collagen.paint.commit", job=job)
    setting = skin_operations.settings_for(session.document.skin, target)
    weights = session.resources.skin[setting.painted].arrays["collagen"]
    assert np.any(weights > 0) and np.any(weights == 0)
    assert len(session.history.entries) == count + 1
    session.command("undo")
    assert session.document.skin == before.skin


def test_through_paints_both_sides(session, monkeypatch):
    target = imported(session, monkeypatch)
    session.command("skin.collagen.fill", owner=target, value=0)
    request(session, target, True)
    value = session.tissue_inspection.values["collagen"].asset["resource"].values
    assert np.all(value > 0)


def test_changed_collagen_rejects_stroke(session, monkeypatch):
    target = imported(session, monkeypatch)
    job = request(session, target)
    session.command("skin.collagen.fill", owner=target, value=0.2)
    before = session.document
    with pytest.raises(ValueError, match="inputs changed"):
        session.command("skin.collagen.paint.commit", job=job)
    assert session.document == before


def test_cancel_rejects_stroke(session, monkeypatch):
    target = imported(session, monkeypatch)
    before = session.document
    job = request(session, target)
    session.command("skin.inspect.cancel")
    with pytest.raises(ValueError, match="incomplete"):
        session.command("skin.collagen.paint.commit", job=job)
    assert session.document == before
