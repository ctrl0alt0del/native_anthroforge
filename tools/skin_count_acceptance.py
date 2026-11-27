"""Exercise Draft root authoring and Topology budget navigation in real QML."""

import os
import sys
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from skin_foundation_acceptance import edit_field
from ui_acceptance import click, find

from anthroforge.application import skin_builder_configuration as builders
from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.qt_profiler import profiler_application
from anthroforge.desktop.runtime import native_runtime


def settle(controller):
    controller.refresh()
    QTest.qWait(150)


def root_count(controller, window):
    before = controller.session.document.skin
    edit_field(window, "skinRootVertices", "802")
    assert builders.decode(controller.session.document.skin).root_vertices == 802
    assert controller.session.document.skin.envelope == before.envelope
    assert controller.session.document.skin.topology_settings == before.topology_settings
    controller.run("undo", {})
    settle(controller)
    assert builders.decode(controller.session.document.skin).root_vertices == 402


def budget_navigation(controller, window):
    root, child = (row.id for row in controller.session.document.entities)
    controller.run(
        "skin.contributor.configure",
        dict(owner=root, values=dict(density_mode="SUBTREE_BUDGET", target_quads=6000)),
    )
    controller.selection_view.select(child)
    settle(controller)
    assert "6000" in find(window, "skinParentBudget").property("text")
    click(window, "skinEditParentBudget")
    assert controller.selection == root
    document_budget(controller, window)


def document_budget(controller, window):
    click(window, "skinEditParentBudget")
    assert find(window, "skinQuadCountValue").hasActiveFocus()
    edit_field(window, "skinQuadCount", "9000")
    assert controller.session.document.skin.topology_settings.target_quads == 9000
    assert builders.decode(controller.session.document.skin).root_vertices == 402
    edit_field(window, "skinSubtreeQuads", "6500")
    assert controller.skin_panel.state["contributor"]["settings"]["target_quads"] == 6500


def capture(window, output):
    find(window, "skinPane").property("contentItem").setProperty("contentY", 0)
    QTest.qWait(100)
    root = find(window, "skinRootVertices").mapToScene(QPointF()).y()
    total = find(window, "skinQuadCount").mapToScene(QPointF()).y()
    subtree = find(window, "skinSubtreeQuads").mapToScene(QPointF()).y()
    assert root < total < subtree
    assert window.grabWindow().save(str(output / "counts-wide.png"))
    window.resize(900, 640)
    QTest.qWait(150)
    assert window.grabWindow().save(str(output / "counts-narrow.png"))
    narrow_navigation(window, output)


def narrow_navigation(window, output):
    pane = find(window, "skinPane").property("contentItem")
    pane.setProperty("contentY", 600)
    QTest.qWait(100)
    click(window, "skinEditParentBudget")
    field = find(window, "skinQuadCountValue")
    assert field.hasActiveFocus()
    assert 0 < field.mapToScene(QPointF()).y() < window.height() - 80
    assert window.grabWindow().save(str(output / "counts-narrow-budget.png"))
    QTest.keyClick(window, Qt.Key.Key_Tab)


def exercise(application, source, output):
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        window = setup(controller, engine, source)
        root_count(controller, window)
        budget_navigation(controller, window)
        capture(window, output)
        assert not warnings, warnings
    finally:
        controller.close()
        delete(engine)


def setup(controller, engine, source):
    controller.run("open", dict(path=str(source)))
    window = engine.rootObjects()[0]
    window.resize(1400, 1200)
    settle(controller)
    click(window, "skinTab")
    return window


def main():
    source, output = (Path(arg).resolve() for arg in sys.argv[1:3])
    output.mkdir(parents=True, exist_ok=True)
    os.environ["ANTHROFORGE_PREFERENCES_PATH"] = str(output / "preferences.json")
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        application = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        application.setFont(QFont("Segoe UI"))
        exercise(application, source, output)
    print("Root count editing/undo, ancestor/document navigation and topology layout passed.")


if __name__ == "__main__":
    main()
