"""Capture maintained addon loop projection/pairing in background Blender."""

import importlib
import json
import sys
from pathlib import Path

import bpy
import numpy as np


def surface(wavy):
    points = [
        [x / 6, y / 6, 0.12 * np.sin(x / 5) * np.cos(y / 5) if wavy else 0]
        for y in range(-18, 19)
        for x in range(-18, 19)
    ]
    faces = []
    for y in range(36):
        for x in range(36):
            a = y * 37 + x
            faces.extend(((a, a + 1, a + 38), (a, a + 38, a + 37)))
    return np.asarray(points), np.asarray(faces)


def ring(radius, offset=0, shortened=False):
    angles = np.linspace(0, 2 * np.pi, 48, endpoint=False)
    if shortened:
        angles = angles[:36]
    return np.column_stack(
        (radius * np.cos(angles) + offset, radius * np.sin(angles), np.full(len(angles), 0.7))
    )


def engine_inputs(modules, wavy, shortened):
    annuli, guides, _ = modules
    vertices, faces = surface(wavy)
    raw = [ring(1, shortened=shortened), ring(0.6), ring(1)[::-1], ring(0.2, 2)]
    source = [guides.Guide(str(i), str(i), True, values) for i, values in enumerate(raw)]
    bvh = guides.surface_bvh(vertices, faces)
    plane = annuli.SymmetryPlane(np.zeros(3), np.array([1, 0, 0]))
    return vertices, faces, raw, source, bvh, plane


def case(modules, wavy, shortened):
    annuli, _, solver = modules
    vertices, faces, raw, source, bvh, plane = engine_inputs(modules, wavy, shortened)
    loops = annuli.surface_loops(
        source,
        bvh,
        np.linalg.norm(np.ptp(vertices, axis=0)),
        annuli.surface_graph(vertices, faces),
        importlib.import_module("scipy.spatial").cKDTree(vertices),
        vertices,
        plane,
    )
    pairs, unpaired = solver._compatible_pairs(loops)
    return record(wavy, shortened, vertices, faces, raw, loops, pairs, unpaired)


def record(wavy, shortened, vertices, faces, raw, loops, pairs, unpaired):
    return dict(
        wavy=wavy,
        shortened=shortened,
        vertices=vertices.tolist(),
        faces=faces.tolist(),
        paths=[p.tolist() for p in raw],
        sources=[int(loop.name) for loop in loops],
        points=[loop.points.tolist() for loop in loops],
        normals=[loop.normals.tolist() for loop in loops],
        symmetric=[bool(loop.symmetric) for loop in loops],
        pairs=[[int(a.name), int(b.name)] for a, b in pairs],
        unpaired=[int(loop.name) for loop in unpaired],
    )


def main():
    args = sys.argv[sys.argv.index("--") + 1 :]
    sys.path.insert(0, args[0])
    importlib.import_module("adapters.draft_skin.vendor").ensure_worker_dependencies()
    modules = tuple(
        importlib.import_module("adapters.topology." + name)
        for name in ("engine.annuli", "engine.guides", "solver")
    )
    cases = [
        case(modules, wavy, short) for wavy, short in ((False, False), (True, False), (False, True))
    ]
    payload = dict(blender=bpy.app.version_string, cases=cases)
    Path(args[1]).write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    main()
