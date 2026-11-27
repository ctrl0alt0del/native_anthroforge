"""Capture stays on the owner; owned-input traversal and checks run in the worker."""

from functools import partial
from threading import get_ident

from anthroforge.application import inspection_context
from anthroforge.application.issues.providers import Provider


def recorded_provider(session, calls):
    def capture(document):
        calls.append(("capture", get_ident()))
        return inspection_context.capture(session)

    return Provider(
        "ownership",
        lambda _: {"document"},
        lambda *_: set(),
        lambda d, s: d.id,
        lambda *_: (),
        capture=capture,
        prepare=partial(prepare_recorded, calls),
    )


def prepare_recorded(calls, context):
    calls.append(("prepare", get_ident()))
    return inspection_context.prepare(context)


def test_inspection_preparation_runs_off_owner_thread(session):
    session.wait(5)
    owner, calls = get_ident(), []
    session.issues.listening.register(recorded_provider(session, calls))
    session.wait(5)
    assert calls[0] == ("capture", owner)
    assert calls[1][0] == "prepare" and calls[1][1] != owner
    assert session.command("issues.status")["clean"]


def test_capture_retains_catalogue_independently_of_live_mutations(session):
    captured = inspection_context.capture(session)
    assert captured.document is session.document
    assert captured.resources is not session.resources
    session.resources.evidence["later"] = b"new"
    assert "later" not in captured.resources.evidence
