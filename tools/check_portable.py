"""Check a relocated distribution with a minimal PATH and no developer Qt/Python settings."""

import json
import os
import shutil
import subprocess
import sys
from functools import partial
from pathlib import Path

import numpy as np
from attached_creation_portable import automatic_construction
from authoring_workflows_portable import authoring_workflows
from branch_placement_portable import branches
from comparison_portable import comparison
from construction_portable import construction
from direct_workflow_portable import direct_workflows
from exterior_placement_portable import exterior_placement
from feedback_portable import feedback
from inspection_portable import inspection
from issues_portable import issues
from mirroring_portable import mirroring
from preferences_portable import preferences
from profiler_portable import profiling
from projects_portable import projects
from PySide6.QtGui import QImage
from shortcuts_portable import shortcuts
from skin_portable import qualify as skin
from spatial_inspection_portable import spatial_inspection
from tissue_portable import tissues
from workflow_portable import workflow

CHECKS = (
    "import",
    "attachments",
    "primitives",
    "deformers",
    "deletion",
    "curve subdivision",
    "save",
    "inspect",
    "render",
    "GUI",
    "runtime profiling",
    "issue reporting and verified repair",
    "workflow inspection, units, workspace policies and image/JSON report",
    "surface rulers, named cameras and explanatory profile diagnostics",
    "independent fibers, shared lofts and portable embedded reference images",
    "window feedback capture, annotations, inbox preview, text editing and deletion",
    "tissues, attached construction, stacking, native profiling and rendering",
    "automatic Fiber endpoints, independent copies, undo/redo and shared deletion impact",
    "direct tissue creation with automatic attached construction",
    "branched point creation, automatic surface grouping and membrane conversion",
    "exterior-only placement, sealed-cavity exclusion and original-material Fiber/Anchor capture",
    "persistent preferences, Custom/PIQP routed curves and fibers, saved/report provenance",
    "accepted tissue stages, displacement, point explanations and advisory geometry reports",
    "stacking footprints, material brush commit/undo, section cutaways and routed Fiber evidence",
    "shortcut formulas, typed Parametric paths, persisted results and native consumer rendering",
    "shortcut influence, captured formula inputs, effective policy and propagation completion",
    "session comparison, paired images, bounded replay journal and isolated replay",
    "strict mirrors, symmetric loops, instance measurements and schema-7 storage",
    "Fiber pins/supports/cold routing, mirrored tubes, SCP split/replacement and tissue retarget",
    "recent-project history, asynchronous recovery capture and discovery with original retention",
    "skin build, native proxy workers, isolated fitting, persisted playback and OBJ quads",
    "spatial measures, qualified volume samples, placement explanation and frozen view export",
)


def clean_environment(background=False):
    env = {
        k: v
        for k, v in os.environ.items()
        if not k.startswith(("PYTHON", "QT_", "QML_", "ANTHROFORGE_", "AF_"))
    }
    system = os.environ["SystemRoot"]
    env["PATH"] = str(Path(system) / "System32") + ";" + system
    return platform_environment(env, background)


def platform_environment(env, background):
    if background:
        env["QT_QPA_PLATFORM"] = "offscreen"
        env["QT_QPA_FONTDIR"] = str(Path(os.environ["SystemRoot"]) / "Fonts")
    return env


def invoke(executable, cwd, *arguments, background=False):
    environment = clean_environment(background)
    environment["ANTHROFORGE_PREFERENCES_PATH"] = str(cwd / "preferences.json")
    result = subprocess.run(
        [str(executable), *arguments],
        cwd=cwd,
        env=environment,
        capture_output=True,
        text=True,
        timeout=90,
    )
    assert result.returncode == 0, f"Exit {result.returncode}: {result.stdout}{result.stderr}"
    return result.stdout


def headless(executable, cwd, invoke=invoke):
    doctor = json.loads(invoke(executable, cwd, "--cli", "doctor", "--require-native"))
    assert Path(doctor["native"]["path"]).is_relative_to(executable.parent)
    invoke(executable, cwd, "--cli", "run", "examples/assembly.json")
    state = json.loads(invoke(executable, cwd, "--cli", "inspect", "assembly.anthroforge"))
    assert state["entity_count"] == 2
    render(executable, cwd, state["revision"], invoke)
    return doctor


def render(executable, cwd, revision, invoke=invoke):
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


