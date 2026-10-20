"""Automatic topology remains explicit, deterministic and undoable after resolution."""

import numpy as np
import pytest

from tests.test_branch_creation import branch, curve
from tests.test_native_surface_branches import FIXTURE
from tests.test_surface_branches import scene
from tests.test_surface_workflow import vertices


def test_auto_surface_recognizes_junctions_and_matches_existing_branch_fixture(session):
    keys, _ = scene(session)
    target = session.command("surface.create", curves=keys, kind="AUTO")
    session.wait()
    item = next(
        o
        for o in session.document.objects
        if o.result.asset and o.name == "Surface" and getattr(o, "kind", "") == "BRANCHED"
    )
    assert item.main == tuple(keys[:2]) and len(item.branches) == 1
    np.testing.assert_allclose(
        vertices(session, item.id), FIXTURE["cases"][0]["vertices"], atol=1e-10
    )
    assert session.scheduler.registry.by_id[target].state == "succeeded"


def ambiguous(session):
    source = session.command("curve.create", points=[dict(position=[0, i, 0]) for i in range(6)])
    other = curve(session)
    children = [branch(session, source, i) for i in range(1, 5)]
    session.wait()
    return [source, other, *children]


def test_four_roots_require_explicit_grouping_without_mutation(session):
    keys = ambiguous(session)
    info = session.command("surface.grouping", curves=keys)
    assert info["ambiguous"]
    before = session.document
    with pytest.raises(ValueError, match="Ambiguous"):
        session.command("surface.create", curves=keys, kind="AUTO")
    assert session.document == before


def test_explicit_split_groups_and_source_preserving_undo(session):
    keys = ambiguous(session)
    plan = dict(
        main=keys[:2],
        branches=[
            dict(boundary=keys[0], curves=keys[2:4]),
            dict(boundary=keys[0], curves=keys[4:]),
        ],
    )
    session.command("surface.create", curves=keys, kind="AUTO", grouping=plan)
    session.wait()
    item = session.document.objects[-1]
    assert len(item.branches) == 2 and item.result.status == "ready"
    session.command("undo")
    assert set(session.document.registry.records) == set(keys)


def test_single_connected_branch_is_not_silently_lofted(session):
    source, other = curve(session), curve(session)
    child = branch(session, source)
    with pytest.raises(ValueError, match="two distinct interior"):
        session.command("surface.create", curves=[source, other, child], kind="AUTO")
