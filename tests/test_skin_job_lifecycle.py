"""All skin stage outputs share one versioned, cancellable authored publication."""

import json
from dataclasses import replace
from threading import Event

from anthroforge.application import skin_assets, skin_stages
from anthroforge.application.skin_results import ComputedStage
from tests.test_skin_jobs import imported


def prepare(session, monkeypatch):
    imported(session, monkeypatch)
    source = next(iter(session.assets.values())).mesh
    entered, release = Event(), Event()

    def compute(engine, document, resources, cancel):
        entered.set()
        assert release.wait(5)
        data = skin_assets.create({}, dict(target=document.skin.topology_settings.target_quads))
        output = ComputedStage(source, data)
        return dict(envelope=output, topology=output)

    policy = replace(skin_stages.POLICIES["construction"], compute=compute)
    monkeypatch.setitem(skin_stages.POLICIES, "construction", policy)
    return entered, release


def start(session, entered):
    key = session.command("skin.build")
    session.scheduler.tick()
    assert entered.wait(5)
    return key


def accepted_target(session):
    skin = session.document.skin
    assert skin.envelope.inputs == skin.topology.inputs
    session.resources.require(session.document)
    return json.loads(session.resources.skin[skin.topology.data].metadata)["target"]


def test_superseded_skin_job_and_history_use_their_own_captured_settings(session, monkeypatch):
    entered, release = prepare(session, monkeypatch)
    start(session, entered)
    try:
        session.command(
            "skin.configure", section="topology_settings", values=dict(target_quads=1500)
        )
        assert not session.document.skin.topology.asset
    finally:
        release.set()
    session.wait()
    assert accepted_target(session) == 1500
    session.command("undo")
    session.wait()
    assert accepted_target(session) == 8100


def test_cancellation_and_undo_do_not_publish_half_a_skin_build(session, monkeypatch):
    entered, release = prepare(session, monkeypatch)
    key = start(session, entered)
    try:
        session.command("job.cancel", job_id=key)
    finally:
        release.set()
    session.wait()
    assert not session.document.skin.envelope.asset and not session.document.skin.topology.asset
    assert session.scheduler.registry.by_id[key].state == "cancelled"
    session.command("undo")
    session.command("redo")
    session.wait()
    assert accepted_target(session) == 8100


def test_undo_during_skin_build_requires_explicit_redo_to_restart(session, monkeypatch):
    entered, release = prepare(session, monkeypatch)
    start(session, entered)
    try:
        session.command("undo")
    finally:
        release.set()
    session.wait()
    assert not session.document.skin.envelope.asset and not session.document.skin.topology.asset
    session.command("redo")
    session.wait()
    assert accepted_target(session) == 8100
