"""Shared painting operations preserve anatomy until one qualified stroke commit."""

import pytest

from tests.test_tissue_painting_native import VIEW
from tests.test_tissue_workflow import assembly


def setup(session, domain="REST"):
    _, _, key = assembly(session)
    session.command("tissue.field.create", target=key, name="paint", domain=domain)
    session.wait()
    return key


def request(session, key, **options):
    arguments = dict(
        target=key,
        name="paint",
        stage="final",
        view=VIEW,
        samples=[[0, 0]],
        brush=[1000, 1, 1, 1, False],
    )
    result = session.command("tissue.inspect.paint", **dict(arguments, **options))
    session.wait()
    state = session.command("tissue.inspect.status", kind="paint")
    assert state["state"] == "ready", state
    return result["job"]


@pytest.mark.parametrize("domain", ["BASE", "REST"])
def test_stroke_preview_is_readonly_and_commit_is_one_undo(session, domain):
    key = setup(session, domain)
    before, count = session.document, len(session.history.entries)
    job = request(session, key)
    assert session.document is before and len(session.history.entries) == count
    session.command("tissue.field.paint.commit", job=job)
    session.wait()
    assert any(session.document.object(key).fields[0].values)
    assert len(session.history.entries) == count + 1
    session.command("undo")
    session.wait()
    assert session.document.object(key).fields == before.object(key).fields


def test_changed_input_rejects_old_stroke_and_preserves_new_field(session):
    key = setup(session)
    job, field = request(session, key), session.document.object(key).fields[0]
    session.command(
        "tissue.field.assign",
        target=key,
        name="paint",
        indices=[0],
        value=0.3,
        topology=field.topology,
    )
    session.wait()
    with pytest.raises(ValueError, match="inputs changed"):
        session.command("tissue.field.paint.commit", job=job)
    assert session.document.object(key).fields[0].values[0] == 0.3


def test_cancelled_stroke_cannot_be_committed(session):
    key = setup(session)
    job = request(session, key)
    session.command("tissue.inspect.cancel", kind="paint")
    with pytest.raises(ValueError, match="incomplete"):
        session.command("tissue.field.paint.commit", job=job)
    assert not any(session.document.object(key).fields[0].values)


def test_repeated_strokes_share_bounded_projection_cache(session):
    key = setup(session)
    request(session, key)
    cached = session.engine.paint_surfaces.retained()
    request(session, key, samples=[[10, 0]])
    assert session.engine.paint_surfaces.retained() == cached
    assert session.engine.paint_surfaces.bytes <= session.engine.paint_surfaces.budget
