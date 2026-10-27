"""Complete build publishes usable intermediates and protects accepted replacements."""

from anthroforge.application import (
    skin_evaluation,
    skin_reference_evaluation,
    skin_topology_evaluation,
)
from anthroforge.application.skin_results import ComputedStage
from tests.test_skin_reference import build, fail_proxy, topology


def stages(session, monkeypatch):
    topology(session)
    skin = session.document.skin
    result = ComputedStage(
        session.assets[skin.topology.asset].mesh, session.resources.skin[skin.topology.data]
    )
    monkeypatch.setattr(skin_evaluation, "evaluate", lambda *args: result)
    monkeypatch.setattr(skin_topology_evaluation, "evaluate", lambda *args: result)


def failed_build(session):
    key = session.command("skin.build")
    session.wait()
    job = session.scheduler.registry.by_id[key]
    assert job.state == "failed" and "proxy failure" in job.error
    return session.document.skin


def test_first_reference_failure_retains_topology_for_retry(session, monkeypatch):
    stages(session, monkeypatch)
    with monkeypatch.context() as patch:
        patch.setattr(skin_reference_evaluation, "proxy", fail_proxy)
        partial = failed_build(session)
    assert partial.envelope.asset and partial.topology.asset and not partial.reference
    assert partial.build_error and not partial.pending_topology.asset
    complete = build(session)
    assert complete.envelope == partial.envelope and complete.topology == partial.topology
    assert complete.reference and not complete.build_error


def test_failed_replacement_retains_old_skin_and_new_topology_for_retry(session, monkeypatch):
    stages(session, monkeypatch)
    previous = build(session)
    with monkeypatch.context() as patch:
        patch.setattr(skin_reference_evaluation, "proxy", fail_proxy)
        partial = failed_build(session)
    assert partial.reference == previous.reference and partial.final == previous.final
    assert partial.topology == previous.topology and partial.pending_topology.asset
    complete = build(session)
    assert complete.topology == partial.pending_topology
    assert not complete.pending_topology.asset and not complete.build_error


def test_complete_build_initializes_reference_in_one_undo(session, monkeypatch):
    stages(session, monkeypatch)
    before = session.document.skin
    key = session.command("skin.build")
    session.wait()
    assert session.scheduler.registry.by_id[key].state == "succeeded"
    complete = session.document.skin
    assert complete.reference and complete.final.asset
    session.command("undo")
    assert session.document.skin == before
    session.command("redo")
    session.wait()
    assert session.document.skin == complete
