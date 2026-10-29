from dataclasses import replace
from threading import Event
from time import monotonic, sleep

from anthroforge.application.editing_contexts import bare
from anthroforge.application.storage import decode_document, document_state
from anthroforge.core.jobs import Job
from anthroforge.core.reconstruction import Reconstruction, SceneSnapshot, Variant


def test_normal_edits_and_undo_are_context_local(session):
    original = session.document
    session.contexts.add("alternative", original)
    with session.contexts.use("alternative"):
        session.begin()
        session.replace_document(name="Alternative")
        session.commit()
        assert session.document.name == "Alternative"
        session.navigate(-1)
        assert session.document.name == original.name
        session.navigate(1)
        assert session.document.name == "Alternative"
    assert session.document is original
    assert session.history.cursor == 0


def deferred(session, gate, published):
    def compute(document, cancel):
        assert gate.wait(2)
        return document.name

    def publish(value):
        published.append((session._editing.key, value))
        session.replace_document(name=value + " done")

    return Job("Context result", frozenset(("same-owner",)), lambda d: d, compute, publish)


def dispatched(scheduler, *jobs):
    deadline = monotonic() + 1
    while not all(job.future for job in jobs):
        scheduler.tick()
        assert monotonic() < deadline
        sleep(0.002)


def test_concurrent_same_identity_jobs_publish_to_own_context(session):
    session.contexts.add("alternative", replace(session.document, name="Alternative"))
    gate, published = Event(), []
    accepted = deferred(session, gate, published)
    session.scheduler.submit(accepted)
    with session.contexts.use("alternative"):
        variant = deferred(session, gate, published)
        session.scheduler.submit(variant)
    dispatched(session.scheduler, accepted, variant)
    assert accepted.future is not None and variant.future is not None
    gate.set()
    session.scheduler.wait(3)
    assert sorted(published) == [("", "Fixture"), ("alternative", "Alternative")]
    assert session.document.name == "Fixture done"
    assert session.contexts.scene("alternative").name == "Alternative done"


def test_reconstruction_roundtrip_does_not_nest_projects(session):
    snapshot = SceneSnapshot(bare(session.document))
    variant = Variant("Alternative", (), (), snapshot.id, snapshot.id)
    project = replace(
        session.document,
        reconstruction=Reconstruction(
            variants=(variant,),
            snapshots=(snapshot,),
        ),
    )
    restored = decode_document(document_state(project))
    assert restored == project
    assert restored.reconstruction.snapshot(snapshot.id).reconstruction == Reconstruction()
