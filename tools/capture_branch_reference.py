"""Pin actual addon branched-surface vertices and seam connectivity without Blender."""

import hashlib
import importlib
import json
import sys
from pathlib import Path

import numpy as np
from capture_surface_reference import package


def paths(boundary, curved):
    main = [
        np.array(
            [[0, y, 0], [0.2, y, 0.1 if curved else 0], [0.7, y, 0.15 if curved else 0], [1, y, 0]]
        )
        for y in (0, 0.4)
    ]
    roots = main[boundary][[1, 2]]
    sign = -1 if boundary == 0 else 1
    children = [np.array([p, p + [0, sign * 0.3, 0.2], p + [0.1, sign * 0.7, 0.1]]) for p in roots]
    return main, children


def case(module, boundary, flip, curved):
    main, children = paths(boundary, curved)
    branch = module.BranchInput("branch", boundary, (1, 2), tuple(children))
    assembly = module.prepare_assembly(main, (branch,), flip)
    vertices, faces = module.assemble(assembly)
    return dict(
        name=f"boundary{boundary}_flip{flip}_curved{curved}",
        rows=[r.tolist() for r in (*main, *children)],
        boundary=0 if boundary == 0 else 1,
        roots=[1, 2],
        main=2,
        flip=flip,
        vertices=vertices.tolist(),
        faces=faces.tolist(),
    )


def capture(root, output):
    package(root)
    module = importlib.import_module("af_surface_reference.branched_surface")
    digest = hashlib.sha256((root / "core/vcp/branched_surface.py").read_bytes()).hexdigest()
    cases = [
        case(module, boundary, flip, curved)
        for boundary in (0, -1)
        for flip in (False, True)
        for curved in (False, True)
    ]
    output.write_text(
        json.dumps(dict(source=str(root), sha256=digest, cases=cases), indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    capture(Path(sys.argv[1]), Path("tests/fixtures/surfaces/branches.json"))
