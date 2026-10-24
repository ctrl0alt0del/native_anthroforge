"""Mirrored final surfaces are frozen providers; source jobs remain the only writers."""

import numpy as np

from anthroforge.application.tissue_stack_scene import StackScene, identity
from anthroforge.core.mirroring import MirrorInstance
from tests.test_tissue_stack_workflow import assembly, current


def array(domain, field):
    return np.ctypeslib.as_array(getattr(domain, field), (domain.vertices * 3,)).reshape(-1, 3)


def test_mirror_domains_reflect_geometry_and_directions_and_exclude_own_instance(session):
    bone, first, second = assembly(session)
    before = current(session, first)
    session.command("mirror.configure", target=bone, enabled=True, axis="Z", shift=3)
    session.command("wait")
    scene = StackScene(session.document, session.resources, second, 0)
    original = scene.domains[identity(first, "a")]
    mirrored = scene.domains[identity(MirrorInstance(first, bone).id, "a")]
    expected = array(original, "own") * [1, 1, -1] + [0, 0, 6]
    np.testing.assert_allclose(array(mirrored, "own"), expected)
    np.testing.assert_allclose(
        array(mirrored, "direction"), array(original, "direction") * [1, 1, -1]
    )
    assert identity(MirrorInstance(second, bone).id, "a") not in scene.domains
    np.testing.assert_array_equal(current(session, first), before)


def test_mirror_instances_never_become_task_writers(session):
    bone, first, second = assembly(session)
    session.command("mirror.configure", target=bone, enabled=True, shift=3)
    session.command("wait")
    assert session.command("mirror.list", source=first)
    assert all(
        not key.startswith("mirror/")
        for job in session.scheduler.jobs
        if job.writes
        for key in job.outputs
    )
    scene = StackScene(session.document, session.resources, second, 0)
    assert MirrorInstance(first, bone).id in {owner for owner, _ in scene.leases}


def test_original_can_stack_against_another_tissues_mirrored_final_surface(session):
    bone, first, second = assembly(session)
    session.command("mirror.configure", target=bone, enabled=True, shift=0)
    session.command("wait")
    item = session.document.object(second)
    assert item.final_result.status == "ready", item.final_result.error
    assert MirrorInstance(first, bone).id in item.stack_plan.providers
    assert MirrorInstance(second, bone).id not in item.stack_plan.providers


def test_shifted_provider_does_not_override_incompatible_fixed_boundaries(session):
    bone, first, second = assembly(session)
    session.command("mirror.configure", target=bone, enabled=True, shift=0.05)
    session.command("wait")
    item = session.document.object(second)
    assert item.final_result.status == "failed"
    assert "STACK_VECTOR_QP_FAILED" in item.final_result.error
    assert item.result.status == "unstacked"
    assert item.result.asset == item.intrinsic_result.asset


def test_every_tissue_stage_is_exact_reflection_and_shares_its_mesh(session):
    from anthroforge.application import tissue_inspection_stages as stages

    bone, first, second = assembly(session)
    session.command("mirror.configure", target=bone, enabled=True, axis="Y", shift=3)
    session.command("wait")
    target = MirrorInstance(first, bone).id
    matrix = np.array(session.document.mirrors.rules[bone].frame).reshape(4, 4)
    for stage in stages.STAGES:
        assert stages.mesh(session, target, stage) is stages.mesh(session, first, stage)
        expected = matrix @ np.array(stages.instance_frame(session, first, stage)).reshape(4, 4)
        np.testing.assert_array_equal(
            np.array(stages.instance_frame(session, target, stage)).reshape(4, 4), expected
        )


def test_excluded_provider_intent_allows_rule_removal_and_survives_reactivation(session):
    bone, first, second = assembly(session)
    session.command("mirror.configure", target=bone, enabled=True)
    session.wait()
    other = MirrorInstance(first, bone).id
    session.command("tissue.stacking.relationship", target=second, other=other, excluded=True)
    session.wait()
    session.command("mirror.configure", target=bone, enabled=False)
    session.wait()
    assert session.document.object(second).final_result.status == "ready"
    assert session.document.object(second).stack_relationships[0].other == other
    session.command("mirror.configure", target=bone, enabled=True)
    session.wait()
    assert other not in session.document.object(second).stack_plan.providers
