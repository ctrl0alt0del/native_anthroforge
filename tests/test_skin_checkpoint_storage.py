"""Checkpoint ownership and extension-selected portable archives survive atomic save."""

import hashlib
import json
from dataclasses import replace
from zipfile import ZipFile

import pytest

from anthroforge.application import skin_assets, skin_checkpoint_assets, storage
from anthroforge.core.skin_checkpoints import Checkpoint, matching


def checkpoint(session, *, durable=True):
    data = skin_checkpoint_assets.create(
        {"warm/velocity.bin": b"1234"}, dict(material="local-stvk-v1")
    )
    prefix = hashlib.sha256(b"prefix").hexdigest()
    row = Checkpoint("AVBD", 3, "SCP", "bone", prefix, data.digest, durable)
    session.resources.skin[data.digest] = data
    session.replace_document(skin=replace(session.document.skin, checkpoints=(row,)))
    return row


@pytest.mark.parametrize("extension,retained", [("anthroforge", False), ("anthroforgex", True)])
def test_atomic_save_uses_final_extension_and_preserves_live_resources(
    session, tmp_path, extension, retained
):
    row = checkpoint(session)
    path = tmp_path / ("checkpoint." + extension)
    storage.atomic_save(path, session.document, session.resources)
    document, resources = storage.read_package(path, session.engine)
    assert bool(document.skin.checkpoints) == retained
    assert (row.resource in resources.skin) == retained
    assert session.document.skin.checkpoints == (row,)
    with ZipFile(path) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        assert (row.resource in manifest["skin_assets"]) == retained


def test_extended_archive_omits_transient_retry_checkpoint(session, tmp_path):
    checkpoint(session, durable=False)
    path = tmp_path / "transient.anthroforgex"
    storage.atomic_save(path, session.document, session.resources)
    document, _ = storage.read_package(path, session.engine)
    assert document.skin.checkpoints == ()


def test_restored_checkpoint_has_owned_bytes_and_relative_paths(session, tmp_path):
    row = checkpoint(session)
    asset = session.resources.skin[row.resource]
    state = skin_checkpoint_assets.restore(asset, tmp_path / "restored")
    assert state["material"] == "local-stvk-v1"
    assert (tmp_path / "restored/warm/velocity.bin").read_bytes() == b"1234"
    with pytest.raises(ValueError, match="inside"):
        skin_checkpoint_assets.create({"../outside.bin": b"bad"}, {})


def test_invalid_inner_checksum_is_rejected_on_open(session, tmp_path):
    row = checkpoint(session)
    asset = session.resources.skin[row.resource]
    info = json.loads(asset.metadata)
    info["files"]["warm/velocity.bin"]["checksum"] = "0" * 64
    corrupt = skin_assets.create(dict(asset.arrays), info)
    session.resources.skin[corrupt.digest] = corrupt
    skin = replace(session.document.skin, checkpoints=(replace(row, resource=corrupt.digest),))
    path = tmp_path / "corrupt.anthroforgex"
    storage.atomic_save(path, replace(session.document, skin=skin), session.resources)
    with pytest.raises(ValueError, match="checksum"):
        storage.read_package(path, session.engine)


def test_only_complete_matching_prefix_can_be_reused(session):
    row = checkpoint(session)
    other = replace(row, source="next", prefix=hashlib.sha256(b"next").hexdigest())
    assert matching((other, row), (row.prefix, other.prefix), "AVBD", 3) == (row, other)
    assert matching((other,), (row.prefix, other.prefix), "AVBD", 3) == ()
    assert matching((row,), (row.prefix,), "AVBD", 4) == ()