def run(executable, cwd, background=False):
    cwd.mkdir(parents=True, exist_ok=True)
    shutil.copytree(executable.parent / "examples", cwd / "examples", dirs_exist_ok=True)
    command = partial(invoke, background=background)
    doctor = headless(executable, cwd, command)
    for check in qualification_steps():
        check(executable, cwd, command)
    desktop(executable, cwd, command, background)
    projects(executable, cwd, command)
    report = portable_report(executable, doctor, background)
    (cwd / "portable-check.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report))


def qualification_steps():
    return (
        primitives,
        deletion,
        curve_edits,
        profiling,
        issues,
        *inspection_steps(),
        *construction_steps(),
        exterior_placement,
        feedback,
        preferences,
        authoring_workflows,
    )


def construction_steps():
    return (
        construction,
        direct_workflows,
        automatic_construction,
        branches,
        shortcuts,
        comparison,
        mirroring,
        tissues,
        skin,
    )


def inspection_steps():
    return workflow, inspection, spatial_inspection


def deletion(executable, cwd, invoke=invoke):
    requests = deletion_requests()
    (cwd / "deletion.json").write_text(json.dumps(requests), encoding="utf-8")
    invoke(executable, cwd, "--cli", "run", "deletion.json")
    state = json.loads(invoke(executable, cwd, "--cli", "inspect", "deleted.anthroforge"))
    assert state["entity_count"] == 2
    group = next(e for e in state["entities"] if not e["parent"])
    leaf = next(e for e in state["entities"] if e["name"] == "Leaf")
    assert group["name"] == "Root group" and group["primitive"] is None
    assert leaf["parent"] == group["id"]


def deletion_requests():
    return [
        dict(id="root", operation="scp.empty", arguments=dict(name="Root")),
        dict(id="branch", operation="scp.empty", arguments=dict(name="Branch", parent="$root")),
        dict(operation="scp.empty", arguments=dict(name="Leaf", parent="$branch")),
        dict(operation="scp.delete", arguments=dict(entity="$branch")),
        dict(operation="scp.delete", arguments=dict(entity="$root")),
        dict(operation="wait", arguments={}),
        dict(operation="save", arguments=dict(path="deleted.anthroforge", blocked_policy="wait")),
    ]


def primitives(executable, cwd, invoke=invoke):
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


def curve_edits(executable, cwd, invoke=invoke):
    batch = cwd / "curve-edits.json"
    batch.write_text(json.dumps(curve_requests()), encoding="utf-8")
    invoke(executable, cwd, "--cli", "run", batch.name)
    state = json.loads(invoke(executable, cwd, "--cli", "inspect", "curve-edits.anthroforge"))
    curve = state["entities"][0]["primitive"]["curves"][0]["curve"]
    points = next(o["state"]["points"] for o in state["objects"] if o["state"]["id"] == curve)
    assert len(points) == 3 and points[1]["left_mode"] == "FREE"
    assert abs(points[1]["position"][0]) < 0.01


def curve_requests():
    return [
        dict(id="body", operation="primitive.create", arguments=dict(kind="BODY")),
        dict(id="definition", operation="primitive.inspect", arguments=dict(entity="$body")),
        dict(
            operation="curve.split",
            arguments=dict(
                entity="$body", curve="$definition.primitive.curves.0.id", segment=0, parameter=0.5
            ),
        ),
        dict(operation="wait", arguments={}),
        dict(
            operation="save", arguments=dict(path="curve-edits.anthroforge", blocked_policy="wait")
        ),
    ]


def desktop(executable, cwd, invoke=invoke, background=False):
    arguments = (
        "--project",
        "assembly.anthroforge",
        "--smoke-test",
        "--screenshot",
        str(cwd / "desktop.png"),
    )
    smoke = invoke(executable, cwd, *arguments)
    assert json.loads(smoke)["desktop_smoke"]
    if not background:
        verify_geometry_pixels(cwd / "desktop.png")


def portable_report(executable, doctor, background=False):
    report = dict(
        passed=True,
        executable=str(executable),
        environment="minimal PATH",
        desktop_platform="offscreen" if background else "windows",
        native_window_verified=not background,
        viewport_pixels="hidden QQuickRenderControl" if background else "hidden and desktop",
        doctor=doctor,
        checks=CHECKS,
    )
    return report


if __name__ == "__main__":
    run(Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve(), "--offscreen" in sys.argv[3:])
