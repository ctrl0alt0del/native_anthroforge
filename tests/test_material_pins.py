"""Accepted structural locations survive refinement, Manual inputs, history and schema 4."""

import numpy as np

from anthroforge.native import material_pins
from anthroforge.native.tissue_stacking import MaterialLease
from tests.conftest import CUBE
from tests.test_fiber_creation import bind, path
from tests.test_surface_branches import branched
from tests.test_surface_workflow import curve, surface
from tests.test_tissue_workflow import roundtrip


def protected_curve(session, y):
    key = session.command(
        "curve.create",
        engine="POLYLINE",
        points=[dict(position=[x, y, 0.7], stacking_fixed=(x == 0.25)) for x in (0, 0.25, 1)],
    )
    session.wait()
    return key


def assembly(session):
    bone = session.command("import", path=str(CUBE), units=1.0)["entity_id"]
    session.wait()
    fibers = [bind(session, bone, protected_curve(session, y)).id for y in (0, 0.3, 0.6)]
    membrane = surface(session, fibers, strips=2, exact=False)
    target = session.command("tissue.create", source=membrane)
    session.wait()
    return fibers, membrane, target


def accepted_mesh(session, target):
    result = session.document.object(target).result
    assert result.status == "ready", result.error
    return session.assets[result.asset].mesh


def exact_points(session, target):
    item = session.document.object(target)
    meshes = [
        session.assets[getattr(item, phase + "_result").asset].mesh
        for phase in ("base", "rest", "intrinsic")
    ]
    lease = MaterialLease(*meshes, item)
    material = lease.domain(1).material
    count = material.constraint_count
    ids = np.ctypeslib.as_array(material.constraints, (4 * count,)).reshape(-1, 4)
    weights = np.ctypeslib.as_array(material.constraint_weights, (4 * count,)).reshape(-1, 4)
    points = np.sum(meshes[0].array(0)[ids] * weights[:, :, None], axis=1)
    return points, weights.copy()


def test_structural_rows_remain_exact_after_refinement_without_pinning_neighbors(session):
    _, membrane, target = assembly(session)
    source = accepted_mesh(session, membrane)
    assert len(material_pins.array(source)) == 9
    points, weights = exact_points(session, target)
    np.testing.assert_allclose(points[4], [0.25, 0.3, 0.7], atol=1e-10)
    assert np.count_nonzero(weights[4] > 1e-10) > 1
    assert np.isclose(weights[4].sum(), 1)


def test_manual_membrane_keeps_pin_snapshot_until_explicit_evaluation_and_saving(session, tmp_path):
    fibers, membrane, _ = assembly(session)
    session.command("update_mode", entity=membrane, mode="MANUAL")
    before = material_pins.array(accepted_mesh(session, membrane)).copy()
    point = session.document.object(fibers[1]).points[1].id
    session.command("curve.point.update", curve=fibers[1], point=point, stacking_fixed=False)
    session.wait()
    retained = session.assets[session.document.object(membrane).result.asset].mesh
    np.testing.assert_array_equal(material_pins.array(retained), before)
    roundtrip(session, tmp_path / "pins.anthroforge")
    session.command("evaluate", entities=[membrane])
    session.wait()
    assert len(material_pins.array(accepted_mesh(session, membrane))) == len(before) - 1


def test_protection_edit_on_moved_fiber_preserves_shape_bindings_and_undo(session):
    fibers, _, _ = assembly(session)
    key, before = fibers[1], session.document.object(fibers[1])
    bone = before.bindings[0].target
    session.command("scp.transform", entity=bone, values=[0, 0, 0.3, 0, 0, 0, 1, 1, 1])
    session.wait()
    shape, attachment = path(session, key), session.document.object(key).attachment_asset
    session.command(
        "curve.point.update", curve=key, point=before.points[1].id, protected_crease=True
    )
    session.wait()
    assert session.document.object(key).attachment_asset == attachment
    np.testing.assert_array_equal(path(session, key), shape)
    session.command("undo")
    assert not session.document.object(key).points[1].protected_crease


def test_patch_constraints_keep_closed_boundary_correspondence(session):
    key = curve(session, closed=True)
    point = session.document.object(key).points[2]
    session.command("curve.point.update", curve=key, point=point.id, protected_crease=True)
    session.wait()
    target = surface(session, [key], "PATCH")
    mesh = accepted_mesh(session, target)
    rows = material_pins.array(mesh)
    assert len(rows) == 1 and rows[0, 0] == -1
    values = mesh.array(0)[rows[0, 3:7].astype(int)] * rows[0, 7:, None]
    np.testing.assert_allclose(values.sum(axis=0), point.position, atol=1e-10)


def test_branch_point_protection_uses_explicit_part_coordinates(session):
    keys, target, _ = branched(session)
    point = session.document.object(keys[2]).points[-1]
    session.command("curve.point.update", curve=keys[2], point=point.id, stacking_fixed=True)
    session.wait()
    rows = material_pins.array(accepted_mesh(session, target))
    assert len(rows) == 1
    np.testing.assert_allclose(rows[0, :3], [1, 0, 1], atol=1e-12)
