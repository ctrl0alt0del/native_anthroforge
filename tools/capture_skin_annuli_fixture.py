"""Capture addon candidate selection and annulus symmetry in background Blender."""

import importlib
import json
import sys
from pathlib import Path

import bpy
import numpy as np


def setup():
    args = sys.argv[sys.argv.index("--") + 1 :]
    sys.path.insert(0, args[0])
    importlib.import_module("adapters.draft_skin.vendor").ensure_worker_dependencies()
    annuli = importlib.import_module("adapters.topology.engine.annuli")
    return args, annuli


def loops(annuli, row):
    return [
        annuli.SurfaceLoop(
            str(i),
            np.array(p),
            np.array(n),
            annuli.loop_perimeter(np.array(p)),
            np.mean(p, axis=0),
            bool(s),
        )
        for i, (p, n, s) in enumerate(
            zip(row["points"], row["normals"], row["symmetric"], strict=True)
        )
    ]


def altered(annuli, source, mode):
    a, b = source[:2]
    if mode == "planar":
        indices = (np.arange(192) * 5) % 192
        b = reordered(annuli, b, indices)
    if mode == "radial":
        b = annuli.SurfaceLoop(b.name, a.points, a.normals, a.perimeter, a.center, a.symmetric)
    return [a, b]


def reordered(annuli, loop, indices):
    return annuli.SurfaceLoop(
        loop.name,
        loop.points[indices],
        loop.normals[indices],
        annuli.loop_perimeter(loop.points[indices]),
        loop.center,
        loop.symmetric,
    )


def patch_record(annuli, patch, bvh):
    return dict(
        points=patch.rings.tolist(),
        normals=patch.normals.tolist(),
        faces=patch.faces.tolist(),
        sources=[int(name) for name in patch.source_names],
        inversions=annuli.patch_inversions(patch, bvh),
    )


def case(annuli, row, kind):
    source = altered(annuli, loops(annuli, row), kind)
    bvh = annuli.guide_test.surface_bvh(np.array(row["vertices"]), np.array(row["faces"]))
    diagonal = np.linalg.norm(np.ptp(row["vertices"], axis=0))
    plane = annuli.SymmetryPlane(np.zeros(3), np.array([1, 0, 0]))
    pair = tuple(source)
    direct = annuli.build_patch(pair, bvh, diagonal, 5, 0)
    planar = annuli.build_planar_pair_patch(pair, bvh, diagonal, 5, 0, plane)
    radial = annuli.build_radial_patch(pair[0], bvh, diagonal, 5, 0)
    chosen = annuli.build_patch_options(pair, bvh, diagonal, 5, 0, plane)
    out = source_record(row, kind, source)
    out["candidates"] = [annuli.patch_inversions(patch, bvh) for patch in (direct, planar, radial)]
    out["chosen"] = patch_record(annuli, chosen, bvh)
    return out


def source_record(row, kind, source):
    return dict(
        kind=kind,
        vertices=row["vertices"],
        faces=row["faces"],
        loops=[
            dict(points=x.points.tolist(), normals=x.normals.tolist(), symmetric=x.symmetric)
            for x in source
        ],
    )


def main():
    args, annuli = setup()
    records = json.loads(Path(args[1]).read_text(encoding="utf-8"))["cases"]
    cases = [
        case(annuli, row, kind) for row in records[:2] for kind in ("direct", "planar", "radial")
    ]
    out = dict(
        blender=bpy.app.version_string, source="adapters/topology/engine/annuli.py", cases=cases
    )
    Path(args[2]).write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print([(c["kind"], c["candidates"], c["chosen"]["inversions"]) for c in cases])


if __name__ == "__main__":
    main()
