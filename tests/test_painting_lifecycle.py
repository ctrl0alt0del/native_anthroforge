"""Publication safety, exact reuse and bounded lifetime across clients/contexts."""

from dataclasses import replace
from threading import Event
from weakref import ref

import pytest

from anthroforge.application import painting_consumers as consumers
from anthroforge.application import painting_jobs
from anthroforge.application.painting_state import presented
from tests.test_editing_contexts import dispatched
from tests.test_painting_system import append, begin
from tests.test_painting_system import painting_case as painting_case


def replace_compute(monkeypatch, compute):
    original = consumers.consumer
    monkeypatch.setattr(
        consumers, "consumer", lambda kind: replace(original(kind), compute=compute)
    )
    monkeypatch.setattr(painting_jobs, "consumer", consumers.consumer)


def test_finish_reuses_exact_ready_candidate(session, painting_case, monkeypatch):
    token = begin(session, painting_case)
    append(session, token)
    session.wait()

    def forbidden(*args):
        raise AssertionError("An exact ready stroke must not be computed again")

    replace_compute(monkeypatch, forbidden)
    session.command("painting.finish", token=token)
    session.wait()
    assert session.command("painting.status", token=token)["state"] == "committed"


def test_replacement_retains_previous_colors_and_releases_resource(session, painting_case):
    token = begin(session, painting_case)
    append(session, token)
    session.wait()
    first = presented(session, painting_case["consumer"])
    owner = ref(first["resource"])
    append(session, token, 20)
    assert presented(session, painting_case["consumer"]) is first
    session.wait()
    assert presented(session, painting_case["consumer"]) is not first
    del first
    assert owner() is None
    session.command("painting.cancel", token=token)
    assert presented(session, painting_case["consumer"]) is None


def test_explicit_commit_cannot_join_another_gesture(session, painting_case):
    token = session.command("painting.preview", **painting_case, samples=[[0, 0]])["token"]
    session.wait()
    session.begin()
    before = session.document
    with pytest.raises(ValueError, match="gesture"):
        session.command("painting.commit", token=token)
    assert session.document is before and session.history.before is before
    session.cancel()


def delayed_compute(original, gate):
    def delayed(*args):
        assert gate.wait(3)
        return original(*args)

    return delayed


def test_legacy_commit_cannot_join_another_gesture(session, painting_case):
    state = session.command("painting.preview", **painting_case, samples=[[0, 0]])
    session.wait()
    session.begin()
    before = session.document
    prefix = "skin.collagen" if painting_case["consumer"] == "collagen" else "tissue.field"
    with pytest.raises(ValueError, match="gesture"):
        session.command(prefix + ".paint.commit", job=state["job"])
    assert session.document is before and session.history.before is before
    session.cancel()


def test_cancellation_during_native_work_cannot_publish(session, painting_case, monkeypatch):
    gate = Event()
    original = consumers.consumer(painting_case["consumer"]).compute
    replace_compute(monkeypatch, delayed_compute(original, gate))
    token, before = begin(session, painting_case), session.document
    append(session, token)
    job = session.scheduler.registry.by_id[session.command("painting.status", token=token)["job"]]
    dispatched(session.scheduler, job)
    session.command("painting.cancel", token=token)
    gate.set()
    session.wait()
    assert session.document is before and not session.painting.active


def failed_compute(*args):
    raise ValueError("Injected painting failure")


def test_failure_retains_values_and_allows_next_stroke(session, painting_case, monkeypatch):
    replace_compute(monkeypatch, failed_compute)
    before = session.document
    token = begin(session, painting_case)
    append(session, token)
    session.command("painting.finish", token=token)
    session.wait()
    state = session.command("painting.status", token=token)
    assert state["state"] == "failed" and "Injected" in state["error"]
    assert session.document is before
    assert begin(session, painting_case) != token


def test_context_strokes_do_not_cross_publish(session, painting_case):
    original = session.document
    session.contexts.add("alternative", original)
    with session.contexts.use("alternative"):
        token = begin(session, painting_case)
        append(session, token)
        session.command("painting.finish", token=token)
    session.wait()
    assert session.document is original
    with session.contexts.use("alternative"):
        assert session.command("painting.status", token=token)["state"] == "committed"
        assert session.history.cursor == 1


def test_undo_cancels_uncommitted_work(session, painting_case):
    token = begin(session, painting_case)
    append(session, token)
    session.command("painting.finish", token=token)
    session.command("undo")
    after = session.document
    session.wait()
    assert session.document is after and not session.painting.active


def test_geometry_changes_hide_old_preview(session, painting_case):
    token = begin(session, painting_case)
    append(session, token)
    session.wait()
    assert presented(session, painting_case["consumer"])
    session.command(
        "scp.empty", name="Changed scene membership", parent=session.document.entities[0].id
    )
    assert presented(session, painting_case["consumer"]) is None
    assert session.command("painting.status", token=token)["state"] == "stale"
