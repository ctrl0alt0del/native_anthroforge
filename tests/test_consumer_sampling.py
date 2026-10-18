"""Consumer density changes actual geometry, preserves sharing and honors incoming locks."""

import pytest


def assembly(session):
    root = session.command("scp.empty", name="Assembly")
    curve = session.command("curve.create")
    bodies = [
        session.command("primitive.from_curves", curves=[curve], kind="BODY", parent=root)
        for _ in range(2)
    ]
    session.wait(5)
    return root, curve, *bodies


def vertices(session, entity):
    return session.assets[session.document.entity(entity).asset].mesh.array(0)


def test_body_density_is_consumer_owned_and_reset_inherits_default(session):
    _, curve, first, second = assembly(session)
    before = len(vertices(session, second))
    session.command("consumer.sampling", entity=first, curve=curve, samples=12)
    session.wait(5)
    assert len(vertices(session, first)) < before == len(vertices(session, second))
    session.command("primitive.update", entity=first, samples=48)
    session.wait(5)
    assert len(vertices(session, first)) < before
    session.command("consumer.sampling", entity=first, curve=curve, samples=None)
    session.wait(5)
    assert len(vertices(session, first)) > before


def test_loft_uses_highest_requested_boundary_density(session):
    key = session.command("primitive.create", kind="LOFT")
    uses = session.document.entity(key).primitive.curves
    session.command("consumer.sampling", entity=key, curve=uses[0].curve, samples=48)
    session.wait(5)
    assert len(vertices(session, key)) == 96
    session.command("consumer.sampling", entity=key, curve=uses[1].curve, samples=64)
    session.wait(5)
    assert len(vertices(session, key)) == 128
    session.command("undo")
    session.wait(5)
    assert len(vertices(session, key)) == 96


def test_consumer_density_is_locked_only_by_its_own_incoming_attachments(session):
    _, curve, first, second = assembly(session)
    child = session.command("scp.empty", name="Child", parent=first)
    with pytest.raises(ValueError, match=child):
        session.command("consumer.sampling", entity=first, curve=curve, samples=12)
    session.command("consumer.sampling", entity=second, curve=curve, samples=12)
    session.command("scp.delete", entity=child)
    session.command("consumer.sampling", entity=first, curve=curve, samples=12)
    session.wait(5)
    assert len(vertices(session, first)) == len(vertices(session, second))


def test_body_rejects_two_samples_without_mutation(session):
    _, curve, first, _ = assembly(session)
    before = session.document
    with pytest.raises(ValueError, match="three longitudinal"):
        session.command("consumer.sampling", entity=first, curve=curve, samples=2)
    assert session.document == before
