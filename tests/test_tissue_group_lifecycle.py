"""Group reservations, dispatch snapshots and historical results use the shared lifecycle."""

from threading import Event

from anthroforge.application import tissue_group_evaluation, tissue_group_tasks
from tests.test_tissue_stack_groups import envelopes
from tests.test_tissue_stack_workflow import current


def pause_group(monkeypatch):
    original, gate, started = tissue_group_evaluation.evaluate, Event(), Event()

    def blocked(*args, **kwargs):
        started.set()
        assert gate.wait(5)
        return original(*args, **kwargs)

    monkeypatch.setattr(tissue_group_evaluation, "evaluate", blocked)
    return gate, started


def dispatch(session, target):
    key = tissue_group_tasks.request(session, target, False)
    job = session.scheduler.registry.by_id[key]
    job.ready_at = 0
    session.scheduler.tick()
    return job


def test_edit_supersedes_running_group_and_undo_redo_restores_complete_results(
    session, monkeypatch
):
    first, second = envelopes(session)
    gate, started = pause_group(monkeypatch)
    try:
        obsolete = dispatch(session, first)
        assert started.wait(2)
        session.command("tissue.inflation", target=second, side="b", changes=dict(amount=0.035))
    finally:
        gate.set()
    session.wait(30)
    assert obsolete.outputs == {first, second} and obsolete.state == "obsolete"
    assert not session.scheduler.blocked
    verify_navigation(session, first, second)


def verify_navigation(session, first, second):
    low = current(session, first)[:, 2].min()
    current(session, second)
    session.command("undo")
    session.wait(30)
    assert current(session, first)[:, 2].min() > low + 0.001
    session.command("redo")
    session.wait(30)
    assert abs(current(session, first)[:, 2].min() - low) < 1e-8
    current(session, second)
