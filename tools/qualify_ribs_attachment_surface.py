"""Read-only seam/rim and confirmed-capture diagnosis on the paired shoulder fixture."""

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from shortcut_attachment_counterfactual import app_record, blender_record, read

from anthroforge.core.entities import IDENTITY, SCP, Attachment
from anthroforge.native import scene
from anthroforge.native.attachments import capture
from anthroforge.native.mesh import GeometryEngine


def mesh(engine, vertices, faces):
    return engine.create_mesh(vertices, faces.ravel(), np.arange(len(faces) + 1) * 3)


def point(vertices, binding):
    return np.asarray(binding[3:6]) @ vertices[np.asarray(binding[:3], dtype=int)]


def captured_binding(engine, target, position):
    frame = list(IDENTITY)
    frame[3], frame[7], frame[11] = position
    parent = SCP("Surface", id="parent", asset="mesh")
    child = SCP(
        "Probe",
        parent="parent",
        matrix=tuple(frame),
        attachment=Attachment(child_mode="OBJECT_ORIGIN"),
    )
    captured = capture(engine, child, parent, {"mesh": target})
    return captured.attachment.binding


def nearest(engine, target, position):
    return point(target.array(0), captured_binding(engine, target, position)).tolist()


def rim_mesh(engine, vertices, faces):
    split = len(vertices) // 2
    mixed = (faces < split).any(axis=1) & (faces >= split).any(axis=1)
    return mesh(engine, vertices, faces[mixed])


def raw_nearest(engine, target, position):
    from anthroforge.native import point_attachments

    _, bindings = point_attachments.capture(engine, [target.handle], [IDENTITY], [position])
    return point(target.array(0), bindings[0])


def classification(vertices, faces, binding):
    selected = set(int(i) for i in binding[:3])
    indices = [i for i, row in enumerate(faces) if set(row) == selected]
    split = len(vertices) // 2
    return dict(
        triangle=indices,
        vertices=list(binding[:3]),
        weights=list(binding[3:6]),
        layer="generated" if min(selected) >= split else "base" if max(selected) < split else "rim",
    )


def qualify(engine, folder, side):
    data, arrays = read(folder)
    child = (blender_record if side == "blender" else app_record)(data, "SCP_7")
    vertices, faces = arrays["SCP_2__vertices"], arrays["SCP_2__triangles"]
    geometry = mesh(engine, vertices, faces)
    anchor = point(vertices, child.attachment.binding)
    rim = raw_nearest(engine, rim_mesh(engine, vertices, faces), anchor)
    return dict(
        classification(vertices, faces, child.attachment.binding),
        **capture_observations(engine, geometry, child, anchor),
        rim_gap=float(np.linalg.norm(anchor - rim)),
        inputs=input_hashes(folder),
    )


def input_hashes(folder):
    return {name: digest(folder / name) for name in ("detail.json", "geometry.npz")}


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def capture_observations(engine, geometry, child, anchor):
    origin = np.asarray(child.matrix).reshape(4, 4)[:3, 3]
    fresh = captured_binding(engine, geometry, origin)
    confirmed = nearest(engine, geometry, anchor)
    return dict(
        stored_anchor=anchor.tolist(),
        confirmed_anchor=confirmed,
        fresh_from_hook=point(geometry.array(0), fresh).tolist(),
        fresh_reference=classification(geometry.array(0), geometry.array(3), fresh),
        confirmed_gap=float(np.linalg.norm(anchor - confirmed)),
        line_of_sight_gap=visibility_gap(engine, geometry, origin, anchor),
    )


def visibility_gap(engine, geometry, origin, anchor):
    handles = np.asarray([geometry.handle], dtype=np.uint64)
    hits = scene.pick(engine, handles, np.asarray([IDENTITY]), origin, anchor - origin)
    return float(np.linalg.norm(np.asarray(hits[0][5:8]) - anchor)) if hits else None


def run(root, output):
    engine = GeometryEngine()
    result = {side: qualify(engine, root / side / "baseline", side) for side in ("blender", "app")}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    run(Path(sys.argv[1]), Path(sys.argv[2]))
