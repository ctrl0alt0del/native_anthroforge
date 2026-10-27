"""Deformation reference lifecycle, source ownership and reload without recomputation."""

import json
from dataclasses import replace

import numpy as np

from anthroforge.application import skin_assets, skin_reference_evaluation, storage
from anthroforge.core.skin import SkinStage
from tests.conftest import CUBE


def topology(session):
    key = session.command("import", path=str(CUBE), units=1)["entity_id"]
    session.wait()
    mesh = session.document.entity(key).result.asset
    data = skin_assets.create({}, {})
    session.resources.skin[data.digest] = data
    skin = session.document.skin
    settings = replace(skin.deformation_settings, proxy_resolution=8)
    stage = SkinStage(asset=mesh, data=data.digest)
    session.replace_document(skin=replace(skin, topology=stage, deformation_settings=settings))
    return key


def build(session):
    key = session.command("skin.reference.build")
    session.wait()
    job = session.scheduler.registry.by_id[key]
    assert job.state == "succeeded", job.error
    return session.document.skin


def test_real_proxy_reference_identity_and_persistence(session, tmp_path):
    topology(session)
    skin = build(session)
    reference = session.resources.skin[skin.reference]
    assert json.loads(reference.metadata)["tissue_surface"] == "FINISHED"
    assert reference.arrays["embedding_ids"].shape == (8, 4)
    before = session.assets[skin.topology.asset].mesh.array(0)
    np.testing.assert_array_equal(session.assets[skin.final.asset].mesh.array(0), before)
    path = tmp_path / "reference.anthroforge"
    storage.atomic_save(path, session.document, session.resources)
    document, resources = storage.read_package(path, session.engine)
    assert document.skin == skin and resources.skin[skin.reference].digest == skin.reference
    assert set(skin.reference_sources) <= resources.meshes.keys()


def test_reference_undo_redo_and_preference_retention(session):
    topology(session)
    before = session.document.skin
    skin = build(session)
    session.command("preferences.set", skin_tissue_surface="INFLATED_REST")
    assert session.document.skin == skin
    session.command("undo")
    assert session.document.skin == before
    session.command("redo")
    session.wait()
    assert session.document.skin == skin


def fail_proxy(*args):
    raise ValueError("fixture proxy failure")


def test_reference_replacement_failure_keeps_accepted_output(session, monkeypatch):
    topology(session)
    skin = build(session)
    monkeypatch.setattr(skin_reference_evaluation, "proxy", fail_proxy)
    key = session.command("skin.reference.build")
    session.wait()
    assert session.scheduler.registry.by_id[key].state == "failed"
    assert session.document.skin == skin
    assert skin.reference in session.resources.skin


def test_missing_topology_blocks_reference_preparation(session):
    key = session.command("skin.reference.build")
    session.wait()
    assert session.scheduler.registry.by_id[key].state == "failed"
    assert not session.document.skin.reference
