"""Editing source lists owns references without deleting or rewriting source curves."""

import pytest

from tests.test_surface_workflow import curve, surface, vertices


def test_add_remove_preserve_source_settings_and_form_one_undo(session):
    a, b, c = [curve(session, y) for y in (0, 0.4, 0.8)]
    target = surface(session, [a, b])
    session.command("surface.source", target=target, curve=b, reverse=True, samples=13)
    session.wait()
    before, cursor = session.document.object(target), session.history.cursor
    session.command("surface.source.add", target=target, curve=c, index=1)
    session.wait()
    assert session.document.object(target).curves[-1] == before.curves[-1]
    assert session.history.cursor == cursor + 1 and len(vertices(session, target))
    session.command("surface.source.remove", target=target, curve=c)
    session.wait()
    assert c in session.document.registry.records
    assert session.document.object(target).curves == before.curves


def test_source_list_validation_is_shared_and_preserves_state_on_failure(session):
    a, b = curve(session), curve(session, 0.4)
    target = surface(session, [a, b])
    before = session.document
    with pytest.raises(ValueError, match="same curve"):
        session.command("surface.source.add", target=target, curve=a)
    with pytest.raises(ValueError, match="compatible source"):
        session.command("surface.source.remove", target=target, curve=a)
    assert session.document == before


def test_closed_add_retains_existing_correspondence_until_explicit_realign(session):
    a, b, c = [curve(session, y, closed=True) for y in (0, 0.4, 0.8)]
    target = surface(session, [a, b])
    before = session.document.object(target).alignment
    session.command("surface.source.add", target=target, curve=c)
    session.wait()
    assert session.document.object(target).alignment[:2] == before
    assert len(vertices(session, target))


def test_patch_source_replacement_preserves_both_independent_curves(session):
    a, b = curve(session, closed=True), curve(session, 0.4, closed=True)
    target = surface(session, [a], kind="PATCH")
    session.command("surface.sources", target=target, curves=[b])
    session.wait()
    assert session.document.object(target).curves[0].curve == b
    assert {a, b} <= session.document.registry.records.keys()
    assert len(vertices(session, target))
