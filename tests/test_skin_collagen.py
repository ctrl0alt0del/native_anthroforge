"""Painted collagen is a source-domain field with coherent undo and saved ownership."""

import numpy as np
import pytest

from anthroforge.application import skin_capture, skin_collagen, skin_operations, storage
from tests.test_skin_jobs import imported


def test_fill_clear_and_undo_preserve_source_geometry(session, monkeypatch):
    owner = imported(session, monkeypatch)
    item = session.document.object(owner)
    session.command("skin.collagen.fill", owner=owner, value=0.25)
    setting = skin_operations.settings_for(session.document.skin, owner)
    assert setting.collagen_mode == "PAINTED" and setting.painted
    np.testing.assert_array_equal(session.resources.skin[setting.painted].arrays["collagen"], 0.25)
    session.command("skin.collagen.clear", owner=owner)
    assert skin_operations.settings_for(session.document.skin, owner).collagen_mode == "UNIFORM"
    session.command("undo")
    assert skin_operations.settings_for(session.document.skin, owner) == setting
    assert session.document.object(owner) == item


def test_zero_field_is_authoritative_and_survives_roundtrip(session, monkeypatch, tmp_path):
    owner = imported(session, monkeypatch)
    session.command("skin.collagen.fill", owner=owner, value=0)
    captured = skin_capture.capture(session.engine, session.document, session.resources)
    np.testing.assert_array_equal(captured.collagen, 0)
    path = tmp_path / "painted.anthroforge"
    session.command("save", path=str(path), blocked_policy="wait")
    session.wait()
    document, resources = storage.read_package(path, session.engine)
    setting = skin_operations.settings_for(document.skin, owner)
    assert setting.painted in resources.skin
    np.testing.assert_array_equal(resources.skin[setting.painted].arrays["collagen"], 0)


def test_invalid_weights_and_wrong_owner_do_not_change_document(session, monkeypatch):
    owner = imported(session, monkeypatch)
    before = session.document
    for weights in ([1], [float("nan")] * 8, [-1] * 8, [2] * 8):
        with pytest.raises(ValueError, match="weight"):
            session.command("skin.collagen.set", owner=owner, values=weights)
    with pytest.raises(ValueError, match="SCP"):
        session.command("skin.collagen.fill", owner="missing")
    assert session.document == before


def test_membership_validation_detects_same_count_different_connectivity(session, monkeypatch):
    owner = imported(session, monkeypatch)
    session.command("skin.collagen.fill", owner=owner, value=0.3)
    mesh = skin_collagen.mesh(session, owner)
    setting = skin_operations.settings_for(session.document.skin, owner)
    data = session.resources.skin[setting.painted]
    assert skin_collagen.matching(data, mesh)
    corners = mesh.array(1).copy()
    end = mesh.array(2)[1]
    corners[:end] = corners[:end][::-1]
    changed = session.engine.create_mesh(mesh.array(0), corners, mesh.array(2))
    assert not skin_collagen.matching(data, changed)
