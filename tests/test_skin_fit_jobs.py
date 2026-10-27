"""Fitted results use the common job/undo/persistence lifecycle without editing anatomy."""

from anthroforge.application import storage
from tests.test_skin_fit_capture import setup


def fit(session, identity):
    job = session.command(
        "skin.fit", shortcut=identity, settings=dict(minimum=0, maximum=0.2, bones=1, samples=5)
    )
    session.wait()
    assert session.scheduler.registry.by_id[job].state == "succeeded", (
        session.scheduler.registry.by_id[job].error
    )
    return session.document.skin.fits[-1]


def test_fit_publication_undo_and_reload_preserve_source(session, tmp_path):
    identity = setup(session)
    before = session.document
    result = fit(session, identity)
    assert (
        session.document.entities == before.entities
        and session.document.skin.final == before.skin.final
    )
    path = tmp_path / "fitted.anthroforge"
    roundtrip(session, path, result)
    session.command("undo")
    assert not session.document.skin.fits
    session.command("redo")
    session.wait()
    assert session.document.skin.fits == (result,)


def roundtrip(session, path, result):
    storage.atomic_save(path, session.document, session.resources)
    restored, resources = storage.read_package(path, session.engine)
    assert restored.skin.fits == (result,) and result.reference in resources.meshes
    assert result.data in resources.skin
