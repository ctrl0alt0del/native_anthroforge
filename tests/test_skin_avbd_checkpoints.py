"""Ordered content prefixes and failed-worker resources survive real job publication."""

import json
import shutil
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from anthroforge.application import skin_avbd_capture, skin_evaluation
from anthroforge.application import skin_avbd_checkpoints as checkpoints
from anthroforge.application import skin_avbd_identity as identity
from anthroforge.application import skin_checkpoint_assets as assets
from anthroforge.application.skin_draft_build import CheckpointFailure, DraftOutput
from anthroforge.avbd_runtime.tissues import surface_files
from anthroforge.core.skin_checkpoints import Checkpoint
from tests.test_skin_jobs import imported


def captures(folder, bones=("a", "b"), tissues=("c", "d")):
    folder.mkdir()
    mesh = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=float), np.array([[0, 1, 2]]), 0
    skin_avbd_capture.write_meshes(folder / "bones.bin", [mesh for _ in bones])
    np.array([0, 0, 0, 1], dtype="<f8").tofile(folder / "frame.bin")
    rows = [dict(id=v, name=f"bone-{i}", mesh_index=i) for i, v in enumerate(bones)]
    muscles = [dict(id=v, name=f"tissue-{i}", assets=f"tissue-{i}") for i, v in enumerate(tissues)]
    for row in muscles:
        (folder / row["assets"]).mkdir()
        for name in ("base", "muscle"):
            skin_avbd_capture.write_meshes(folder / row["assets"] / (name + ".bin"), [mesh])
    (folder / "recipe.json").write_text(json.dumps(dict(bones=rows, muscles=muscles)))
    return identity.prefixes(folder, "runtime")


def bundle(kind, source, prefix, durable=True):
    asset = assets.create({"warm.bin": b"accepted"}, dict(kind=kind))
    return assets.Bundle(Checkpoint("AVBD", 3, kind, source, prefix, asset.digest, durable), asset)


def test_early_geometry_change_invalidates_the_whole_later_prefix(tmp_path):
    folder = tmp_path / "inputs"
    before = captures(folder)
    values = bytearray((folder / "bones.bin").read_bytes())
    values[20:28] = np.array([0.5], dtype="<f8").tobytes()
    (folder / "bones.bin").write_bytes(values)
    after = identity.prefixes(folder, "runtime")
    assert all(
        a != b for a, b in zip((*before[0], *before[1]), (*after[0], *after[1]), strict=True)
    )
    assert identity.prefixes(folder, "changed-runtime")[0][0] != after[0][0]


def test_appended_vcp_reuses_combined_prefix_but_earlier_edit_replays_skeleton(tmp_path):
    old = captures(tmp_path / "old", tissues=("c",))
    new = captures(tmp_path / "new")
    record = bundle("VCP", "c", old[1][-1]).checkpoint
    assert old[0] == new[0] and old[1] == new[1][:1]
    assert checkpoints.latest_tissue((record,), new[1]) == record
    changed = captures(tmp_path / "changed", tissues=("different", "d"))
    assert checkpoints.latest_tissue((record,), changed[1]) is None


def test_prepare_restores_only_last_complete_scp_and_combined_vcp(tmp_path, monkeypatch):
    folder = tmp_path / "inputs"
    bones, tissues = captures(folder)
    bundles = [bundle("SCP", key, p) for key, p in zip(("a", "b"), bones, strict=True)]
    bundles.append(bundle("VCP", "d", tissues[-1]))
    monkeypatch.setattr(identity, "runtime", lambda root: "runtime")
    skin = SimpleNamespace(checkpoints=tuple(b.checkpoint for b in bundles))
    resources = SimpleNamespace(skin={b.asset.digest: b.asset for b in bundles})
    request = SimpleNamespace(document=SimpleNamespace(skin=skin), resources=resources)
    _, kept = checkpoints.prepare(folder, request, tmp_path)
    assert len(kept) == 3
    assert {p.name for p in folder.glob("resume-*")} == {"resume-SCP", "resume-VCP"}


