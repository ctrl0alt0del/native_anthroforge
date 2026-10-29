"""Hidden desktop candidate versus isolated exported images, using the same camera/layers."""

import json
import os
import sys
import zipfile
from contextlib import closing
from pathlib import Path

import numpy as np
from PIL import Image
from PySide6.QtGui import QGuiApplication
from PySide6.QtQuickControls2 import QQuickStyle

from anthroforge.application import inspection_snapshot_export, inspection_snapshots
from anthroforge.desktop import inspection_capture
from anthroforge.desktop.controller import Controller
from anthroforge.desktop.offscreen import Offscreen
from anthroforge.desktop.runtime import native_runtime


def prepare(controller):
    session = controller.session
    root = session.command("scp.empty", name="Comparison")
    path = str(Path(__file__).resolve().parents[1] / "examples/primitives/cube.obj")
    bone = session.command("import", path=path, units=1.0, parent=root)["entity_id"]
    session.wait()
    session.command("mirror.configure", target=root, enabled=True, shift=1)
    state = session.command("scp.mesh.replace.assess", target=bone, path=path)
    session.wait()
    result = session.command("inspection.capture", kind="mesh_replacement", token=state["token"])
    return inspection_snapshots.selected(session, result["snapshot"])


def comparison(app, controller, renderer, snapshot, output, yaw, mode):
    options = dict(mode=mode, camera=[1, 0, 0, -15, yaw, 45, 8])
    view = inspection_snapshot_export.view_settings(snapshot, options)
    image = inspection_capture.draw(app, controller, renderer, dict(view=view), snapshot.layers)
    live = output / f"desktop-{mode}-{yaw}.png"
    assert image.save(str(live))
    evidence = inspection_capture.displayed(controller, snapshot.layers, view)
    assert evidence["complete"] and not renderer.window.isVisible()
    archive = output / f"export-{mode}-{yaw}.afinspection.zip"
    controller.session.command(
        "inspection.export", snapshot=snapshot.identity, path=str(archive), view=view, wait=True
    )
    return pixels(live, archive, evidence)


def pixels(live, archive, scene):
    with zipfile.ZipFile(archive) as data:
        exported = live.with_name(live.stem.replace("desktop", "export") + ".png")
        exported.write_bytes(data.read("image.png"))
        evidence = json.loads(data.read("image.png.json"))
    before = np.asarray(Image.open(live).convert("RGB"), dtype=np.int16)
    after = np.asarray(Image.open(exported).convert("RGB"), dtype=np.int16)
    difference = np.abs(before - after)
    assert evidence["scene"] == scene and evidence["captured"] and not evidence["window_visible"]
    assert difference.max() <= 1, (difference.max(), difference.mean())
    return dict(live=str(live), exported=str(exported), maximum=int(difference.max()))


def render(app, output):
    warnings = []
    with closing(Controller()) as controller:
        controller.capture_mode = True
        controller.timer.stop()
        snapshot = prepare(controller)
        with closing(Offscreen(controller, warnings)) as renderer:
            rows = [
                comparison(app, controller, renderer, snapshot, output, yaw, mode)
                for yaw, mode in ((0, "Split"), (55, "Overlay"))
            ]
        assert not warnings, warnings
        return rows


def main(directory):
    output = Path(directory).resolve()
    output.mkdir(parents=True, exist_ok=True)
    if os.name == "nt":
        os.environ["QT_QPA_PLATFORM"] = "windows"
    QQuickStyle.setStyle("Basic")
    app = QGuiApplication([])
    with native_runtime():
        rows = render(app, output)
    (output / "comparison.json").write_text(json.dumps(rows, indent=2), "utf-8")
    print(json.dumps(dict(passed=True, comparisons=rows, visible_window=False)))


if __name__ == "__main__":
    main(sys.argv[1])
