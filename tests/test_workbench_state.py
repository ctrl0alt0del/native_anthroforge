"""Desktop layout persistence never belongs to document or preference records."""

import pytest

pytest.importorskip("PySide6")

from anthroforge.desktop.workbench_state import WorkbenchState


def test_layout_roundtrip_and_category_defaults(tmp_path):
    path = tmp_path / "layout.ini"
    state = WorkbenchState(path=path)
    state.setPage("TISSUE", "Inspect")
    state.setExpanded("tissue/source", True)
    state.savePanes(220, 350)
    state.setFocusEditor(True)
    state.settings.sync()
    restored = WorkbenchState(path=path)
    assert restored.page("TISSUE") == "Inspect"
    assert restored.page("CURVE") == "Shape"
    assert restored.expanded("tissue/source", False)
    assert restored.paneWidth("inspector", 330) == 350
    assert restored.focusEditor


def test_invalid_layout_recovers_without_changing_document_defaults(tmp_path):
    state = WorkbenchState(path=tmp_path / "layout.ini")
    state.settings.setValue("pages/SCP", "missing page")
    state.settings.setValue("panes/inspector", "invalid")
    assert state.page("SCP") == "Shape"
    assert state.paneWidth("inspector", 330) == 330
    state.setPage("SCP", "invalid")
    state.savePanes(-100, 10000)
    assert state.page("SCP") == "Shape"
    assert state.paneWidth("navigation", 210) == 195
    assert state.paneWidth("inspector", 330) == 500
    assert not state.expanded("unseen", False)
    assert state.expanded("unseen", True)
