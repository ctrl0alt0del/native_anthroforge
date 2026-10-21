"""Discriminate a fixed historical pin error from QP-backend behavior, in memory only."""

from dataclasses import replace

import numpy as np

from anthroforge.native import point_attachments, scene

from . import cases, harness
from .run import checked, save


def outer_point(engine, case, spec, owners, bindings):
    owner, binding = int(owners[0]), bindings[0]
    surface = case["surfaces"][owner]
    indices = binding[:3].astype(int)
    triangles = np.asarray(surface["triangles"]).reshape(-1, 3)
    face = int(np.flatnonzero(np.all(triangles == indices, axis=1))[0])
    closest = binding[3:6] @ np.asarray(surface["vertices"])[indices]
    return scene.surface_snap(engine, spec.handles[owner], spec.matrices[owner], face, closest)


def alternatives(engine, spec, case):
    output = []
    for backend in range(3):
        harness.configure(engine, backend)
        path, result = checked(engine, spec, case)
        output.append(dict(result, backend=backend))
    return output


def comparison(engine, case):
    meshes, spec = cases.inputs(engine, case)
    owners, bindings = point_attachments.capture(
        engine, spec.handles, spec.matrices, case["points"]
    )
    point = outer_point(engine, case, spec, owners, bindings)
    first = replace(spec.curve.points[0], position=tuple(point["point"]))
    corrected = replace(spec, curve=replace(spec.curve, points=(first, *spec.curve.points[1:])))
    return dict(
        owners=owners.tolist(),
        normal_offsets=bindings[:, 17].tolist(),
        snap=point,
        original=alternatives(engine, spec, case),
        diagnostic_copy=alternatives(engine, corrected, case),
    )


def main():
    engine = harness.engine()
    case = next(c for c in cases.skull_cases() if c["name"] == "skull-AF_FIBER_1")
    result = comparison(engine, case)
    save(cases.ROOT / "build/routing-piqp/skull-counterexample.json", result)
    print(
        [
            (row["qualified"], row["quality"]["collision_segments"])
            for row in result["diagnostic_copy"]
        ]
    )


if __name__ == "__main__":
    main()
