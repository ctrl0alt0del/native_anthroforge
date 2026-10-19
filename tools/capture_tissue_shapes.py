"""Pin production addon shell/sweep outputs for native port qualification."""

import hashlib
import importlib
import json
import sys
from dataclasses import asdict
from pathlib import Path

import numpy as np


def grid():
    points = [(i * 0.1, j * 0.1, 0.02 * np.sin(i * j)) for i in range(5) for j in range(7)]
    faces = [
        (i * 7 + j, (i + 1) * 7 + j, (i + 1) * 7 + j + 1, i * 7 + j + 1)
        for i in range(4)
        for j in range(6)
    ]
    return points, faces


def shell(custom, reverse=False):
    source = importlib.import_module("core.vcp.source_surface_normals")
    fields = importlib.import_module("core.vcp.soft_tissue_surface_field")
    module = importlib.import_module("core.vcp.soft_tissue_surface_inflation")
    points, faces = grid()
    faces = [tuple(reversed(f)) if reverse else tuple(f) for f in faces]
    edges = edges_of(faces)
    weights = shell_weights(fields, points, edges, faces, custom)
    profile = module.SurfaceLayerProfile(0.12, 0.006, 0.8)
    inputs = (points, source.normals(points, faces), faces, fields.boundary_edges(edges, faces))
    result = module.inflate_surface_layer(*inputs, weights, profile)
    return shell_record(points, faces, custom, profile, result)


def edges_of(faces):
    return list({tuple(sorted((f[i], f[(i + 1) % len(f)]))) for f in faces for i in range(len(f))})


def shell_weights(fields, points, edges, faces, custom):
    if custom is not None:
        return custom
    return fields.boundary_falloff_weights(len(points), edges, faces, points)


def shell_record(points, faces, custom, profile, result):
    return dict(
        kind="NORMAL",
        points=points,
        faces=faces,
        custom=custom,
        settings=asdict(profile),
        output=asdict(result),
    )


def sweep(closed=False, taper=0.16):
    module = importlib.import_module("core.vcp.soft_tissue_curve_inflation")
    phase = np.linspace(0, 2 * np.pi if closed else np.pi, 9, endpoint=not closed)
    points = [(0.2 * np.cos(t), 0.2 * np.sin(t), 0.03 * np.sin(2 * t)) for t in phase]
    normals = [(0, 0, 1)] * len(points)
    profile = module.CurveRidgeProfile(0.08, 0.12, 0.65, 9, taper, closed)
    result = module.inflate_curve_ridge(points, normals, profile)
    return dict(
        kind="PROFILE",
        points=points,
        normals=normals,
        settings=asdict(profile),
        output=asdict(result),
    )


def sources(addon):
    names = (
        "soft_tissue_surface_field",
        "source_surface_normals",
        "soft_tissue_surface_inflation",
        "soft_tissue_curve_inflation",
    )
    return {
        f"core/vcp/{name}.py": hashlib.sha256(
            (addon / f"core/vcp/{name}.py").read_bytes()
        ).hexdigest()
        for name in names
    }


def main(addon, output):
    sys.path.insert(0, str(addon))
    cases = [
        shell(None),
        shell([0.0] * 35),
        shell([0.5] * 35, True),
        sweep(),
        sweep(True),
        sweep(taper=0),
    ]
    output.write_text(json.dumps(dict(sources=sources(addon), cases=cases), allow_nan=False) + "\n")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
