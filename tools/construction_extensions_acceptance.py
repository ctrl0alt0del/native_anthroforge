"""Offscreen production inspector checks for Segment Chain and Shrinkwrap."""

import json
from pathlib import Path

from primitive_acceptance import settle
from PySide6.QtCore import Q_ARG, QMetaObject
from PySide6.QtGui import QFontDatabase, QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest

from anthroforge.desktop.app import create_engine, open_controller, prepare_view
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/construction-extensions-review").resolve()


def find(window, name):
    pending = [window.contentItem()]
    while pending:
        item = pending.pop()
        if item.objectName() == name and item.isVisible():
            return item
        pending.extend(item.childItems())
    raise AssertionError("Visible control missing: " + name)


def number(window, name, value):
    item = find(window, name)
    assert item is not None
    assert QMetaObject.invokeMethod(item, "edited", Q_ARG(float, value))


def assert_value(window, name, expected):
    assert abs(find(window, name).property("value") - expected) < 1e-9


def capture(window, name):
    QTest.qWait(100)
    assert window.grabWindow().save(str(OUTPUT / (name + ".png")))


def reveal(window, name):
    item = find(window, name)
    parent = item.parentItem()
    while parent is not None:
        if parent.property("contentY") is not None:
            parent.setProperty(
                "contentY", max(0, item.mapToItem(parent.property("contentItem"), 0, 0).y() - 40)
            )
            return
        parent = parent.parentItem()


def chain(controller, window):
    controller.authoring.create("SEGMENT_CHAIN", "")
    settle(controller)
    key = controller.selection
    assert_value(window, "segmentLength", 0.3)
    number(window, "segmentLength", 0.7)
    settle(controller)
    assert_value(window, "segmentLength", 0.7)
    controller.authoring.setEditing(True)
    assert not controller.authoring.editing
    controller.viewport_view.frameSelection()
    reveal(window, "segmentLength")
    capture(window, "segment-chain")
    return key


def wrap(controller, window, target):
    controller.authoring.create("LOFT", "")
    settle(controller)
    owner = controller.selection
    controller.authoring.edit("shrinkwrap.add", dict(target=dict(owner=owner), surface=target))
    settle(controller)
    number(window, "shrinkwrapOffset", 0.02)
    settle(controller)
    assert controller.session.document.entity(owner).deformers[0].shrinkwrap.offset == 0.02
    controller.viewport_view.frameSelection()
    reveal(window, "shrinkwrapOffset")
    capture(window, "shrinkwrap")


def verify(controller, window):
    window.resize(1500, 950)
    target = chain(controller, window)
    wrap(controller, window, target)
    assert not controller.session.scheduler.errors, controller.session.scheduler.errors
    controller.session.command(
        "save", path=str(OUTPUT / "editable.anthroforge"), blocked_policy="wait"
    )


def run():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    controller, warnings = open_controller(None), []
    controller.capture_mode = True
    engine = create_engine(controller, warnings)
    prepare_view(controller, None)
    try:
        verify(controller, engine.rootObjects()[0])
        assert not warnings, warnings
        (OUTPUT / "acceptance.json").write_text(json.dumps(dict(passed=True, warnings=warnings)))
    finally:
        controller.close()


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    font = Path("C:/Windows/Fonts/segoeui.ttf")
    if font.exists():
        QFontDatabase.addApplicationFont(str(font))
    with native_runtime():
        run()
