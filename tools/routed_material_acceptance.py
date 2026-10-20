"""Actual exact-corner geometry, retained attachments, hidden GPU views and runtime trace."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
from construction_profile_qualification import shutdown, wait_export
from PySide6.QtQuickControls2 import QQuickStyle
from shiboken6 import delete
from tissue_scene_acceptance import frames, settle

from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.qt_profiler import QtProfiler, profiler_application
from anthroforge.desktop.runtime import native_runtime
from tests import routed_surface_scene as scene
from tests.test_routed_surface_consumers import fiber_on_target
from tests.test_routed_surface_material import assert_bindings_ready, attached_exact_surface

OUTPUT = Path("build/routed-fiber-surface-stability/production").resolve()


def prepare(controller):
    objects = attached_exact_surface(controller.session)
    tissue = objects["attached"][0].binding.reference.target
    objects["child"] = fiber_on_target(controller.session, tissue, "TISSUE_BASE")
    visible = set(objects["supports"] + objects["fibers"] + [objects["exact"]])
    hidden = [key for key in controller.session.document.registry.records if key not in visible]
    controller.run("workspace.update", dict(hidden=hidden))
    controller.select(objects["exact"])
    settle(controller)
    controller.cameraRequested.emit([0, 0, 0.3, -20, 25, 0, 4.0], True)
    return objects


def arrays(session, objects):
    result = {}
    for i, key in enumerate(objects["fibers"]):
        item = session.document.object(key)
        result[f"path{i}"] = session.resources.paths[item.result.asset].path.array()[:, :3]
    mesh = session.assets[session.document.object(objects["exact"]).result.asset].mesh
    result["surface"], result["triangles"] = mesh.array(0), mesh.array(3)
    result["anchors"] = np.array(
        [session.document.object(a.id).resolved_position for a in objects["attached"]]
    )
    return result


def capture(controller, renderer, app, objects, name, height):
    scene.move(controller.session, objects["supports"][-1], [0, 0, height])
    settle(controller)
    assert_bindings_ready(controller.session, objects["attached"])
    data = arrays(controller.session, objects)
    np.savez(OUTPUT / (name + ".npz"), **data)
    assert frames(controller, renderer, app).save(str(OUTPUT / (name + ".png")))
    controller.session.command(
        "save", path=str(OUTPUT / (name + ".anthroforge")), blocked_policy="wait"
    )
    child = controller.session.document.object(objects["child"].id)
    assert child.result.status == "ready" and child.bindings == objects["child"].bindings
    return evidence(name, data)


def evidence(name, data):
    return dict(
        phase=name,
        route_samples=len(data["path0"]),
        vertices=len(data["surface"]),
        anchors=data["anchors"].tolist(),
        binding_records_unchanged=True,
    )


def recording(controller, renderer, app):
    objects = prepare(controller)
    frames(controller, renderer, app)
    controller.session.command("profile.start")
    evidence = [
        capture(controller, renderer, app, objects, name, height)
        for name, height in (("before", 3), ("blocked", 0), ("restored", 3))
    ]
    controller.session.command("profile.stop", path=str(OUTPUT / "material.afprofile.zip"))
    status = wait_export(controller, app)
    assert status["state"] == "saved", status
    assert not controller.session.scheduler.errors, controller.session.scheduler.errors
    (OUTPUT / "acceptance.json").write_text(json.dumps(evidence, indent=2))


def run(app):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    collector, controller, warnings = QtProfiler(), Controller(), []
    controller.profiler.collector = collector
    renderer = Offscreen(controller, warnings)
    collector.attach(renderer.window, controller)
    try:
        recording(controller, renderer, app)
        assert not warnings, warnings
    finally:
        shutdown(renderer, controller, collector)


if __name__ == "__main__":
    QQuickStyle.setStyle("Basic")
    with native_runtime():
        app = profiler_application()
        try:
            run(app)
        finally:
            delete(app)
