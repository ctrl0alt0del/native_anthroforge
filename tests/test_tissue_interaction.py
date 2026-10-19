"""Tissue anatomy selection and shared command entry points, without a visible window."""

import pytest
from PySide6.QtCore import QCoreApplication

from anthroforge.desktop.controller import Controller
from tests.test_tissue_workflow import assembly


@pytest.fixture
def controller():
    app = QCoreApplication.instance() or QCoreApplication([])
    controller = Controller()
    controller.timer.stop()
    yield controller
    controller.close()
    assert app


def test_tissue_is_anatomy_with_mesh_and_no_transform(controller):
    _, source, target = assembly(controller.session)
    controller.refresh()
    controller.select(target)
    row = controller.selectedData
    assert row["is_tissue"] and not row["is_construction"]
    assert not row["transformable"]
    assert row["handle"] and row["source"] == source
    assert target in {r["id"] for r in controller.treeRows}
    assert target not in controller.construction.records
    assert controller.selectionCenter()


def test_creation_selects_tissue_and_settings_preserve_source(controller):
    _, source, _ = assembly(controller.session)
    controller.refresh()
    controller.select(source)
    key = controller.createConstruction("tissue.create", dict(source=source))
    controller.session.wait()
    controller.refresh()
    assert controller.selection == key
    assert controller.selectedData["is_tissue"]
    controller.run("tissue.configure", dict(target=key, changes=dict(stacking=False)))
    controller.session.wait()
    controller.refresh()
    assert controller.selectedData["status"] == "ready"
