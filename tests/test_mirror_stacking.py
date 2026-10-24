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
    np.testing.assert_allclose(array(mirrored, "direction"), array(original, "direction") * [1, 1, -1])
    assert identity(MirrorInstance(second, bone).id, "a") not in scene.domains
    np.testing.assert_array_equal(current(session, first), before)


def test_mirror_instances_never_become_task_writers(session):
    bone, first, second = assembly(session)
    session.command("mirror.configure", target=bone, enabled=True, shift=3)
    session.command("wait")
    assert session.command("mirror.list", source=first)
    assert all(not key.startswith("mirror/") for job in session.scheduler.jobs if job.writes
               for key in job.outputs)
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
