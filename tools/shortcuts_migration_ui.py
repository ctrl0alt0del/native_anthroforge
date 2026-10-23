"""Production controls for retained Bezier interpolation and explicit policy scope."""

import os

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from pathlib import Path

from PySide6.QtCore import Q_ARG, QMetaObject
from PySide6.QtGui import QFont, QFontDatabase, QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shortcuts_editor_acceptance import create_engine, prepare, settle
from ui_acceptance import find

from anthroforge.desktop.controller import Controller

OUTPUT = Path("build/shortcuts-migration-ui")


def driver(session, root, child):
    key = session.command("driver.create", label="Shared control", value=1.0)
    for target in (root, child):
        ref = dict(target=target, path=["transform", "scale"], component=0)
        session.command("driver.formula.add", driver=key, target=ref, expression="value")
    session.wait(5)
    return key


def activate(choice, index):
    choice.setProperty("currentIndex", index)
    assert QMetaObject.invokeMethod(choice, "activated", Q_ARG(int, index))


def interpolation(controller, engine, curve):
    window = engine.rootObjects()[0]
    activate(find(window, "parametricInterpolation"), 1)
    settle(controller)
    assert controller.session.document.object(curve).engine_settings.interpolation == "BEZIER"
    engine.probe_curve.synchronize(controller.session.document.object(curve))
    QTest.qWait(80)
    assert window.grabWindow().save(str(OUTPUT / "bezier-editor.png"))


def multi_owner(controller, curve):
    session = controller.session
    root = session.command("primitive.from_curves", curves=[curve], kind="BODY")
    child = session.command("primitive.create", kind="BODY", parent=root)
    settle(controller)
    key = driver(session, root, child)
    controller.refresh()
    controller.shortcut_panel.editor.select(key)
    return root, child, key


def scope(controller, engine, curve):
    root, child, key = multi_owner(controller, curve)
    window, adapter = engine.rootObjects()[0], controller.shortcut_panel.editor.policies
    find(window, "shortcutPolicies").setProperty("expanded", True)
    QTest.qWait(80)
    index = next(i for i, row in enumerate(adapter.scopeOptions) if row["id"] == root)
    activate(find(window, "shortcutAttachmentScope"), index)
    adapter.override(child, "follow_rotation", "DISABLED")
    settle(controller)
    info = controller.session.command("driver.inspect", driver=key)
    assert info["policy"]["scope"] == root and not info["scp_owner"]
    assert info["policy"]["descendants"][0]["follow_rotation"] == "DISABLED"
    assert window.grabWindow().save(str(OUTPUT / "scope-editor.png"))


def run():
    controller, warnings = Controller(), []
    try:
        curve, _, _ = prepare(controller)
        engine = create_engine(controller, curve, warnings)
        interpolation(controller, engine, curve)
        scope(controller, engine, curve)
        assert not warnings, warnings
        engine.rootObjects()[0].close()
    finally:
        controller.close()


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    QQuickStyle.setStyle("Basic")
    application = QGuiApplication([])
    QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
    application.setFont(QFont("Segoe UI", 10))
    run()
    print("Offscreen production Bezier and explicit attachment-scope controls passed.")
