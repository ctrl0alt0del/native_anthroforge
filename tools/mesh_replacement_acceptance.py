"""Exercise source selection and explicit replacement approval without desktop input."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"
if os.name == "nt":
    os.environ.setdefault("QT_QPA_FONTDIR", os.path.join(os.environ["SystemRoot"], "Fonts"))

from pathlib import Path

from PySide6.QtCore import QMetaObject, QObject, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from ui_acceptance import find

from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.runtime import native_runtime

OUTPUT = Path("build/parity-workflows-034/replacement")


def settle(controller):
    controller.session.wait(10)
    controller.refresh()
    QTest.qWait(200)


def scene(controller):
    target = controller.run("import", dict(path="examples/primitives/cube.obj", units=1))[
        "entity_id"
    ]
    settle(controller)
    controller.run("import", dict(path="examples/primitives/cube.obj", units=0.1, parent=target))
    settle(controller)
    controller.selection_view.select(target)
    return target


def replacement_file():
    path = OUTPUT / "tetra.obj"
    path.write_text("v 0 0 0\nv 1 0 0\nv 0 1 0\nv 0 0 1\nf 1 3 2\nf 1 2 4\nf 2 3 4\nf 3 1 4\n")
    return str(path.resolve())


def exercise(controller, window):
    target = scene(controller)
    settle(controller)
    choose_source(window)
    controller.mesh_replacement.assess(replacement_file())
    settle(controller)
    assert window.property("modalOpen")
    approve(controller, window, target)
    automatic(controller, window)


def choose_source(window):
    button = next(
        o
        for o in window.findChildren(QObject)
        if o.objectName() == "replaceImportedMesh" and o.property("visible")
    )
    assert button.property("visible") and button.property("enabled")
    assert QMetaObject.invokeMethod(button, "clicked", Qt.DirectConnection)
    assert window.property("modalOpen")
    assert QMetaObject.invokeMethod(find(window, "replacementFile"), "reject", Qt.DirectConnection)


def approve(controller, window, target):
    cursor = controller.session.history.cursor
    assert not find(window, "applyReplacement").property("enabled")
    activate(window, "approveReplacementChanges")
    activate(window, "applyReplacement")
    settle(controller)
    assert not window.property("modalOpen")
    assert controller.session.history.cursor == cursor + 1
    item = controller.session.document.entity(target)
    assert item.result.status == "ready", item.result.error
    assert controller.session.assets[item.primitive.source].mesh.counts[0] == 4
    assert window.grabWindow().save(str(OUTPUT / "reviewed-replacement.png"))


def automatic(controller, window):
    cursor = controller.session.history.cursor
    controller.mesh_replacement.assess(replacement_file())
    settle(controller)
    assert not controller.mesh_replacement.active
    assert not window.property("modalOpen")
    assert controller.session.history.cursor == cursor + 1


def activate(window, name):
    assert QMetaObject.invokeMethod(find(window, name), "clicked", Qt.DirectConnection)


def run():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        exercise(controller, engine.rootObjects()[0])
        assert not warnings, warnings
        assert not controller.message, controller.message
        print("Offscreen replacement: source button, review, approval and one undo passed.")
    finally:
        controller.close()
        delete(engine)


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        run()
