"""Inspect accepted skin stages in a saved project using a hidden GPU viewport."""

import argparse
import os
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle
from PySide6.QtTest import QTest
from tissue_scene_acceptance import frames

from anthroforge.application import projects, storage
from anthroforge.desktop import offscreen, runtime
from anthroforge.desktop.controller import Controller


def initialize(controller, options):
    state = storage.read_package(options.project, controller.session.engine)
    projects.adopt(controller.session, *state)
    assert controller.session.document.skin.topology.asset, "No accepted skin topology to inspect."
    controller.run("view.hide", dict(targets=list(controller.session.document.registry.records)))
    controller.refresh()


def capture(controller, renderer, application, mesh, output):
    bounds = mesh.bounds
    center = [(bounds[i] + bounds[i + 3]) / 2 for i in range(3)]
    extent = max(bounds[i + 3] - bounds[i] for i in range(3))
    for name, angles in views():
        controller.cameraRequested.emit([*center, *angles, extent * 1.6], True)
        image = settle(controller, renderer, application, mesh.handle)
        assert image.save(str(output.with_name(output.name + "-" + name + ".png")))


def views():
    return (
        ("axis-y", (0, 0, 0)),
        ("oblique", (-15, 30, 0)),
        ("axis-x", (0, 90, 0)),
        ("oblique-x", (-15, 120, 0)),
        ("back", (0, 180, 0)),
    )


def settle(controller, renderer, application, handle):
    for _ in range(200):
        controller.process_tick()
        QTest.qWait(20)
        image = frames(controller, renderer, application)
        if any(row["handle"] == handle for row in controller.render_model.active_rows()):
            return image
    raise AssertionError("Accepted skin did not reach the displayed geometry revision.")


def stages(controller, renderer, application, output):
    for name in ("envelope", "topology", "final"):
        stage = getattr(controller.session.document.skin, name)
        if not stage.asset:
            continue
        controller.run("workspace.update", dict(skin_display=name.upper()))
        controller.refresh()
        capture(
            controller,
            renderer,
            application,
            controller.session.assets[stage.asset].mesh,
            output / name,
        )


def fitted(controller, renderer, application, output):
    for item in controller.session.document.skin.fits:
        data = controller.session.resources.skin[item.data].arrays
        values = data["keys"]
        for label, value in (("middle", float(values.mean())), ("maximum", float(values.max()))):
            controller.run("skin.fit.preview", dict(identity=item.id, value=value))
            controller.session.wait()
            controller.refresh()
            candidate = controller.session.skin_fit_preview.asset
            assert candidate is not None, controller.session.skin_fit_preview.error
            capture(controller, renderer, application, candidate.mesh, output / ("fit-" + label))
        controller.run("skin.fit.preview.cancel", {})


def run(application, options):
    controller, warnings = Controller(), []
    controller.timer.stop()
    renderer = offscreen.Offscreen(controller, warnings)
    try:
        initialize(controller, options)
        stages(controller, renderer, application, options.output)
        fitted(controller, renderer, application, options.output)
        assert not warnings, warnings
    finally:
        renderer.close()
        controller.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("output", type=Path)
    options = parser.parse_args()
    options.output.mkdir(parents=True, exist_ok=True)
    if native := os.environ.get("AF_SKIN_BUILD"):
        runtime.build_directory = lambda: Path(native)
        offscreen.build_directory = runtime.build_directory
    QQuickStyle.setStyle("Basic")
    application = QGuiApplication([])
    with runtime.native_runtime():
        run(application, options)


if __name__ == "__main__":
    main()
