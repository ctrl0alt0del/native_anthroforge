"""Surface consumers honor ordinary frames, independent copies and source ownership."""

import numpy as np

from anthroforge.application.curve_sources import world
from anthroforge.native.components import transformed
from tests.test_shared_curves import move
from tests.test_surface_workflow import curve, surface, vertices


def placed(session, target):
    return transformed(
        session.engine, vertices(session, target), world(session.engine, session.document, target)
    )


def parented(session):
    root = session.command("scp.empty", name="Assembly")
    a, b = curve(session), curve(session, 0.4)
    for key in (a, b):
        session.command("object.reparent", target=key, parent=root)
    target = surface(session, [a, b], parent=root)
    return root, a, b, target


def test_surface_shared_parent_moves_once_and_reparent_preserves_world(session):
    root, a, _, target = parented(session)
    before = placed(session, target)
    move(session, root, 0.5, "scp.transform")
    np.testing.assert_allclose(placed(session, target), before + [0.5, 0, 0])
    session.command("object.reparent", target=a)
    session.wait()
    np.testing.assert_allclose(placed(session, target), before + [0.5, 0, 0])
    session.command("object.reparent", target=target)
    session.wait()
    np.testing.assert_allclose(placed(session, target), before + [0.5, 0, 0])
    assert not session.scheduler.errors


def test_surface_parent_deletion_retains_placement_references_and_undo(session):
    root, _, _, target = parented(session)
    move(session, root, 0.5, "scp.transform")
    before = placed(session, target)
    session.command("scp.delete", entity=root)
    session.wait()
    item = session.document.object(target)
    assert not item.parent and not any(u.reference_frame == root for u in item.curves)
    np.testing.assert_allclose(placed(session, target), before)
    session.command("undo")
    session.wait()
    np.testing.assert_allclose(placed(session, target), before)
    assert session.document.object(target).parent == root


def test_surface_independence_remaps_closed_correspondence_and_leaves_other_consumer(session):
    a, b = curve(session, closed=True), curve(session, 0.4, closed=True)
    first, second = surface(session, [a, b]), surface(session, [a, b])
    before = vertices(session, first)
    copied = session.command("consumer.make_independent", entity=first, curve=a)
    session.wait()
    item = session.document.object(first)
    assert item.alignment[0].point in {p.id for p in session.document.object(copied).points}
    assert session.document.registry.consumers[a] == {second}
    np.testing.assert_allclose(vertices(session, first), before)
    move(session, a, 0.25)
    np.testing.assert_allclose(vertices(session, first), before)
    assert not np.allclose(vertices(session, second), before)


def test_surface_origin_relocation_preserves_world(session, assembly):
    _, root = assembly
    a, b = curve(session), curve(session, 0.4)
    for key in (a, b):
        session.command("object.reparent", target=key, parent=root)
    target = surface(session, [a, b], parent=root)
    before = placed(session, target)
    session.command("scp.origin", entity=root)
    session.wait()
    np.testing.assert_allclose(placed(session, target), before, atol=1e-12)
    assert not session.scheduler.errors