def test_failed_append_keeps_prior_durable_and_latest_transient_vcp():
    previous = bundle("VCP", "c", "a" * 64)
    transient = bundle("VCP", "d", "b" * 64, False)
    assert checkpoints.tissue_retention([previous, transient], False) == (previous, transient)
    successful = checkpoints.tissue_retention([previous, transient], True)
    assert len(successful) == 1 and successful[0].checkpoint.durable


def failed_stage(checkpoint):
    def build(request):
        raise CheckpointFailure(ValueError("later stage failed"), (checkpoint,))

    return build


def install_builder(monkeypatch, build):
    monkeypatch.setitem(
        skin_evaluation.BUILDERS, "AVBD", replace(skin_evaluation.BUILDERS["AVBD"], build=build)
    )


def test_partial_checkpoint_publishes_without_promoting_builder_or_replacing_draft(
    session, monkeypatch
):
    owner = imported(session, monkeypatch)
    before = session.document.skin
    accepted = bundle("SCP", owner, "a" * 64)
    install_builder(monkeypatch, failed_stage(accepted))
    session.command("skin.configure", section="draft_settings", values=dict(backend="AVBD"))
    session.wait()
    skin = session.document.skin
    assert skin.envelope == before.envelope and skin.applied_draft == before.applied_draft
    assert skin.checkpoints == (accepted.checkpoint,)
    assert accepted.asset.digest in session.resources.skin
    session.command("undo")
    assert session.document.skin.checkpoints == before.checkpoints


def successful_stage(request):
    checkpoint = bundle("SCP", request.capture.sources[0].identity.owner, "a" * 64)
    return DraftOutput(request.capture.sources[0].mesh, {}, (checkpoint,))


def test_successful_checkpoint_is_retained_by_undo_redo_and_owned_resources(session, monkeypatch):
    imported(session, monkeypatch)
    install_builder(monkeypatch, successful_stage)
    session.command("skin.configure", section="draft_settings", values=dict(backend="AVBD"))
    session.wait()
    accepted = session.document.skin
    session.command("undo")
    assert not session.document.skin.checkpoints
    session.command("redo")
    session.wait()
    assert session.document.skin == accepted
    assert all(c.resource in session.resources.skin for c in accepted.checkpoints)


def test_checkpoint_receipt_cannot_escape_owned_worker_directory(tmp_path):
    with pytest.raises(ValueError, match="inside"):
        checkpoints.owned_file(tmp_path, "../foreign.bin")


def regional_material(tmp_path):
    names = (
        "latest.bin",
        "faces.bin",
        "validated/latest.bin",
        "validated/faces.bin",
        "solve/relaxation/rest.bin",
        "regions/limb-labels.bin",
        "regions/limb-corners.bin",
    )
    for name in names:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"owned")
    return names


def test_vcp_checkpoint_retains_regional_material_and_rejects_partial_state(tmp_path):
    names = regional_material(tmp_path)
    assert set(surface_files(tmp_path)) == {"skin/" + name for name in names}
    (tmp_path / "solve/relaxation/rest.bin").unlink()
    with pytest.raises(ValueError, match="material checkpoint"):
        surface_files(tmp_path)


def test_packaged_adapter_imports_without_top_level_source_package(tmp_path):
    source = Path(__file__).parents[1] / "src/anthroforge/avbd_runtime"
    target = tmp_path / "anthroforge/avbd_runtime"
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__"))
    result = subprocess.run(
        [sys.executable, "-I", str(target / "bootstrap.py"), "--help"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert result.returncode == 0, result.stderr
    assert "runtime" in result.stdout and "folder" in result.stdout


def test_runtime_environment_version_change_invalidates_checkpoint_identity(tmp_path):
    folder = tmp_path / ".venv/Lib/site-packages/numerical-1.dist-info"
    folder.mkdir(parents=True)
    metadata = folder / "METADATA"
    metadata.write_text("Version: 1")
    before = identity.runtime(tmp_path)
    metadata.write_text("Version: 20")
    assert identity.runtime(tmp_path) != before
