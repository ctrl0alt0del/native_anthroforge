"""Persistent FAST products are disposable and never change the solver output."""

import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import numpy as np
import pytest

from anthroforge.core.skin import DeformationSettings
from anthroforge.native import skin_deformation, skin_weight_cache
from tests.test_skin_deformation import FIXTURE


def prepare(session):
    return skin_deformation.Preparation(
        session.engine, FIXTURE["arrays"], DeformationSettings(method="FAST", fast_handles=5)
    )


def test_cache_survives_preparation_and_checksum_failure_recomputes(session, tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    with prepare(session) as first:
        assert first.cache_status == "miss"
        expected = first.solve(FIXTURE["targets"]["identity"])[0]
    with prepare(session) as second:
        assert second.cache_status == "hit"
        np.testing.assert_array_equal(second.solve(FIXTURE["targets"]["identity"])[0], expected)
    corrupt_product(next(skin_weight_cache.directory().glob("*.zip")))
    with prepare(session) as third:
        assert third.cache_status == "unavailable"
        np.testing.assert_array_equal(third.solve(FIXTURE["targets"]["identity"])[0], expected)
    with prepare(session) as restored:
        assert restored.cache_status == "hit"


def corrupt_product(path):
    with ZipFile(path) as source:
        info = json.loads(source.read("manifest.json"))
        content = source.read(info["name"])
    with ZipFile(path, "w") as output:
        output.writestr("manifest.json", json.dumps(info))
        output.writestr(info["name"], b"wrong" + content[5:])


def test_unavailable_cache_does_not_prevent_computation(session, tmp_path, monkeypatch):
    directory = tmp_path / "blocked"
    directory.write_text("not a directory")
    monkeypatch.setattr(skin_weight_cache, "directory", lambda: directory)
    with prepare(session) as solver:
        result, _, _ = solver.solve(FIXTURE["targets"]["identity"])
        np.testing.assert_allclose(result, FIXTURE["arrays"]["vertices"], atol=1e-9)
    assert directory.read_text() == "not a directory"


def test_new_process_reuses_weights_with_identical_results(tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    results = []
    for name in ("cold", "warm"):
        destination = tmp_path / (name + ".json")
        process = subprocess.run(
            [sys.executable, "-m", "tools.check_skin_weight_cache", str(destination)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert process.returncode == 0, process.stderr
        results.append(json.loads(destination.read_text()))
    assert [row["cache"] for row in results] == ["miss", "hit"]
    assert results[0]["sha256"] == results[1]["sha256"]


def test_atomic_products_and_reference_keys_are_isolated(session, tmp_path, monkeypatch):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    arrays = skin_deformation.inputs(FIXTURE["arrays"])
    key = skin_weight_cache.key(arrays, 5)
    assert skin_weight_cache.key(arrays, 6) != key
    changed = list(arrays)
    changed[2] = changed[2] + 0.001
    assert skin_weight_cache.key(tuple(changed), 5) != key
    with prepare(session) as solver:
        assert solver.cache_status == "miss"
    with TemporaryDirectory() as folder:
        assert skin_weight_cache.restore(key, folder) == "hit"
        assert len(list(Path(folder).glob("bbw_v1_*.bin"))) == 1
    assert not list(skin_weight_cache.directory().glob("*.tmp"))


@pytest.mark.parametrize("content", ["[]", '{"name":23,"format":"bad"}', "{broken"])
def test_invalid_metadata_falls_back_to_computation(tmp_path, monkeypatch, content):
    monkeypatch.setattr(skin_weight_cache, "directory", lambda: tmp_path)
    with ZipFile(tmp_path / "bad.zip", "w") as archive:
        archive.writestr("manifest.json", content)
    with TemporaryDirectory() as folder:
        assert skin_weight_cache.restore("bad", folder) == "unavailable"
