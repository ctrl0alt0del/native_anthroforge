"""Branched surfaces consume explicit shared curves through the normal geometry lifecycle."""

import numpy as np
import pytest

from tests.test_junction_workflow import reference
from tests.test_native_surface_branches import FIXTURE
from tests.test_surface_workflow import surface, vertices


def scene(session):
    keys = source_curves(session)
    for index, key in enumerate(keys[2:], 1):
        session.command(
            "junction.create",
            source=reference(session, keys[0], index),
            targets=[reference(session, key)],
        )
    session.wait()
    target = surface(session, keys[:2])
    return keys, target


def source_curves(session):
    keys = []
    for row in FIXTURE["cases"][0]["rows"]:
        keys.append(
            session.command(
                "curve.create", points=[dict(position=p) for p in row], engine="POLYLINE"
            )
        )
    session.wait()
    return keys


def branched(session):
    keys, target = scene(session)
    branch = session.command("surface.branch.add", target=target, boundary=keys[0], curves=keys[2:])
    session.wait()
    assert len(vertices(session, target))
    return keys, target, branch


def test_branch_creation_undo_and_deletion_preserve_sources(session):
    keys, target, _ = branched(session)
    item = session.document.object(target)
    assert item.kind == "BRANCHED" and item.main == tuple(keys[:2])
    np.testing.assert_allclose(
        vertices(session, target), FIXTURE["cases"][0]["vertices"], atol=1e-10
    )
    session.command("undo")
    session.wait()
    assert session.document.object(target).kind == "LOFT"
    session.command("redo")
    session.wait()
    assert session.document.object(target).kind == "BRANCHED"
    session.command("object.delete", target=target)
    assert set(keys) <= session.document.registry.records.keys()


def test_shared_edit_recomputes_branch_and_roundtrip_keeps_correspondence(session, tmp_path):
    keys, target, branch = branched(session)
    before = vertices(session, target)
    session.command("curve.point.update", **reference(session, keys[2]), position=[0.2, 0, 0.2])
    session.wait()
    assert not np.array_equal(vertices(session, target), before)
    location = tmp_path / "branch.anthroforge"
    session.command("save", path=str(location), blocked_policy="wait")
    session.wait()
    session.command("open", path=str(location))
    session.wait()
    assert session.document.object(target).branches[0].id == branch
    assert len(vertices(session, target))


def test_branch_policy_rejects_unresolved_junction_detach_and_closed_inputs(session):
    keys, target, _ = branched(session)
    joint = session.document.object(keys[0]).points[1].junction
    with pytest.raises(ValueError, match="explicit junctions"):
        session.command("junction.remove", junction=joint)
    with pytest.raises(ValueError, match="closure"):
        session.command("curve.edit", curve=keys[2], closed=True)
    assert session.document.object(target).result.status == "ready"


def test_removing_branch_unlocks_junction_and_leaves_last_loft(session):
    keys, target, branch = branched(session)
    session.command("surface.branch.remove", target=target, branch=branch)
    session.wait()
    item = session.document.object(target)
    assert item.kind == "LOFT" and not item.branches
    assert tuple(u.curve for u in item.curves) == tuple(keys[:2])
    joint = session.document.object(keys[0]).points[1].junction
    session.command("junction.remove", junction=joint)
    session.wait()
    assert len(vertices(session, target))
