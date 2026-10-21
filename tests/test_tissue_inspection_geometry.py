"""Real crossing fixtures, material correspondence and advisory query scope."""

import numpy as np
import pytest

from anthroforge.core.entities import IDENTITY
from anthroforge.native import inspection, tissue_parts
from anthroforge.native.mesh import NativeCancellation
from tests.test_tissue_intersection_policy import CASE, fixture
from tests.test_tissue_shape_workflow import create
from tests.test_tissue_workflow import assembly


def test_permitted_control_point_crossings_have_locatable_witnesses(session):
    base, parts = fixture(session.engine)
    output = tissue_parts.evaluate(base, parts, "a", CASE["reverse"])
    before = output.array(0).copy()
    ids, bounds, truncated = inspection.findings(output, IDENTITY, [], [], 512, 0)
    assert any(row[0] == 2 for row in ids) and not truncated
    for row, box in zip(ids, bounds, strict=True):
        points = np.array(inspection.face_lines(output, IDENTITY, row[2]))
        assert (points >= np.array(box[:3]) - 1e-12).all()
        assert (points <= np.array(box[3:]) + 1e-12).all()
    np.testing.assert_array_equal(output.array(0), before)


def test_crossing_scan_limit_and_cooperative_cancel(session):
    base, parts = fixture(session.engine)
    output = tissue_parts.evaluate(base, parts, "a", CASE["reverse"])
    assert inspection.findings(output, IDENTITY, [], [], 1, 0)[2]
    cancel = NativeCancellation(session.engine)
    cancel.set()
    with pytest.raises(ValueError, match="[Cc]ancel"):
        inspection.findings(output, IDENTITY, [], [], 512, cancel.handle)


def triangle(engine, vertices):
    return engine.create_mesh(vertices, [0, 1, 2], [0, 3])


def test_crossings_exclude_coplanar_contact_and_respect_world_transforms(session):
    first = triangle(session.engine, [[-1, -1, 0], [1, -1, 0], [0, 1, 0]])
    other = triangle(session.engine, [[0, -0.5, -1], [0, -0.5, 1], [0.5, 0.5, 0]])
    ids, _, _ = inspection.findings(first, IDENTITY, [other], [IDENTITY], 32, 0)
    assert [r[0] for r in ids] == [3]
    assert not inspection.findings(first, IDENTITY, [first], [IDENTITY], 32, 0)[0]
    translated = list(IDENTITY)
    translated[3] = 10
    assert not inspection.findings(first, IDENTITY, [other], [translated], 32, 0)[0]


@pytest.mark.parametrize("envelope", [False, True])
def test_cropped_comparison_uses_material_correspondence(session, envelope):
    _, _, key = assembly(session)
    session.command("tissue.configure", target=key, changes=dict(both_sides=envelope))
    session.wait()
    session.command("tissue.crop", target=key, changes=dict(enabled=True, origin=[0.5, 0, 0]))
    session.wait()
    session.command("tissue.inspect.compare", target=key, stage="intrinsic", reference="rest")
    session.wait()
    status = session.command("tissue.inspect.status", kind="comparison")
    assert status["state"] == "ready", status
    assert status["report"]["maximum"] < 1e-10


def test_structural_backing_and_constraint_weights_are_explained(session):
    _, source, _ = assembly(session)
    key = create(session, source)
    session.command("tissue.constraint.add", target=key, mask="ALL")
    session.wait()
    mesh = session.assets[session.document.object(key).final_result.asset].mesh
    face = backing_triangle(mesh)
    session.command(
        "tissue.inspect.point", target=key, stage="final", triangle=face, weights=[1, 0, 0]
    )
    session.wait()
    status = session.command("tissue.inspect.status", kind="point")
    assert status["state"] == "ready", status
    assert status["report"]["constraints"][0]["fixed_fraction"] == 1
    assert status["report"]["point"]["backing"] == 1


def backing_triangle(mesh):
    return next(
        i
        for i in range(mesh.counts[3])
        if inspection.point(mesh, None, i, [1, 0, 0])["backing"] == 1
    )


def test_comparison_scale_and_same_base_are_not_resampled(session):
    base, parts = fixture(session.engine)
    output = tissue_parts.evaluate(base, parts, "a", CASE["reverse"])
    local = inspection.Comparison(base, output, source=True)
    matrix = np.array(IDENTITY).reshape(4, 4)
    matrix[:3, :3] *= 3
    world = inspection.Comparison(base, output, source=True, frame=matrix.ravel())
    np.testing.assert_allclose(world.stats, np.array(local.stats) * 3, atol=1e-12)
    assert inspection.Comparison(base, base).stats == (0, 0, 0, 0)
