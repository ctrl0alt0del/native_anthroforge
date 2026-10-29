"""Persistent variant promotion and reference comparison in a relocated package."""

import json
from zipfile import ZipFile

from assembly_portable import request
from skeleton_update_portable import run


def reconstruction(executable, cwd, invoke):
    state = json.loads(invoke(executable, cwd, "--cli", "inspect", "assembly.anthroforge"))
    child = next(e["id"] for e in state["entities"] if e["parent"])
    run(executable, cwd, invoke, "reconstruction", commands(child))
    with ZipFile(cwd / "reconstruction.anthroforge") as archive:
        manifest = json.loads(archive.read("manifest.json"))
        metadata = manifest["document"]["reconstruction"]
        assert manifest["version"] == 9 and len(metadata["variants"]) == 3
        assert metadata["reviews"][0]["decision"] == "APPROVED"
    run(executable, cwd, invoke, "reconstruction-export", comparisons(child))
    with ZipFile(cwd / "reconstruction.afinspection.zip") as archive:
        report = json.loads(archive.read("inspection.json"))
        assert report["image"]["captured"] and not report["image"]["window_visible"]


def commands(target):
    return [
        request("open", path="assembly.anthroforge"),
        request("wait"),
        request("variant.create", "variant", subjects=[target], name="Alternative"),
        request("scp.rename", entity=target, name="Reviewed alternative"),
        request("variant.checkpoint", "checkpoint", name="Shape checkpoint"),
        request("variant.leave"),
        request("variant.review.prepare", "review", variant="$variant.id"),
        request("variant.review.status", wait=True),
        request("variant.review.apply", token="$review.token"),
        *metadata(target),
        request("save", path="reconstruction.anthroforge", blocked_policy="wait"),
    ]


def metadata(target):
    return [
        request("catalogue.type.create", "type", name="Bone"),
        request("catalogue.assign", target=target, type_id="$type", side="LEFT"),
        request("catalogue.region.set", target=target, name="Patch", triangles=[0]),
        request(
            "review.set",
            subject=target,
            dimension="ANATOMY",
            decision="APPROVED",
            reviewer="Portable qualification",
        ),
        request("reconstruction.queue.add", subject=target, type_id="$type"),
        request("reconstruction.queue.claim", owner="Qualification"),
    ]


def comparisons(target):
    return [
        request("open", path="reconstruction.anthroforge"),
        request("wait"),
        *reference(target),
        *export_comparison(target),
    ]


def reference(target):
    return [
        request(
            "reconstruction.stage.import_mesh",
            "stage",
            subject=target,
            stage="ORIGINAL",
            path="examples/primitives/cube.obj",
            units=1.0,
        ),
        request("wait"),
    ]


def export_comparison(target):
    return [
        request(
            "reconstruction.compare.start",
            subject=target,
            before=dict(stage="$stage.id"),
            after=dict(stage="final"),
        ),
        request("reconstruction.compare.status", wait=True),
        export_request(),
    ]


def export_request():
    return request(
        "reconstruction.compare.export",
        path="reconstruction.afinspection.zip",
        camera=[0, 0, 0, -18, 25, 8],
        wait=True,
    )
