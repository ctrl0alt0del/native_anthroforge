"""Independent construction graphs retain shape, internal sharing and external anchoring."""

import numpy as np
import pytest

from anthroforge.application.source_graph_copy import required
from anthroforge.core.fibers import Fiber
from tests.test_anchor_operations import scene
from tests.test_fiber_creation import bind
from tests.test_junction_workflow import reference
from tests.test_surface_workflow import curve
from tests.test_tissue_parts_workflow import branched_tissue
from tests.test_tissue_workflow import assembly, mesh, roundtrip


def test_shared_membrane_copy_is_independent_and_keeps_external_bone_binding(session, tmp_path):
    bone, source, target = assembly(session)
    before = mesh(session, target)
    graph = required(session.document, source)
    records = {key: session.document.object(key) for key in graph}
    copied = session.command("consumer.make_independent", entity=target)
    session.wait()
    assert copied != source and not graph & required(session.document, copied)
    assert all(session.document.object(key) == record for key, record in records.items())
    np.testing.assert_allclose(mesh(session, target), before, atol=1e-12)
    exercise_copy(session, source, copied, bone, target, before)
    roundtrip(session, tmp_path / "independent.anthroforge")
    assert session.document.object(target).source == copied


def exercise_copy(session, source, copied, bone, target, before):
    original_curve = session.document.object(source).curves[0].curve
    session.command(
        "curve.point.update", **reference(session, original_curve, 1), position=[0.3, 0.2, 0.8]
    )
    session.wait()
    np.testing.assert_allclose(mesh(session, target), before, atol=1e-12)
    fibers = [session.document.object(u.curve) for u in session.document.object(copied).curves]
    assert all(isinstance(f, Fiber) and {b.target for b in f.bindings} == {bone} for f in fibers)
    session.command("scp.transform", entity=bone, values=[0, 0, 0.2, 0, 0, 0, 1, 1, 1])
    session.wait()
    np.testing.assert_allclose(mesh(session, target), before + [0, 0, 0.2], atol=1e-8)


def test_branched_copy_remaps_parts_and_junctions_once_with_one_action_undo(session):
    source, target, branch = branched_tissue(session)
    session.command("tissue.inflation", target=target, part=branch, changes=dict(amount=0.13))
    session.wait()
    before, original = mesh(session, target), session.document
    copied = session.command("consumer.make_independent", entity=target)
    session.wait()
    verify_branch_copy(session, target, copied, branch, before)
    session.command("undo")
    session.wait()
    assert session.document.object(target).source == source
    assert len(session.document.objects) == len(original.objects)
    session.command("redo")
    session.wait()
    verify_branch_copy(session, target, copied, branch, before)


def verify_branch_copy(session, target, copied, branch, before):
    item, base = session.document.object(target), session.document.object(copied)
    new_branch = base.branches[0].id
    assert new_branch != branch and base.accepted_parts == ("main", new_branch)
    assert item.base_state.parts == base.accepted_parts
    assert next(p for p in item.parts if p.id == new_branch).a.inflation.amount == 0.13
    for key in base.branches[0].junctions:
        incident = [
            c
            for c in session.document.objects
            if isinstance(c, Fiber) and any(p.junction == key for p in c.points)
        ]
        assert len(incident) == 2 and {c.id for c in incident} <= required(session.document, copied)
    np.testing.assert_allclose(mesh(session, target), before, atol=1e-12)


@pytest.mark.parametrize("kind", ["POINT", "CURVE"])
def test_anchor_and_fiber_source_copy_preserves_accepted_geometry(session, kind):
    parent, _, anchor = scene(session)
    source = anchor.id if kind == "POINT" else bind(session, parent, curve(session, 0)).id
    target = session.command("tissue.create", source=source, preset="CUSTOM")
    session.wait()
    before = mesh(session, target)
    copied = session.command("consumer.make_independent", entity=target)
    session.wait()
    assert copied != source
    assert type(session.document.object(copied)) is type(session.document.object(source))
    np.testing.assert_allclose(mesh(session, target), before, atol=1e-12)


def test_pending_manual_membrane_copy_preserves_accepted_layout(session):
    source, target, branch = branched_tissue(session)
    session.command("update_mode", entity=source, mode="MANUAL")
    session.command("surface.branch.remove", target=source, branch=branch)
    session.wait()
    before = mesh(session, target)
    copied = session.command("consumer.make_independent", entity=target)
    session.wait()
    base = session.document.object(copied)
    assert base.kind == "LOFT" and base.accepted_kind == "BRANCHED"
    assert len(base.accepted_parts) == 2 and base.accepted_parts[1] != branch
    assert session.document.object(target).base_state.parts == base.accepted_parts
    np.testing.assert_allclose(mesh(session, target), before, atol=1e-12)
