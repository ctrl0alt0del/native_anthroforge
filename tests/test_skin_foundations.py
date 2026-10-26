"""Skin has independent document ownership and preserves previous project state."""

import json
from dataclasses import replace
from zipfile import ZipFile

import numpy as np
import pytest

from anthroforge.application import skin_assets, storage
from anthroforge.core.skin import (
    DeformationSettings,
    EnvelopeSettings,
    SkinContributor,
    effective_collagen,
)


def test_settings_use_shared_undo_and_reject_invalid_values(session):
    original = session.document
    session.command("skin.configure", section="envelope_settings", values={"gap_limit_ratio": 0.01})
    assert session.document.skin.envelope_settings.gap_limit_ratio == 0.01
    session.command("undo")
    assert session.document.skin == original.skin
    session.command("redo")
    assert session.document.skin.envelope_settings.gap_limit_ratio == 0.01
    before = session.document
    with pytest.raises(ValueError, match="finite"):
        session.command(
            "skin.configure", section="envelope_settings", values={"gap_strength": float("nan")}
        )
    assert session.document == before


def test_addon_defaults_and_validation_are_preserved():
    assert EnvelopeSettings().minimum_offset_ratio == 1.189424086064195 / 220
    assert effective_collagen(SkinContributor("a"), "Ear cartilage") == 0
    assert effective_collagen(SkinContributor("a"), "Femur") == 1
    assert (
        effective_collagen(SkinContributor("a", collagen_mode="UNIFORM", collagen=0.3), "Ear")
        == 0.3
    )
    assert DeformationSettings(fast_handles=1024).fast_handles == 1024
    with pytest.raises(ValueError):
        DeformationSettings(fast_handles=4)


def test_skin_asset_owns_immutable_data():
    values = np.arange(12.0).reshape(4, 3)
    metadata = {"kind": "fixture", "owners": ["a"]}
    asset = skin_assets.create({"vertices": values}, metadata)
    values[:] = 99
    metadata["owners"].append("b")
    assert asset.arrays["vertices"][0, 0] == 0
    assert json.loads(asset.metadata)["owners"] == ["a"]
    with pytest.raises(ValueError):
        asset.arrays["vertices"].flags.writeable = True
    with pytest.raises(ValueError):
        skin_assets.create({"bad": np.array([np.nan])}, {})


def test_skin_resource_roundtrip_and_checksum(session, tmp_path):
    asset = skin_assets.create({"samples": np.eye(3)}, {"kind": "fixture"})
    session.resources.skin[asset.digest] = asset
    session.replace_document(skin=replace(session.document.skin, reference=asset.digest))
    path = tmp_path / "skin.anthroforge"
    session.command("save", path=str(path), blocked_policy="wait")
    document, resources = storage.read_package(path, session.engine)
    assert document.skin == session.document.skin
    assert resources.skin[asset.digest].digest == asset.digest
    np.testing.assert_array_equal(resources.skin[asset.digest].arrays["samples"], np.eye(3))
    with ZipFile(path) as archive:
        assert json.loads(archive.read("manifest.json"))["version"] == 7


def legacy_copy(source, target, version):
    with ZipFile(source) as src, ZipFile(target, "w") as dst:
        for name in src.namelist():
            data = src.read(name)
            if name == "manifest.json":
                value = json.loads(data)
                value["version"] = version
                value["document"].pop("skin")
                value.pop("skin_assets")
                data = json.dumps(value).encode()
            dst.writestr(name, data)


@pytest.mark.parametrize("version", [4, 5, 6])
def test_previous_schema_keeps_geometry_and_empty_skin(session, assembly, tmp_path, version):
    root, _child = assembly
    saved, old = tmp_path / "new.anthroforge", tmp_path / "old.anthroforge"
    session.command("save", path=str(saved), blocked_policy="wait")
    original = session.document
    legacy_copy(saved, old, version)
    document, resources = storage.read_package(old, session.engine)
    assert document == original
    key = document.entity(root).result.asset
    np.testing.assert_array_equal(
        resources.meshes[key].mesh.array(0), session.assets[key].mesh.array(0)
    )
    assert not document.skin.final.asset and not document.skin.reference
