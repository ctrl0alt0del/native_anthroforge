"""Anatomy presentation keeps each subtree contiguous without reordering authored data."""

import pytest
from PySide6.QtCore import QCoreApplication

from anthroforge.core.construction import Control
from anthroforge.core.entities import SCP
from anthroforge.desktop.controller import Controller
from tests.test_tissue_workflow import assembly


def anatomy():
    links = [
        ("root", ""),
        ("b", "root"),
        ("a", "root"),
        ("b1", "b"),
        ("a1", "a"),
        ("b2", "b"),
        ("tip", "b1"),
    ]
    return tuple(SCP(key, id=key, parent=parent) for key, parent in links)


@pytest.fixture
def controller():
    app = QCoreApplication.instance() or QCoreApplication([])
    value = Controller()
    value.timer.stop()
    value.session.replace_document(entities=anatomy())
    value.refresh()
    yield value
    value.close()
    assert app


def identities(controller):
    return [row["id"] for row in controller.selection_view.treeRows]


def test_tree_keeps_descendants_before_siblings_without_changing_document_order(controller):
    document = controller.session.document
    assert identities(controller) == ["root", "b", "b1", "tip", "b2", "a", "a1"]
    assert [r["depth"] for r in controller.selection_view.treeRows] == [0, 1, 2, 3, 2, 1, 2]
    assert document.entities == anatomy()
    assert document.index.structure.order == ("root", "b", "a", "b1", "b2", "a1", "tip")


def test_reparent_and_undo_keep_sibling_order_and_selection(controller):
    controller.selection_view.select("a1")
    controller.run("scp.reparent", dict(entity="a1", parent="b"))
    assert identities(controller) == ["root", "b", "b1", "tip", "a1", "b2", "a"]
    assert controller.selection == "a1"
    controller.run("undo", {})
    assert identities(controller) == ["root", "b", "b1", "tip", "b2", "a", "a1"]
    assert controller.selection == "a1"


def test_controls_stay_out_of_anatomy_and_empty_document_clears_rows(controller):
    control = Control("Hook", "HOOK", id="hook")
    controller.session.replace_document(controls=(control,))
    controller.refresh()
    assert "hook" not in identities(controller)
    assert "hook" in controller.construction.records
    controller.session.replace_document(entities=(), controls=())
    controller.refresh()
    assert identities(controller) == []


def test_tissues_stay_visible_with_construction_parents_outside_anatomy(controller):
    controller.session.replace_document(entities=())
    _, source, target = assembly(controller.session)
    controller.refresh()
    assert target in identities(controller) and source not in identities(controller)
    row = next(r for r in controller.selection_view.treeRows if r["id"] == target)
    assert row["is_tissue"]
