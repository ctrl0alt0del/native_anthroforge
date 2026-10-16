"""Check a relocated distribution with a minimal PATH and no developer Qt/Python settings."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PySide6.QtGui import QImage

CHECKS = ("import", "attachments", "primitives", "deformers", "save", "inspect", "render", "GUI")


def clean_environment():
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(("PYTHON", "QT_", "QML_", "ANTHROFORGE_", "AF_"))
    }
    system = os.environ["SystemRoot"]
    env["PATH"] = str(Path(system) / "System32") + ";" + system
    return env


def invoke(executable, cwd, *arguments):
    result = subprocess.run(
        [str(executable), *arguments],
        cwd=cwd,
        env=clean_environment(),
        capture_output=True,
        text=True,
        timeout=90,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result.stdout


def headless(executable, cwd):
    doctor = json.loads(invoke(executable, cwd, "--cli", "doctor", "--require-native"))
    assert Path(doctor["native"]["path"]).is_relative_to(executable.parent)
    invoke(executable, cwd, "--cli", "run", "examples/assembly.json")
    state = json.loads(invoke(executable, cwd, "--cli", "inspect", "assembly.anthroforge"))
    assert state["entity_count"] == 2
    render(executable, cwd, state["revision"])
    return doctor


def render(executable, cwd, revision):
    arguments = (
        "--cli",
        "render",
        "assembly.anthroforge",
        "capture.png",
        "--revision",
        str(revision),
    )
    invoke(executable, cwd, *arguments)
    verify_capture(cwd, revision)


def verify_capture(cwd, revision):
    capture = json.loads((cwd / "capture.png.json").read_text())
    assert capture["captured"] and capture["revision"] == revision
    assert capture["scene"]["vertices"] == 72 and not capture["window_visible"]
    verify_geometry_pixels(cwd / "capture.png")


def verify_geometry_pixels(path):
    image = QImage(str(path)).convertToFormat(QImage.Format.Format_RGBA8888)
    assert not image.isNull()
    pixels = np.frombuffer(image.constBits(), np.uint8).reshape(image.height(), image.width(), 4)
    red, green, blue = (pixels[:, :, i].astype(int) for i in range(3))
    foreground = (green - red > 10) & (green > blue) & (green > 90)
    assert np.count_nonzero(foreground) > 10000, "Missing expected cube surface pixels"


def run(executable, cwd):
    cwd.mkdir(parents=True, exist_ok=True)
    shutil.copytree(executable.parent / "examples", cwd / "examples", dirs_exist_ok=True)
    doctor = headless(executable, cwd)
    primitives(executable, cwd)
    desktop(executable, cwd)
    report = portable_report(executable, doctor)
    (cwd / "portable-check.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report))


def primitives(executable, cwd):
    invoke(executable, cwd, "--cli", "run", "examples/primitives.json")
    state = json.loads(invoke(executable, cwd, "--cli", "inspect", "primitives.anthroforge"))
    assert state["entity_count"] == 4 and len(state["controls"]) == 2
    assert all(e["result"]["status"] == "ready" for e in state["entities"])
    assert all(e["result"]["asset"] for e in state["entities"] if e["primitive"])
    kinds = {e["primitive"]["kind"] for e in state["entities"] if e["primitive"]}
    assert kinds == {"LOFT", "BODY", "IMPORTED"}
    arguments = ("--project", "primitives.anthroforge", "--smoke-test", "--screenshot")
    smoke = invoke(executable, cwd, *arguments, str(cwd / "primitives.png"))
    assert json.loads(smoke)["desktop_smoke"]


def desktop(executable, cwd):
    arguments = (
        "--project",
        "assembly.anthroforge",
        "--smoke-test",
        "--screenshot",
        str(cwd / "desktop.png"),
    )
    smoke = invoke(executable, cwd, *arguments)
    assert json.loads(smoke)["desktop_smoke"]
    verify_geometry_pixels(cwd / "desktop.png")


def portable_report(executable, doctor):
    report = dict(
        passed=True,
        executable=str(executable),
        environment="minimal PATH",
        doctor=doctor,
        checks=CHECKS,
    )
    return report


if __name__ == "__main__":
    run(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve())
