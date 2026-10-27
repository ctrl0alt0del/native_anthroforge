"""Ordinary anatomical movement deforms skin without changing topology or bindings."""

import numpy as np

from tests.test_skin_reference import build, topology


def translate(session, key, value):
    session.command("scp.transform", entity=key, values=[*value, 0, 0, 0, 1, 1, 1])
    session.wait()


def test_anatomy_motion_preserves_skin_connectivity_and_reference(session):
    bone = topology(session)
    skin = build(session)
    before = session.assets[skin.final.asset].mesh
    translate(session, bone, [0, 0.2, 0])
    after = session.document.skin
    assert after.final.status == "ready", after.final.error
    assert after.final.revision > skin.final.revision and after.reference == skin.reference
    mesh = session.assets[after.final.asset].mesh
    for kind in (1, 2, 3, 4):
        np.testing.assert_array_equal(mesh.array(kind), before.array(kind))
    np.testing.assert_allclose(mesh.array(0), before.array(0) + [0, 0.2, 0], atol=1e-8)


def test_explicit_evaluation_and_manual_anatomy_keep_fixed_reference(session):
    topology(session)
    skin = build(session)
    key = session.command("skin.evaluate")
    session.wait()
    assert session.scheduler.registry.by_id[key].state == "succeeded"
    assert session.document.skin.reference == skin.reference
    assert session.document.skin.final.revision == skin.final.revision + 1
