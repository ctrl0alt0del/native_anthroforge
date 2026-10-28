"""Shared inspection APIs and frozen spatial evidence in the relocated executable."""

import json
from zipfile import ZipFile

from inspection_portable import request


def spatial_inspection(executable, cwd, invoke):
    path = cwd / "spatial-inspection.json"
    path.write_text(json.dumps(commands()))
    invoke(executable, cwd, "--cli", "run", path.name)
    with ZipFile(cwd / "spatial.afinspection.zip") as archive:
        report = json.loads(archive.read("inspection.json"))
        assert archive.read("image.png").startswith(b"\x89PNG")
    view = report["view"]
    assert view["measurements"]["extents"] == [1, 1, 1]
    assert view["volume"]["boundary"] == 8
    assert view["placement"]["confirmed"]["hit"]
    assert view["neighborhood"]["members"] == [view["selected"]]


def commands():
    return [
        dict(id="mesh", **request("import", path="examples/primitives/cube.obj", units=1)),
        request("wait"),
        request("geometry.measure", target="$mesh.entity_id", plane=[0, 0, 1, 0]),
        request("geometry.volume", target="$mesh.entity_id", other="$mesh.entity_id"),
        placement(),
        request("wait"),
        export(),
    ]


def placement():
    return request(
        "geometry.placement",
        target="$mesh.entity_id",
        targets=["$mesh.entity_id"],
        position=[0, 0, 2],
        direction=[0, 0, -1],
    )


def export():
    return request(
        "inspection.export",
        path="spatial.afinspection.zip",
        selected="$mesh.entity_id",
        spatial=dict(
            measurements=True, volume=True, placement=True, neighborhood="$mesh.entity_id"
        ),
        wait=True,
    )
