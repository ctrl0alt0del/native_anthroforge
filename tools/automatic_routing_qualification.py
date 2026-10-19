"""Relocated executable acceptance for the user's preserved two-cube routing fixture."""

import hashlib
import json
import shutil
import sys
from pathlib import Path

from check_portable import invoke
from profiler_portable import validate

from anthroforge.application import attachment_assets, curve_sources, storage
from anthroforge.core.routing_obstacles import targets
from anthroforge.native import path_collisions
from anthroforge.native.mesh import GeometryEngine

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = json.loads((ROOT / "tests/fixtures/routing/surface_pins.json").read_text())


def original(source, engine):
    assert hashlib.sha256(source.read_bytes()).hexdigest() == FIXTURE["source"]["sha256"]
    return storage.read_package(source, engine)


def requests(key):
    return [
        dict(operation="profile.start", arguments={}),
        dict(operation="curve.engine_settings", arguments=dict(curve=key, obstacle_mode="AUTO")),
        dict(operation="wait", arguments={}),
        dict(operation="save", arguments=dict(path="routed.anthroforge", blocked_policy="wait")),
        dict(operation="profile.stop", arguments=dict(path="routing.afprofile.zip", wait=True)),
    ]


def execute(executable, output, key):
    (output / "commands.json").write_text(json.dumps(requests(key)))
    result = invoke(
        executable,
        output,
        "--cli",
        "run",
        "commands.json",
        "--project",
        "input.anthroforge",
        background=True,
    )
    (output / "commands-result.json").write_text(result)


def verify(output, source, engine, key):
    document, resources = storage.read_package(output / "routed.anthroforge", engine)
    item = document.object(key)
    assert item.points == source.object(key).points and item.result.status == "ready"
    assert item.engine_settings.obstacle_mode == "AUTO" and not item.engine_settings.obstacles
    surfaces = [e.id for e in source.entities]
    assert set(targets(document, item)) == set(surfaces)
    handles, frames = attachment_assets.surface_inputs(engine, document, resources.meshes, surfaces)
    path = resources.paths[item.result.asset].path
    row = path_collisions.row(path, curve_sources.world(engine, document, key), FIXTURE["contacts"])
    hits, tolerance = path_collisions.check(engine, [row], handles, frames)
    assert (hits < 0).all(), hits
    return dict(revision=document.revision, collision_segments=hits.tolist(), tolerance=tolerance)


def render(executable, output, key, revision):
    write_view(output, key)
    args = ("--cli", "render", "routed.anthroforge", "routed.png", "--revision", str(revision))
    invoke(executable, output, *args, "--view", "view.json", background=True)
    metadata = json.loads((output / "routed.png.json").read_text())
    assert metadata["captured"] and not metadata["window_visible"], metadata


def write_view(output, key):
    view = dict(
        workspace=0,
        selected=key,
        editing=False,
        camera=[0, 0, 0, -25, -96, 0, 4],
        orthographic=False,
    )
    (output / "view.json").write_text(json.dumps(view))


def run(executable, source, output):
    engine = GeometryEngine()
    document, _ = original(source, engine)
    key = next(o.id for o in document.objects if getattr(o, "engine", "") == "ROUTED")
    output.mkdir(parents=True, exist_ok=False)
    shutil.copy2(source, output / "input.anthroforge")
    execute(executable, output, key)
    evidence = verify(output, document, engine, key)
    evidence["build"] = validate(output / "routing.afprofile.zip", False)["environment"]["build"]
    render(executable, output, key, evidence["revision"])
    original(source, engine)
    (output / "qualification.json").write_text(json.dumps(evidence, indent=2))
    print(json.dumps(evidence))


if __name__ == "__main__":
    run(*(Path(value).resolve() for value in sys.argv[1:4]))
