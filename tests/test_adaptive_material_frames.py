"""Material locations and offset frames survive changes in evaluated sampling."""

import numpy as np
import pytest

from anthroforge.core.tissue_settings import TissueInflation
from anthroforge.native import curve_surfaces, material_bindings, point_attachments, tissue_shapes
from anthroforge.native.mesh import NativeCancellation
from tests.test_material_bindings import IDENTITY, records
from tests.test_native_surfaces import row


def loft(engine, stations, closed=False):
    points = (
        [[np.cos(2 * np.pi * t), np.sin(2 * np.pi * t), 0] for t in stations]
        if closed
        else [[t, 0, 0] for t in stations]
    )
    shift = [0, 0, 1] if closed else [0, 1, 0]
    rows = [row(engine, points, closed), row(engine, np.array(points) + shift, closed)]
    return curve_surfaces.geometry(engine, rows, [1], curve_surfaces.Settings())


def all_records(mesh):
    rows = np.vstack([records(mesh, i) for i in range(mesh.counts[3])])
    rows[:, 15:18] = [0.03, -0.02, 0.04]
    return rows


def frames(mesh, rows, world=IDENTITY):
    return point_attachments.resolve(
        mesh.engine, [mesh.handle], [world], np.zeros(len(rows), dtype=np.int32), rows
    )


@pytest.mark.parametrize("shell", [False, True])
def test_resampling_preserves_material_points_tangent_normal_and_offset(session, shell):
    before = loft(session.engine, [0, 0.5, 1])
    after = loft(session.engine, [0, 0.2, 0.5, 0.8, 1])
    if shell:
        before, after = [
            tissue_shapes.normal(m, TissueInflation(amount=0.1, minimum=0.1))
            for m in (before, after)
        ]
    rows = all_records(before)
    world = np.array([[0, -0.7, 0, 0.4], [2, 0, 0, -0.3], [0, 0, 1.2, 0.1], [0, 0, 0, 1]]).ravel()
    actual = material_bindings.frames(before, after, world, rows)
    np.testing.assert_allclose(actual, frames(before, rows, world), atol=1e-10)


def test_material_frames_cancel_and_do_not_reinterpret_closure(session):
    before = loft(session.engine, [0, 0.5, 1])
    after = loft(session.engine, [0, 0.25, 0.5, 0.75], closed=True)
    with pytest.raises(ValueError, match="closure"):
        material_bindings.frames(before, after, IDENTITY, all_records(before))
    token = NativeCancellation(session.engine)
    token.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        material_bindings.frames(before, before, IDENTITY, all_records(before), token.handle)


def patch(engine, points, resolution=4):
    settings = curve_surfaces.Settings(patch=True, patch_resolution=resolution)
    return curve_surfaces.geometry(engine, [row(engine, points, True)], [], settings)


def test_patch_binding_survives_added_evaluated_corner_and_keeps_saved_capture(session):
    points = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
    before = patch(session.engine, points)
    after = patch(session.engine, [points[0], [0.4, -0.2, 0.1], *points[1:]])
    rows = all_records(before)
    result = material_bindings.frames(before, after, IDENTITY, rows)
    assert np.isfinite(result).all()
    np.testing.assert_allclose(
        material_bindings.frames(before, before, IDENTITY, rows), frames(before, rows), atol=1e-10
    )


def closed_loft(engine, points):
    rows = [row(engine, points, True), row(engine, np.array(points) + [0, 0, 1], True)]
    return curve_surfaces.geometry(engine, rows, [1], curve_surfaces.Settings())


def test_closed_seam_resampling_keeps_frames_on_both_sides_of_wrap(session):
    points = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]
    before = closed_loft(session.engine, points)
    changed = [points[0], [0.4, 0, 0], points[1], points[2], [0.5, 1, 0], points[3], [0, 0.2, 0]]
    after = closed_loft(session.engine, changed)
    rows = all_records(before)
    np.testing.assert_allclose(
        material_bindings.frames(before, after, IDENTITY, rows), frames(before, rows), atol=1e-10
    )


def branch_resampling_inputs(engine):
    from tests.test_native_surface_branches import FIXTURE, inputs

    case = FIXTURE["cases"][0]
    original, branch = inputs(engine, case)
    changed = dict(case, rows=list(case["rows"]))
    points = changed["rows"][2]
    changed["rows"][2] = [points[0], ((np.array(points[0]) + points[1]) / 2).tolist(), *points[1:]]
    rows, branch = inputs(engine, changed)
    return original, rows, branch


def test_branched_material_charts_survive_added_source_station(session):
    from anthroforge.native import surface_branches

    original, rows, branch = branch_resampling_inputs(session.engine)
    before, after = [
        surface_branches.geometry(session.engine, source, 2, [branch], curve_surfaces.Settings())
        for source in (original, rows)
    ]
    captured = all_records(before)
    np.testing.assert_allclose(
        material_bindings.frames(before, after, IDENTITY, captured),
        frames(before, captured),
        atol=1e-10,
    )


def test_tissue_material_basis_owns_coordinates_without_retaining_source_handle(session):
    import gc

    from anthroforge.native import material_basis, memory

    source = loft(session.engine, [0, 0.5, 1])
    handle = source.handle
    own = tissue_shapes.normal(source, TissueInflation(amount=0.1, minimum=0.1))
    records, coordinates = material_basis.arrays(own)
    del source
    gc.collect()
    handles = {row[0] for row in memory.snapshot(session.engine)[0]}
    assert handle not in handles
    assert len(records) and len(coordinates) and np.isfinite(coordinates).all()
