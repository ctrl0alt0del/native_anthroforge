"""Replay frozen attachment inputs through the existing native kernel; never publish."""

import json
import sys
from dataclasses import replace
from pathlib import Path
from threading import Event

import numpy as np

from anthroforge.core.entities import SCP, Attachment
from anthroforge.native.attachments import propagate
from anthroforge.native.components import transformed
from anthroforge.native.mesh import GeometryEngine


def read(folder):
    data = json.loads((folder / "detail.json").read_text())
    with np.load(folder / "geometry.npz") as arrays:
        return data, {key: arrays[key] for key in arrays.files}


def binding(runtime):
    keys = (
        "parent_tri_vidx",
        "parent_tri_weights",
        "parent_flow_tri_vidx",
        "parent_flow_tri_weights",
        "parent_tangent_hint_local",
        "parent_offset_local",
        "child_origin_local",
        "child_tangent_local",
        "child_normal_local",
    )
    result = [v for key in keys for v in runtime["attach_" + key]]
    return tuple(result + [runtime["attach_child_anchor_index"]])


def blender_record(data, key):
    row = next(e for e in data["entities"] if e["id"] == key)
    objects = {o["name"]: o for o in data["objects"]}
    frame = objects[row["transform_object_ref"]]["world"]
    runtime = dict(row["runtime"])
    runtime["attach_parent_tangent_hint_local"] = parent_hint(data, row)
    return SCP(
        row["name"],
        id=key,
        parent=row["parent_id"],
        matrix=tuple(frame),
        attachment=blender_attachment(row, runtime),
    )


def blender_attachment(row, runtime):
    return Attachment(
        binding=binding(runtime),
        parent_mode=row["attach_parent_anchor_mode"],
        child_mode=row["attach_child_anchor_mode"],
        follow_rotation=row["attach_follow_rotation"],
        strategy=row["attach_tangent_strategy"],
    )


def parent_hint(data, row):
    parents = {e["id"]: e for e in data["entities"]}
    if row["parent_id"] not in parents:
        return row["runtime"]["attach_parent_tangent_hint_local"]
    parent = parents[row["parent_id"]]
    objects = {o["name"]: o for o in data["objects"]}
    owner = np.array(objects[parent["transform_object_ref"]]["world"]).reshape(4, 4)[:3, :3]
    geometry = np.array(objects[parent["geometry_object_ref"]]["world"]).reshape(4, 4)[:3, :3]
    owner, geometry = (
        owner / np.linalg.norm(owner, axis=0),
        geometry / np.linalg.norm(geometry, axis=0),
    )
    return owner.T @ geometry @ row["runtime"]["attach_parent_tangent_hint_local"]


def app_record(data, key):
    row = next(e for e in data["entities"] if e["id"] == key)
    settings = dict(row["attachment"])
    settings.update(binding=tuple(settings["binding"]), material_asset="")
    return SCP(
        row["name"],
        id=key,
        parent=row["parent"],
        matrix=tuple(row["matrix"]),
        geometry_offset=tuple(row["geometry_offset"]),
        attachment=Attachment(**settings),
    )


def parent_mesh(engine, arrays, parent):
    frame = np.array(parent.matrix).reshape(4, 4).copy()
    frame[:3, 3] += frame[:3, :3] @ np.array(parent.geometry_offset)
    local = transformed(engine, arrays[parent.id + "__vertices"], np.linalg.inv(frame).ravel())
    triangles = arrays[parent.id + "__triangles"]
    return engine.create_mesh(local, triangles.ravel(), np.arange(len(triangles) + 1) * 3)


def replay(engine, folder, key, variant):
    data, arrays = read(folder)
    record = blender_record if variant == "blender" else app_record
    child = record(data, key)
    parent = replace(record(data, child.parent), parent="", asset="parent")
    mesh = parent_mesh(engine, arrays, parent)
    output = propagate(engine, [parent, child], {"parent": mesh}, {key}, Event())[-1]
    delta = np.array(output.matrix).reshape(4, 4) - np.array(child.matrix).reshape(4, 4)
    return dict(
        status=output.status,
        error=output.error,
        matrix=list(output.matrix),
        position_delta=delta[:3, 3].tolist(),
        maximum_matrix_delta=float(abs(delta).max()),
    )


def run(folder):
    engine = GeometryEngine()
    result = {}
    for scenario, case, ids in (
        ("ribs", "SHORTCUT_4", ("SCP_7", "SCP_5", "SCP_6")),
        ("thumb", "SHORTCUT_21", ("SCP_17",)),
    ):
        for variant in ("blender", "app"):
            for state in ("baseline", case):
                for key in ids:
                    label = "/".join((scenario, variant, state, key))
                    result[label] = replay(
                        engine, folder / scenario / variant / state, key, variant
                    )
    (folder / "counterfactual.json").write_text(json.dumps(result, indent=2), encoding="utf-8")


if __name__ == "__main__":
    run(Path(sys.argv[1]))
