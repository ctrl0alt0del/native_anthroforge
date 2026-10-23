"""Buried material follows its own union exterior without rewriting binding intent."""

import json
import zipfile
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from anthroforge.core.entities import IDENTITY
from anthroforge.core.segment_chain import Segment, SegmentChain
from anthroforge.native import construction, material_bindings, point_attachments, triangle_material
from anthroforge.native.mesh import NativeCancellation
from anthroforge.native.segment_chain import construct
from anthroforge.native.topology import finalize


def thumb_settings():
    path = Path(__file__).parent / "fixtures/primitives/retained_thumb.json"
    data = json.loads(path.read_text())["chain"]
    data["segments"] = tuple(Segment(**s) for s in data["segments"])
    data["profile"] = tuple(data["profile"])
    return SegmentChain(**data)


def thumb_pair(session, factor=1.05):
    settings = thumb_settings()
    segments = (replace(settings.segments[0], radius=settings.segments[0].radius * factor),)
    changed = replace(settings, segments=segments + settings.segments[1:])
    return tuple(finalize(construct(session.engine, s, 0), None, 0) for s in (settings, changed))


def bindings(mesh):
    values = np.zeros((mesh.counts[3], 28))
    values[:, :3], values[:, 3:6], values[:, 6:9] = mesh.array(3), 1 / 3, -1
    return values


def queries(before, after):
    rows, coordinates = triangle_material.arrays(before)
    source = triangle_material.source(after)[1:].reshape(-1, 3, 3)
    weights = coordinates.reshape(-1, 3, 3).mean(axis=1)
    return np.einsum("ij,ijk->ik", weights, source[rows[1:]])


def nearest_points(mesh, points):
    targets, records = point_attachments.capture(mesh.engine, [mesh.handle], [IDENTITY], points)
    records[:, 15:18] = 0
    frames = point_attachments.resolve(mesh.engine, [mesh.handle], [IDENTITY], targets, records)
    return frames.reshape(-1, 4, 4)[:, :3, 3]


@pytest.mark.parametrize("factor", [1.05, 1.72, 3.0])
def test_buried_union_material_follows_exterior_and_returns_without_rebinding(session, factor):
    before, after = thumb_pair(session, factor)
    records = bindings(before)
    frozen = records.copy()
    query = queries(before, after)
    expected = nearest_points(after, query)
    assert np.max(np.linalg.norm(expected - query, axis=1)) > 1e-4
    frames = material_bindings.frames(before, after, IDENTITY, records).reshape(-1, 4, 4)
    np.testing.assert_allclose(frames[:, :3, 3], expected, atol=1e-8)
    restored = material_bindings.frames(before, before, IDENTITY, records).reshape(-1, 4, 4)
    np.testing.assert_allclose(
        restored[:, :3, 3], before.array(0)[before.array(3)].mean(1), atol=1e-12
    )
    np.testing.assert_array_equal(records, frozen)


def test_exterior_binding_follows_post_union_deformation_and_preserves_offset(session):
    before, after = thumb_pair(session)
    records = bindings(before)
    expected = nearest_points(after, queries(before, after)) * [2, 1.5, 0.8] + [1, 2, 3]
    moved = construction.deformed(after, after.array(0) * [2, 1.5, 0.8] + [1, 2, 3])
    records[:, 17] = 0.002
    frames = material_bindings.frames(before, moved, IDENTITY, records).reshape(-1, 4, 4)
    np.testing.assert_allclose(frames[:, :3, 3], expected + frames[:, :3, 2] * 0.002, atol=1e-8)
    np.testing.assert_array_equal(triangle_material.source(after), triangle_material.source(moved))


def test_missing_legacy_chart_and_cancellation_remain_explicit(session):
    before, after = thumb_pair(session, 3)
    legacy = triangle_material.restore(after, *triangle_material.arrays(after))
    with pytest.raises(ValueError, match="Reevaluate.*construction chart"):
        material_bindings.frames(before, legacy, IDENTITY, bindings(before))
    token = NativeCancellation(session.engine)
    token.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        material_bindings.frames(before, after, IDENTITY, bindings(before), token.handle)


def stored(mesh, tmp_path):
    from anthroforge.application.assets import Asset
    from anthroforge.application.resource_storage import mesh_metadata, read_mesh, write_mesh

    asset = Asset(mesh, "generated", "", 1.0, False)
    path = tmp_path / "resource.zip"
    with zipfile.ZipFile(path, "w") as archive:
        write_mesh(archive, "union", asset)
    with zipfile.ZipFile(path) as archive:
        return read_mesh(archive, "union", mesh_metadata(asset), mesh.engine).mesh


def test_exterior_chart_roundtrip_retains_resolution_without_recomputation(session, tmp_path):
    before, after = thumb_pair(session)
    reopened = stored(after, tmp_path)
    np.testing.assert_array_equal(
        triangle_material.source(after), triangle_material.source(reopened)
    )
    original = material_bindings.frames(before, after, IDENTITY, bindings(before))
    restored = material_bindings.frames(before, reopened, IDENTITY, bindings(before))
    np.testing.assert_array_equal(original, restored)
