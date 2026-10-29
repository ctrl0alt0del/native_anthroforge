"""Relocated JSON authoring parity, immutable candidate scenes and literal text."""

import json
import zipfile

import numpy as np
from authoring_workflows_portable import execute, named
from construction_portable import request
from PIL import Image


def authoring_parity(executable, cwd, invoke):
    data = execute(executable, cwd, invoke, "authoring-parity", commands())
    assert data["root_state"]["entities"][0]["name"] == "$literal"
    assert data["editing"]["total"] == 9 and data["editing"]["next_offset"] == 2
    assert data["skin"]["authored_override"] is False
    assert sum(row["ready"] for row in data["surfaces"]["items"]) == 2
    assert data["geometry"]["total"] > 0 and len(data["geometry"]["values"]) <= 3
    verify_archive(cwd / "candidate.afinspection.zip", data["capture"])


def commands():
    return setup() + curve_queries() + mesh_capture()


def setup():
    literal = named("root", "scp.empty", name="$literal")
    literal["literal_paths"] = ["/name"]
    return [
        literal,
        named("root_state", "inspect"),
        named("bone", "import", path="examples/primitives/cube.obj", units=1, parent="$root"),
        request("wait"),
        request("mirror.configure", target="$root", enabled=True, shift=1),
        named("skin", "skin.contributor.inspect", owner="$bone.entity_id"),
        named("surfaces", "surface.options"),
    ]


def curve_queries():
    points = [dict(position=p) for p in ((0, 0, 0), (0, 1, 0), (1, 1, 0))]
    return [
        named("curve", "curve.create", points=points),
        request("wait"),
        named("editing", "editing.inspect", target="$curve", category="CURVE", limit=2),
        named("convert", "curve.conversion.preview", curve="$curve", engine="POLYLINE", samples=12),
        request("wait"),
        named(
            "path_capture", "inspection.capture", kind="curve_conversion", token="$convert.token"
        ),
        request("curve.conversion.cancel"),
        export_path(),
    ]


def mesh_capture():
    return [
        assess_mesh(),
        request("wait"),
        named("capture", "inspection.capture", kind="mesh_replacement", token="$review.token"),
        geometry_page(),
        request("scp.mesh.replace.cancel"),
        export_mesh(),
        request("inspection.release", snapshot="$capture.snapshot"),
    ]


def export_path():
    return request(
        "inspection.export",
        snapshot="$path_capture.snapshot",
        images=False,
        path="path.afinspection.zip",
        wait=True,
    )


def assess_mesh():
    return named(
        "review",
        "scp.mesh.replace.assess",
        target="$bone.entity_id",
        path="examples/primitives/cube.obj",
    )


def geometry_page():
    return named(
        "geometry",
        "inspection.geometry",
        snapshot="$capture.snapshot",
        layer="$capture.layers.0.id",
        buffer="positions",
        limit=3,
    )


def export_mesh():
    view = dict(mode="Split", camera=[1, 0, 0, -15, 30, 45, 8])
    return request(
        "inspection.export",
        snapshot="$capture.snapshot",
        path="candidate.afinspection.zip",
        wait=True,
        view=view,
    )


def verify_archive(path, capture):
    with zipfile.ZipFile(path) as archive:
        metadata = json.loads(archive.read("inspection.json"))
        evidence = json.loads(archive.read("image.png.json"))
        assert metadata["schema_version"] == 2 and metadata["snapshot"] == capture["snapshot"]
        assert evidence["captured"] and not evidence["window_visible"]
        assert evidence["scene"]["complete"] and not evidence["warnings"]
        assert any(row["subject"].startswith("mirror/") for row in metadata["layers"])
        with archive.open("image.png") as image:
            pixels = np.asarray(Image.open(image).convert("RGB"))
            assert np.unique(pixels.reshape(-1, 3), axis=0).shape[0] > 100
