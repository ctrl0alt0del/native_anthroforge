"""Candidate capture owns exact arrays independently of live previews and document state."""

import gc
import json
import zipfile
from weakref import ref

import numpy as np
import pytest

from anthroforge.application import inspection_snapshots as snapshots
from tests.test_curve_conversion import preview, source
from tests.test_surface_preview import loops
from tests.test_surface_preview import preview as surface_preview


def capture(session):
    key = source(session)
    token = preview(session, key, samples=12)
    result = session.command("inspection.capture", kind="curve_conversion", token=token)
    return key, result["snapshot"]


def test_capture_exact_path_after_cancel_and_mutation(session):
    key, snapshot = capture(session)
    value = snapshots.selected(session, snapshot)
    original = session.conversion.asset.path.array().copy()
    before, cursor = session.document, session.history.cursor
    layer = next(r for r in value.layers if r.side == "after")
    result = session.command(
        "inspection.geometry", snapshot=snapshot, layer=layer.identity, buffer="samples"
    )
    np.testing.assert_array_equal(result["values"], original)
    assert before is session.document and cursor == session.history.cursor
    session.command("curve.conversion.cancel")
    assert not session.command("inspection.capture.status", snapshot=snapshot)["current"]
    np.testing.assert_array_equal(snapshots.array(layer, "samples"), original)
    session.command("object.rename", target=key, name="Later name")


def test_capture_replaces_owner_and_explicit_release_reclaims_resources(session):
    _, snapshot = capture(session)
    held = ref(snapshots.selected(session, snapshot))
    token = session.conversion.token
    second = session.command("inspection.capture", kind="curve_conversion", token=token)
    gc.collect()
    assert held() is None
    with pytest.raises(ValueError, match="released"):
        session.command("inspection.capture.status", snapshot=snapshot)
    held = ref(snapshots.selected(session, second["snapshot"]))
    session.command("inspection.release", snapshot=second["snapshot"])
    gc.collect()
    assert held() is None


def test_surface_connectivity_reconstructs_from_bounded_pages(session):
    token = surface_preview(session, curves=loops(session))
    result = session.command("inspection.capture", kind="surface", token=token)
    layer = result["layers"][0]["id"]
    for name, index in snapshots.MESH_BUFFERS.items():
        expected = session.surface_preview.asset.mesh.array(index)
        collected = geometry_pages(session, result["snapshot"], layer, name)
        np.testing.assert_array_equal(collected, expected)


def geometry_pages(session, snapshot, layer, name):
    rows, offset = [], 0
    while offset is not None:
        page = session.command(
            "inspection.geometry",
            snapshot=snapshot,
            layer=layer,
            buffer=name,
            offset=offset,
            limit=5,
        )
        rows.extend(page["values"])
        offset = page["next_offset"]
    return rows


def test_numerical_export_survives_preview_cancel_without_qt(session, tmp_path):
    _, snapshot = capture(session)
    session.command("curve.conversion.cancel")
    output = tmp_path / "candidate.afinspection.zip"
    session.command(
        "inspection.export", path=str(output), snapshot=snapshot, images=False, wait=True
    )
    with zipfile.ZipFile(output) as archive:
        metadata = json.loads(archive.read("inspection.json"))
        assert metadata["snapshot"] == snapshot and metadata["schema_version"] == 2
        assert "image.png" not in archive.namelist()
        assert any(name.endswith("samples.npy") for name in archive.namelist())


def test_rejected_capture_does_not_release_existing_snapshot(session):
    key, snapshot = capture(session)
    point = session.document.object(key).points[1].id
    session.command("curve.point.update", curve=key, point=point, position=[0, 2, 0])
    session.wait()
    with pytest.raises(ValueError, match="current candidate"):
        session.command(
            "inspection.capture", kind="curve_conversion", token=session.conversion.token
        )
    assert snapshots.selected(session, snapshot)


def test_export_failure_preserves_snapshot_and_previous_archive(session, tmp_path, monkeypatch):
    from anthroforge.application import report_renderer

    _, snapshot = capture(session)
    output = tmp_path / "candidate.afinspection.zip"
    output.write_bytes(b"previous archive")
    monkeypatch.setattr(report_renderer, "render_scene", failed_renderer)
    with pytest.raises(ValueError, match="renderer failed"):
        session.command("inspection.export", path=str(output), snapshot=snapshot, wait=True)
    assert output.read_bytes() == b"previous archive"
    session.command(
        "inspection.export", path=str(output), snapshot=snapshot, images=False, wait=True
    )
    assert zipfile.is_zipfile(output)


def failed_renderer(*args):
    raise ValueError("renderer failed for test")
