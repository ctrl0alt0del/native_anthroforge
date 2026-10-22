"""Accepted geometry owns the construction settings that made it, including Manual inputs."""

from dataclasses import replace

import numpy as np

from anthroforge.application import geometry_ownership, tissue_evaluation, tissue_tasks
from anthroforge.application.assets import Asset
from anthroforge.core.results import EvaluationResult
from anthroforge.core.tissue_material import TissueMaterialState
from anthroforge.core.tissues import TissueVCP
from anthroforge.native import construction as native
from anthroforge.native.tissue_stacking import MaterialLease, assemble
from tests.stacking_material_fixtures import arrays
from tests.test_tissue_workflow import assembly, roundtrip


def test_manual_edits_do_not_reinterpret_accepted_material(session, tmp_path):
    _, _, target = assembly(session)
    before = session.document.object(target).final_material
    assert before and before.base and before.rest and before.own and before.final
    session.command("update_mode", entity=target, mode="MANUAL")
    session.command("tissue.inflation", target=target, changes=dict(amount=0.12))
    session.wait()
    assert session.document.object(target).final_material == before
    roundtrip(session, tmp_path / "accepted-material.anthroforge")
    assert session.document.object(target).final_material == before
    session.command("evaluate", entities=[target])
    session.wait()
    assert session.document.object(target).final_material.parts[0].a.inflation.amount == 0.12


def test_retained_final_keeps_previous_material_resources_when_intrinsic_changes(session):
    _, _, target = assembly(session)
    before = session.document.object(target).final_material
    session.command("update_mode", entity=target, mode="MANUAL")
    session.command("tissue.inflation", target=target, changes=dict(amount=0.08))
    for phase in ("rest", "intrinsic"):
        tissue_tasks.request(session, target, phase)
        session.wait()
    geometry_ownership.collect(session)
    assert session.document.object(target).final_material == before
    meshes = [session.assets[key].mesh for key in (before.base, before.rest, before.own)]
    lease = MaterialLease(*meshes, before, frame=before.frame)
    output = assemble(lease, arrays(lease.domain(1))["own"])
    np.testing.assert_allclose(output.array(0), meshes[-1].array(0), atol=1e-12)


def test_intrinsic_uses_accepted_rest_settings_despite_pending_authored_changes(session):
    _, _, target = assembly(session)
    before = session.document.object(target)
    session.command("update_mode", entity=target, mode="MANUAL")
    session.command("tissue.configure", target=target, changes=dict(reverse=True))
    current = session.document.object(target)
    output = tissue_evaluation.evaluate(
        session.engine, session.document, session.resources, target, "intrinsic", 0
    )
    assert output.material.reverse == before.reverse and current.reverse != before.reverse
    assert output.asset == before.intrinsic_result.asset and output.mesh is None


def test_material_snapshots_do_not_increment_authored_revisions(session):
    from anthroforge.application.object_revisions import changed_ports

    _, _, target = assembly(session)
    item = session.document.object(target)
    edited = replace(item, final_material=replace(item.final_material, final="replacement"))
    assert changed_ports(item, edited) == set()


def concave_rest(session):
    mesh = session.engine.create_mesh(
        [[0, 0, 0], [1, -1, 0], [2, 0, 0], [1, 2, 0]], range(4), [0, 4]
    )
    mesh = native.joined(session.engine, [mesh], 0)
    rest = native.deformed(mesh, [[0, 0, 0], [1, 0.25, 0], [2, 0, 0], [1, 2, 0]])
    session.assets["rest"] = Asset(rest, "generated", "", 1.0, False)
    item = TissueVCP(
        name="Initial tissue", source="source", rest_result=EvaluationResult(asset="rest")
    )
    return replace(item, rest_material=TissueMaterialState(base="rest")), rest


def evaluate_intrinsic(session, item):
    return tissue_evaluation.intrinsic(session.engine, session.document, session.resources, item, 0)


def test_first_intrinsic_tessellates_its_own_shape_and_later_edits_retain_it(session):
    item, rest = concave_rest(session)
    output = evaluate_intrinsic(session, item)
    np.testing.assert_array_equal(output.mesh.array(3), [[0, 1, 3], [1, 2, 3]])
    np.testing.assert_array_equal(rest.array(3), [[0, 1, 2], [0, 2, 3]])
    session.assets["accepted"] = Asset(output.mesh, "generated", "", 1.0, False)
    moved = native.deformed(rest, [[0, 0, 0], [1, -1, 0], [2, 0, 0], [1, 2, 0]])
    session.assets["rest"] = Asset(moved, "generated", "", 1.0, False)
    item = replace(item, intrinsic_result=EvaluationResult(asset="accepted"))
    updated = evaluate_intrinsic(session, item)
    np.testing.assert_array_equal(updated.mesh.array(3), output.mesh.array(3))
    np.testing.assert_array_equal(updated.mesh.array(0), moved.array(0))
