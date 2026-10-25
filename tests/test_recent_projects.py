"""Recent history persists only accepted file identities and never owns project files."""

import pytest

from anthroforge.application.recent_projects import LIMIT, RecentProjects


def test_history_persists_recency_deduplicates_and_bounds(tmp_path):
    store = RecentProjects(tmp_path / "recent.json")
    for index in range(LIMIT + 4):
        store.remember(tmp_path / f"{index}.anthroforge")
    target = tmp_path / "10.anthroforge"
    store.remember(target)
    reopened = RecentProjects(store.path)
    assert reopened.entries == store.entries and len(store.entries) == LIMIT
    assert store.entries[0] == str(target) and store.entries.count(str(target)) == 1
    assert not target.exists()


def test_equal_names_keep_distinct_directories_and_clear_only_history(tmp_path):
    store = RecentProjects(tmp_path / "recent.json")
    first, second = tmp_path / "a/Model.anthroforge", tmp_path / "b/Model.anthroforge"
    store.remember(first)
    store.remember(second)
    rows = store.rows()
    assert rows[0]["name"] == rows[1]["name"] == "Model"
    assert rows[0]["directory"] != rows[1]["directory"]
    store.clear()
    assert RecentProjects(store.path).entries == ()


def test_bad_history_requires_explicit_clear(tmp_path):
    path = tmp_path / "recent.json"
    path.write_text('{"schema":10}')
    store = RecentProjects(path)
    assert store.error and not store.entries
    with pytest.raises(ValueError, match="Clear recent"):
        store.remember(tmp_path / "file.anthroforge")
    assert path.read_text() == '{"schema":10}'
    store.clear()
    store.remember(tmp_path / "file.anthroforge")
    assert RecentProjects(path).entries == store.entries


def test_failed_write_preserves_previous_history(tmp_path, monkeypatch):
    from anthroforge.application import user_json

    path = tmp_path / "recent.json"
    store = RecentProjects(path)
    store.remember(tmp_path / "first.anthroforge")
    before = path.read_bytes()
    monkeypatch.setattr(
        user_json.os, "replace", lambda *args: (_ for _ in ()).throw(OSError("disk"))
    )
    with pytest.raises(OSError, match="disk"):
        store.remember(tmp_path / "second.anthroforge")
    assert path.read_bytes() == before and RecentProjects(path).entries == store.entries
    assert not list(tmp_path.glob("*.tmp"))
