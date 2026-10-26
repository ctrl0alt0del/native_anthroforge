"""Capture addon half-mesh and reflected-output behavior without a visible Blender UI."""

import importlib
import json
import sys
from pathlib import Path

import bpy
import numpy as np

CUTS = [
    ("axis", [0.2, 0, 0, 1, 0, 0]),
    ("oblique", [0.15, 0.05, 0.2, 0.7, 0.3, 0.2]),
    ("on-vertices", [-1, 0, 0, 1, 0, 0]),
]
MIRRORS = [
    ("capped", [0, 0, 0, 1, 0, 0]),
    ("snap", [0, 0, 0, 1, 0, 0]),
    ("shifted", [3, 4, 5, 1, 0, 0]),
    ("oblique-mirror", [0, 0, 0, 0.8, 0.6, 0]),
]


def cube():
    ring = [[-1, -1], [1, -1], [1, 1], [-1, 1]]
    p = np.array([[x, y, z] for z in (-1, 1) for x, y in ring], float)
    f = np.array(
        [[3, 2, 1, 0], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    )
    return p, f


def plane(module, values):
    return module.SymmetryPlane(
        np.array(values[:3]), np.array(values[3:]) / np.linalg.norm(values[3:])
    )


def half(module, name, equation):
    points, quads = cube()
    faces = np.stack((quads[:, [0, 1, 2]], quads[:, [0, 2, 3]]), axis=1).reshape(-1, 3)
    data = bpy.data.meshes.new(name)
    data.from_pydata(points, [], faces)
    obj = bpy.data.objects.new(name, data)
    module.bisect_left_half(obj, plane(module, equation))
    expected = dict(
        points=[list(v.co) for v in data.vertices], faces=[list(f.vertices) for f in data.polygons]
    )
    bpy.data.objects.remove(obj)
    bpy.data.meshes.remove(data)
    return record(name, "half", points, faces, equation, expected)


def record(name, operation, points, faces, equation, expected):
    return dict(
        name=name,
        operation=operation,
        vertices=points.tolist(),
        faces=faces.tolist(),
        plane=equation,
        expected=expected,
    )


def mirrored(module, name, equation):
    points, faces = cube()
    points[points[:, 0] > 0, 0] = 0.001 if name == "snap" else 0
    if name == "snap":
        faces = np.delete(faces, 3, axis=0)
    if name == "shifted":
        points += equation[:3]
    if name == "oblique-mirror":
        points = points @ np.array([[0.8, -0.6, 0], [0.6, 0.8, 0], [0, 0, 1]]).T
    out = module.mirrored_output(points.copy(), faces, (), plane(module, equation))
    expected = dict(points=out[0].tolist(), faces=out[1].tolist())
    return record(name, "mirror", points, faces, equation, expected)


def main():
    args = sys.argv[sys.argv.index("--") + 1 :]
    sys.path.insert(0, args[0])
    importlib.import_module("adapters.draft_skin.vendor").ensure_worker_dependencies()
    module = importlib.import_module("adapters.topology.engine.instant")
    rows = [half(module, *row) for row in CUTS] + [mirrored(module, *row) for row in MIRRORS]
    Path(args[1]).write_text(
        json.dumps(dict(blender=bpy.app.version_string, cases=rows), separators=(",", ":")),
        encoding="utf-8",
    )
    print([(r["name"], len(r["expected"]["faces"])) for r in rows])


if __name__ == "__main__":
    main()
