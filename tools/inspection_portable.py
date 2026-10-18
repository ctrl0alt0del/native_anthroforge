"""Two surface witnesses and persistent named cameras through the shipped headless API."""

import json
from zipfile import ZipFile

CAMERA = [0, 0, 0, 0, 0, 0, 3]


def request(operation, **arguments):
    return dict(operation=operation, arguments=arguments)


def rulers():
    return [
        dict(id="mesh", **request("import", path="examples/primitives/cube.obj", units=1)),
        request("wait"),
        sample("first", [1, 0, 0]),
        sample("second", [0, 1, 0]),
        request("measurement.add", start="$first", end="$second", name="Width"),
    ]


def sample(identity, weights):
    return dict(
        id=identity,
        **request("measurement.point", entity="$mesh.entity_id", triangle=0, weights=weights),
    )


def views():
    return [
        request("workspace.update", camera=CAMERA, orthographic=True, display_units="mm"),
        dict(id="view", **request("bookmark.add", name="Comparison")),
        request("workspace.update", camera=[1, 2, 3, 10, 20, 30, 6], orthographic=False),
        request("bookmark.restore", bookmark="$view"),
        request("save", path="measurements.anthroforge", blocked_policy="wait"),
    ]


def inspection(executable, cwd, invoke):
    (cwd / "measurements.json").write_text(json.dumps(rulers() + views()))
    invoke(executable, cwd, "--cli", "run", "measurements.json")
    state = json.loads(invoke(executable, cwd, "--cli", "inspect", "measurements.anthroforge"))
    path = cwd / "measurements.afinspection.zip"
    arguments = ("--cli", "report", "measurements.anthroforge", str(path))
    invoke(executable, cwd, *arguments, "--revision", str(state["revision"]))
    verify(path)


def verify(path):
    with ZipFile(path) as archive:
        data = json.loads(archive.read("inspection.json"))
        assert archive.read("image.png").startswith(b"\x89PNG")
    workspace, ruler = data["workspace"], data["measurements"][0]
    assert workspace["bookmarks"][0]["name"] == "Comparison"
    assert workspace["camera"] == CAMERA and workspace["orthographic"]
    assert workspace["display_units"] == "mm"
    assert ruler["distance"] > 0 and not ruler["stale"]
    assert len(ruler["start"]["position"]) == 3 and len(ruler["delta"]) == 3
