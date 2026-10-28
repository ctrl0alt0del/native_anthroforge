"""Disposable disk retention never changes source files or active temporary writes."""

import os

from anthroforge.native import disk_cache_budget as budget
from anthroforge.native import skin_weight_cache


def product(folder, name, size, timestamp):
    path = folder / (name + ".zip")
    path.write_bytes(b"x" * size)
    os.utime(path, (timestamp, timestamp))
    return path


def test_disk_eviction_uses_recent_access_and_respects_bytes_and_count(tmp_path, monkeypatch):
    monkeypatch.setattr(budget, "BUDGET", 100)
    monkeypatch.setattr(budget, "CAPACITY", 2)
    old = product(tmp_path, "old", 40, 1)
    recent = product(tmp_path, "recent", 40, 2)
    temporary = tmp_path / "active.tmp"
    temporary.write_bytes(b"untouched")
    with budget.transaction(tmp_path):
        assert budget.trim(tmp_path, 40)
    assert not old.exists() and recent.exists() and temporary.read_bytes() == b"untouched"


def test_disk_oversize_bypasses_without_evicting_useful_entries(tmp_path, monkeypatch):
    monkeypatch.setattr(budget, "BUDGET", 64)
    monkeypatch.setattr(skin_weight_cache, "directory", lambda: tmp_path / "cache")
    source = tmp_path / "source"
    source.mkdir()
    weights = source / "bbw_v1_5.bin"
    weights.write_bytes(b"weights" * 100)
    assert not skin_weight_cache.retain("new", str(source))
    assert weights.read_bytes() == b"weights" * 100
    assert not list(skin_weight_cache.directory().glob("*.zip"))


def test_missing_cache_touch_does_not_recreate_evicted_product(tmp_path):
    missing = tmp_path / "evicted.zip"
    budget.used(missing)
    assert not missing.exists()


def test_active_budget_writer_causes_safe_cache_bypass(tmp_path, monkeypatch):
    monkeypatch.setattr(skin_weight_cache, "directory", lambda: tmp_path / "cache")
    source = tmp_path / "source"
    source.mkdir()
    (source / "bbw_v1_5.bin").write_bytes(b"valid weights")
    with budget.transaction(skin_weight_cache.directory()):
        assert not skin_weight_cache.retain("contended", str(source))
    assert skin_weight_cache.retain("available", str(source))


def test_abandoned_cache_staging_is_removed_only_under_exclusive_lock(tmp_path):
    abandoned = tmp_path / "af-weights-interrupted.tmp"
    unrelated = tmp_path / "other.tmp"
    abandoned.write_bytes(b"interrupted archive")
    unrelated.write_bytes(b"leave alone")
    with budget.transaction(tmp_path):
        assert not abandoned.exists() and unrelated.exists()
