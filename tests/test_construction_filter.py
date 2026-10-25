"""Construction search preserves keyed source rows and follows incremental updates."""

import pytest

pytest.importorskip("PySide6")

from anthroforge.desktop.construction_filter import ConstructionFilter
from anthroforge.desktop.record_model import RecordModel


def row(key, name, kind="CURVE"):
    return dict(id=key, item=dict(id=key, name=name, kind=kind))


def test_case_insensitive_search_and_kind_without_source_mutation():
    source = RecordModel(None, ("item",), "id")
    rows = [row("a", "Ribs"), row("b", "Arm", "FIBER")]
    source.synchronize_records(rows)
    proxy = ConstructionFilter(source)
    proxy.search(" RIBS ")
    assert proxy.rowCount() == 1 and proxy.mapToSource(proxy.index(0, 0)).row() == 0
    proxy.search("fiber")
    assert proxy.rowCount() == 1 and proxy.mapToSource(proxy.index(0, 0)).row() == 1
    proxy.search("absent")
    assert proxy.rowCount() == 0 and source.rows == rows
    proxy.search("")
    assert proxy.rowCount() == 2


def test_matching_rows_follow_rename_insert_and_removal():
    source = RecordModel(None, ("item",), "id")
    source.synchronize_records([row("a", "Ribs")])
    proxy = ConstructionFilter(source)
    proxy.search("Arm")
    source.synchronize_records([row("a", "Arm")])
    assert proxy.rowCount() == 1
    source.synchronize_records([row("a", "Arm"), row("b", "Arm detail")])
    assert proxy.rowCount() == 2
    source.synchronize_records([row("b", "Hand")])
    assert proxy.rowCount() == 0
