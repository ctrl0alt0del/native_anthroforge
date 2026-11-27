"""Real Qt mode/Retry interaction with default FIELD and the configured AVBD runtime."""

import json
import os
import sys
from pathlib import Path

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from preferences_acceptance import choose
from PySide6.QtCore import QPointF
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from shiboken6 import delete
from skin_foundation_acceptance import edit_field
from ui_acceptance import click, find

from anthroforge.application import skin_field_builder
from anthroforge.desktop.app import create_engine
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.qt_profiler import profiler_application
from anthroforge.desktop.runtime import native_runtime


def settle(controller):
    controller.session.wait()
    controller.refresh()
    QTest.qWait(300)


def capture(window, output, name):
    QTest.qWait(150)
    assert window.grabWindow().save(str(output / (name + ".png")))


def configure(controller, section, **values):
    controller.session.command("skin.configure", section=section, values=values)


def setup(controller, window):
    assert skin_field_builder.TARGET_RESOLUTION == 220
    result = controller.run(
        "import", dict(path=str(Path("examples/primitives/cube.obj").resolve()), units=1)
    )
    settle(controller)
    skin = controller.session.document.skin
    data = controller.session.resources.skin[skin.envelope.data]
    assert json.loads(data.metadata)["resolution"] == 220
    configure_final(controller)
    controller.cameraRequested.emit([0, 0, 0, -18, 25, 0, 3], False)
    window.resize(1050, 800)
    click(window, "skinTab")
    return result["entity_id"]


def configure_final(controller):
    configure(
        controller, "topology_settings", backend="INSTANT", target_quads=1000, symmetry="NONE"
    )
    configure(controller, "deformation_settings", proxy_resolution=8)


def move(controller, target, offset):
    controller.run("scp.transform", dict(entity=target, values=[offset, 0, 0, 0, 0, 0, 1, 1, 1]))
    settle(controller)


def final_mode(controller, window, target, output):
    draft = controller.session.document.skin.envelope
    click(window, "skinFinalMode")
    settle(controller)
    before = controller.session.document.skin
    assert before.update_mode == "FINAL" and before.final.status == "ready", controller.message
    assert before.envelope == draft and before.final.asset
    move(controller, target, 0.1)
    after = controller.session.document.skin
    assert after.envelope == draft and after.topology == before.topology
    assert after.reference == before.reference and after.final.asset != before.final.asset
    capture(window, output, "final-mode")
    return after


def draft_mode(controller, window, target, previous, output):
    click(window, "skinFinalMode")
    settle(controller)
    skin = controller.session.document.skin
    assert skin.update_mode == "DRAFT" and skin.envelope != previous.envelope
    assert skin.final.asset == previous.final.asset
    edit_field(window, "skin_gap_strength", "30")
    applied = skin.applied_draft
    move(controller, target, 0.2)
    assert controller.session.document.skin.applied_draft == applied
    assert "pending" in find(window, "skinConfigurationState").property("text").lower()
    capture(window, output, "draft-pending-settings")


def bounds(window):
    item = find(window, "skinRetry")
    point = item.mapToScene(QPointF(0, 0))
    return point.x(), point.y(), item.width(), item.height()


def fail_selection(controller, window, output):
    previous = controller.session.document.skin.envelope
    runtime = os.environ["ANTHROFORGE_AVBD_RUNTIME"]
    try:
        os.environ["ANTHROFORGE_AVBD_RUNTIME"] = str(output / "unavailable-runtime")
        choose(window, 1, "skinDraftBuilder")
        settle(controller)
    finally:
        os.environ["ANTHROFORGE_AVBD_RUNTIME"] = runtime
    assert controller.session.document.skin.envelope == previous
    assert find(window, "skinRetry").isEnabled()
    assert not find(window, "skinResetEnvelope").isVisible()
    capture(window, output, "builder-unavailable")


def retry(controller, window, output):
    fail_selection(controller, window, output)
    position = bounds(window)
    click(window, "skinRetry")
    settle(controller)
    skin = controller.session.document.skin
    assert skin.applied_draft.configuration.builder == "AVBD", controller.message
    assert skin.checkpoints and skin.envelope.asset
    assert not find(window, "skinRetry").isEnabled() and bounds(window) == position
    capture(window, output, "avbd-retry-complete")
    window.resize(900, 640)
    capture(window, output, "avbd-narrow")


def persistence(controller, window, output):
    path = str(output / "pipeline.anthroforgex")
    before = controller.session.document.skin
    controller.run("save", dict(path=path, blocked_policy="wait"))
    settle(controller)
    controller.run("open", dict(path=path))
    settle(controller)
    assert controller.session.document.skin == before
    assert not controller.session.skin_pipeline.active()
    assert not find(window, "skinFinalMode").property("checked")
    capture(window, output, "reopened-extended")


def exercise(application, output):
    controller, warnings = Controller(), []
    engine = create_engine(controller, warnings)
    try:
        window = engine.rootObjects()[0]
        target = setup(controller, window)
        previous = final_mode(controller, window, target, output)
        draft_mode(controller, window, target, previous, output)
        retry(controller, window, output)
        persistence(controller, window, output)
        assert not warnings, warnings
    finally:
        controller.close()
        delete(engine)
        application.processEvents()


def main():
    output = Path(sys.argv[1]).resolve()
    output.mkdir(parents=True, exist_ok=True)
    os.environ["ANTHROFORGE_PREFERENCES_PATH"] = str(output / "preferences.json")
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        application = profiler_application()
        QFontDatabase.addApplicationFont("C:/Windows/Fonts/segoeui.ttf")
        application.setFont(QFont("Segoe UI"))
        exercise(application, output)
    print("Qt mode, default FIELD, AVBD Retry, stable status and extended reopen passed.")


if __name__ == "__main__":
    main()
