"""Real desktop/headless command boundary for both complete topology pipelines."""

import json
import sys

import numpy as np
import pytest

from anthroforge.application import storage
from tests.test_skin_jobs import imported

pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Pinned QuadWild is Windows-only")


def configure(session, backend, symmetry):
    session.command(
        "skin.configure", section="deformation_settings", values={"proxy_resolution": 8}
    )
    session.command(
        "skin.configure",
        section="topology_settings",
        values=dict(backend=backend, symmetry=symmetry, target_quads=1000),
    )


def build(session, command="skin.build"):
    key = session.command(command)
    session.wait()
    job = session.scheduler.registry.by_id[key]
    assert job.state == "succeeded", job.error
    stage = session.document.skin.topology
    mesh = session.assets[stage.asset].mesh
    assert mesh.counts[1] > 0 and np.all(np.diff(mesh.array(2)) == 4)
    return stage, json.loads(session.resources.skin[stage.data].metadata)


@pytest.mark.parametrize("backend", ["INSTANT", "QUADWILD"])
@pytest.mark.parametrize("symmetry", ["NONE", "X"])
def test_combined_topology_build_has_owned_quads_and_coherent_undo(
    session, monkeypatch, backend, symmetry
):
    imported(session, monkeypatch)
    configure(session, backend, symmetry)
    stage, report = build(session)
    envelope = session.document.skin.envelope
    assert report["settings"]["backend"] == backend and report["attempts"]
    assert envelope.asset and report["requested_quads"] == 1000
    session.command("undo")
    assert not session.document.skin.topology.asset and not session.document.skin.envelope.asset
    session.command("redo")
    session.wait()
    assert session.document.skin.topology == stage and session.document.skin.envelope == envelope


def test_topology_roundtrip_and_individual_rebuild_preserves_envelope(
    session, monkeypatch, tmp_path
):
    imported(session, monkeypatch)
    configure(session, "INSTANT", "NONE")
    stage, _ = build(session)
    envelope = session.document.skin.envelope
    newer, _ = build(session, "skin.topology.build")
    assert newer.revision == stage.revision + 1 and session.document.skin.envelope == envelope
    path = tmp_path / "quad-skin.anthroforge"
    session.command("save", path=str(path), blocked_policy="wait")
    session.wait()
    document, resources = storage.read_package(path, session.engine)
    assert document.skin == session.document.skin
    assert resources.skin[newer.data].digest == newer.data


def test_missing_envelope_fails_without_publishing_partial_topology(session):
    with pytest.raises(ValueError, match="envelope"):
        session.command("skin.topology.build")
    assert not session.document.skin.topology.asset
