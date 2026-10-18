"""Conversions and copied anatomical assemblies retain explicit internal junctions."""

import numpy as np

from tests.test_curve_conversion import preview
from tests.test_curve_conversion import source as curve
from tests.test_fiber_copy import body
from tests.test_fiber_junctions import connected
from tests.test_junction_workflow import reference
from tests.test_path_lifecycle import path


def test_sampled_conversion_preserves_interior_junction_identity(session):
    a, b = curve(session), curve(session)
    ref = reference(session, a, 1)
    joint = session.command("junction.create", source=ref, targets=[reference(session, b)])
    session.wait()
    token = preview(session, a, samples=13)
    session.command("curve.conversion.accept", token=token)
    session.wait()
    item = session.document.object(a)
    point = next(p for p in item.points if p.id == ref["point"])
    assert point.junction == joint and len(item.points) == 13
    assert session.document.object(b).result.status == "ready"


def test_routing_conversion_requires_shared_constraints(session):
    a, b = curve(session), curve(session)
    session.command(
        "junction.create", source=reference(session, a, 1), targets=[reference(session, b)]
    )
    session.wait()
    item = session.document.object(a)
    routing_preview(session, item)
    session.wait()
    status = session.command("curve.conversion.status")
    assert status["state"] == "failed" and "junction point" in status["error"]


def routing_preview(session, item):
    session.command(
        "curve.conversion.preview",
        curve=item.id,
        engine="ROUTED",
        mode="AUTHORED",
        points=[item.points[0].id, item.points[-1].id],
    )


def copied_pair(session):
    root, _, a, b, joint = connected(session)
    body(session, a, root)
    body(session, b, root)
    new = session.command("scp.duplicate", entity=root)
    session.wait()
    shared = next(j for j in session.document.junctions if j.id != joint)
    source = session.document.object(shared.source.curve)
    assert source.id != a and source.bindings[0].target == new
    copied = [
        o
        for o in session.document.objects
        if any(p.junction == shared.id for p in getattr(o, "points", ()))
    ]
    return (a, b), copied, shared


def test_copied_set_shares_only_its_new_junction_and_keeps_accepted_metadata(session):
    originals, copies, shared = copied_pair(session)
    assert len(copies) == 2
    before = {key: path(session, key) for key in originals}
    check_metadata_and_edit(session, copies, shared)
    session.wait()
    for key in originals:
        np.testing.assert_array_equal(path(session, key), before[key])
    np.testing.assert_allclose(
        path(session, copies[0].id)[0, :3], path(session, copies[1].id)[0, :3]
    )


def check_metadata_and_edit(session, copies, shared):
    for item in copies:
        assert item.result.status == "ready", item.result.error
        accepted = session.resources.paths[item.result.asset].authored
        assert any(p.junction == shared.id for p in accepted.points)
    session.command(
        "curve.point.update",
        curve=copies[0].id,
        point=copies[0].points[0].id,
        position=[-0.2, 0.2, 0.9],
    )
