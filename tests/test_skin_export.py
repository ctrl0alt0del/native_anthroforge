"""Frozen skin OBJ export preserves identity, units, quads and independent update policy."""

from threading import Event

import numpy as np
import pytest

from anthroforge.application import skin_export, skin_export_writers
from tests.test_skin_reference import build, topology


def read(path):
    rows = [line.split() for line in path.read_text().splitlines()]
    vertices = np.array([[float(x) for x in r[1:]] for r in rows if r[0] == "v"])
    faces = [[int(x) - 1 for x in r[1:]] for r in rows if r[0] == "f"]
    return vertices, faces


def test_export_freezes_accepted_skin_and_preserves_quads(session, tmp_path):
    topology(session)
    skin = build(session)
    mesh = session.assets[skin.final.asset].mesh
    path = tmp_path / "skin.obj"
    before = session.document
    result = session.command("skin.export", path=str(path), policy="accepted")
    session.replace_document(name="Edited after request")
    session.wait()
    points, faces = read(path)
    np.testing.assert_array_equal(points, mesh.array(0))
    assert faces == mesh.array(1).reshape(-1, 4).tolist()
    assert f"source revision {before.revision}" in path.read_text()
    assert session.scheduler.registry.by_id[result["job"]].state == "succeeded"


def test_update_export_captures_pending_motion_without_changing_live_skin(session, tmp_path):
    bone = topology(session)
    original = build(session)
    session.command("update_mode", mode="MANUAL")
    session.command("scp.transform", entity=bone, values=[0, 0.3, 0, 0, 0, 0, 1, 1, 1])
    before = session.document
    path = tmp_path / "updated.obj"
    session.command("skin.export", path=str(path), policy="update", wait=True)
    vertices, _ = read(path)
    expected = session.assets[original.final.asset].mesh.array(0) + [0, 0.3, 0]
    np.testing.assert_allclose(vertices, expected, atol=1e-7)
    assert session.document is before and session.document.skin.final.asset == original.final.asset


def test_export_requires_skin_and_explicit_policy(session, tmp_path):
    path = str(tmp_path / "skin.obj")
    with pytest.raises(TypeError, match="policy"):
        session.command("skin.export", path=path)
    with pytest.raises(ValueError, match="Build final skin"):
        session.command("skin.export", path=path, policy="accepted")
    assert session.command("skin.export", path=path, policy="cancel")["state"] == "cancelled"


def test_atomic_export_failure_preserves_destination_and_removes_temporary(session, tmp_path):
    topology(session)
    skin = build(session)
    path = tmp_path / "skin.obj"
    path.write_text("previous file")
    cancel = Event()
    cancel.set()
    with pytest.raises(ValueError, match="cancelled"):
        skin_export.atomic_write(path, session.assets[skin.final.asset].mesh, 0, cancel)
    assert path.read_text() == "previous file"
    assert not list(tmp_path.glob(".anthroforge-skin-*"))
    with pytest.raises(ValueError, match="Unsupported"):
        skin_export_writers.writer(tmp_path / "skin.fbx")
